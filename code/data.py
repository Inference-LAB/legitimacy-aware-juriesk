"""
Data layer for the IPM v2 study.

Builds every dataset directly from the official public sources so that splits, vote vectors
and annotator metadata are verifiable:
  * HateXplain  - punyajoy/HateXplain (official post_id_divisions: 15,383 / 1,922 / 1,924)
  * MD-Agreement, HS-Brexit, ArMIS - official LeWiDi-2023 release (Le-Wi-Di/le-wi-di.github.io)

Annotator metadata kept (it was discarded by the earlier pipeline):
  * HS-Brexit : per-vote group ('target' = Muslim immigrants in the UK, 'control'), from other_info
  * ArMIS     : per-vote annotator profile (Moderate_Female, Liberal_Female, Conservative_Male)
  * MD-Agreement : domain (BLM, Covid-19, Election2020)
"""
import json
import os
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

HX_DATA = "https://raw.githubusercontent.com/punyajoy/HateXplain/master/Data/dataset.json"
HX_DIV = "https://raw.githubusercontent.com/punyajoy/HateXplain/master/Data/post_id_divisions.json"
LW = "https://raw.githubusercontent.com/Le-Wi-Di/le-wi-di.github.io/main/LeWiDi_2-2023/{ds}_dataset/{ds}_{sp}.json"

DATASETS = ["HateXplain", "MD-Agreement", "HS-Brexit", "ArMIS"]
HX_LABELS = ["normal", "offensive", "hatespeech"]


def _fetch(url, name):
    dest = RAW / name
    if not dest.exists():
        print("  downloading", url)
        urllib.request.urlretrieve(url, dest)
    with open(dest, encoding="utf-8") as f:
        return json.load(f)


def load_hatexplain():
    d = _fetch(HX_DATA, "hatexplain_dataset.json")
    div = _fetch(HX_DIV, "hatexplain_divisions.json")
    lab = {l: i for i, l in enumerate(HX_LABELS)}
    rows = []
    for sp in ["train", "val", "test"]:
        for pid in div[sp]:
            rec = d[pid]
            votes = [lab[a["label"]] for a in rec["annotators"]]
            rows.append(dict(id=pid, split=sp, text=" ".join(rec["post_tokens"]), votes=votes,
                             groups=["crowd"] * len(votes), domain="all"))
    return pd.DataFrame(rows), 3


def load_lewidi(ds):
    rows = []
    for sp, name in [("train", "train"), ("dev", "val"), ("test", "test")]:
        d = _fetch(LW.format(ds=ds, sp=sp), f"{ds}_{sp}.json")
        for pid, rec in d.items():
            votes = [int(x) for x in str(rec["annotations"]).split(",")]
            info = rec.get("other_info", {}) or {}
            anns = str(rec.get("annotators", "")).split(",")
            if ds == "HS-Brexit":
                gmap = {"group1": info.get("group1", "target group").split()[0],
                        "group2": info.get("group2", "control group").split()[0]}
                groups = [gmap[g.strip()] for g in info["annotators group"].split(",")]
            elif ds == "ArMIS":
                groups = [info.get(a.strip(), a.strip()) for a in anns]
            else:
                groups = ["crowd"] * len(votes)
            domain = info.get("domain", "all") if isinstance(info, dict) else "all"
            rows.append(dict(id=f"{ds}_{pid}", split=name, text=rec["text"], votes=votes,
                             groups=groups, domain=domain))
    return pd.DataFrame(rows), 2


def load(ds):
    df, K = load_hatexplain() if ds == "HateXplain" else load_lewidi(ds)
    V = np.array(df["votes"].tolist())                       # (n, M) - every dataset has a fixed M
    P = np.stack([(V == k).mean(1) for k in range(K)], 1)    # empirical annotator distribution p_h
    df["M"] = V.shape[1]
    df["K"] = K
    df["p_max"] = P.max(1)
    df["contested"] = (P.max(1) < 1.0).astype(int)
    df["plurality"] = P.argmax(1)                            # ties -> lowest index (documented)
    with np.errstate(divide="ignore", invalid="ignore"):
        H = -(np.where(P > 0, P * np.log(P), 0.0)).sum(1) / np.log(K)
    df["h_norm"] = H
    return df.reset_index(drop=True), V, P, K


if __name__ == "__main__":
    for ds in DATASETS:
        df, V, P, K = load(ds)
        sizes = df.split.value_counts().reindex(["train", "val", "test"]).to_dict()
        print(f"{ds:13s} M={V.shape[1]} K={K} {sizes} contested={df.contested.mean():.3f} "
              f"groups={sorted(set(sum(df.groups.tolist(), [])))} domains={sorted(df.domain.unique())}")
