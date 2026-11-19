"""
Cached multilingual dense sentence embeddings loader for IPM v2 study.
Retrieves and aligns 384-dimensional dense semantic representations for each dataset.
"""
import pickle
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EMB_DIR = ROOT / "research_project" / "results" / "processed" / "embeddings"

def get_embeddings(ds, df):
    fname = ds.lower().replace("-", "_") + "_embeddings.pkl"
    path = EMB_DIR / fname
    with open(path, "rb") as f:
        emb = pickle.load(f)
        
    if ds == "HateXplain":
        orig_df = pd.read_csv(ROOT / "research_project" / "results" / "processed" / "hatexplain_cleaned.csv")
        out = {}
        for sp in ["train", "val", "test"]:
            sub_orig = orig_df[orig_df.split == sp].reset_index(drop=True)
            id_to_idx = {str(row["id"]): i for i, row in sub_orig.iterrows()}
            sub_df = df[df.split == sp].reset_index(drop=True)
            idxs = [id_to_idx[str(row["id"])] for _, row in sub_df.iterrows()]
            out[sp] = emb["X_" + sp][idxs]
        return out["train"], out["val"], out["test"]
    else:
        return emb["X_train"], emb["X_val"], emb["X_test"]
