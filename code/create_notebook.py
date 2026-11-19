import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_NB = ROOT / "IPM_v2_Replication_Notebook.ipynb"

nb = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# How Many Humans Does a Decision Need?\n",
                "## Legitimacy-Aware Jury Allocation and Conformal Overrule Guarantees for Content Moderation\n",
                "**Target Journal:** *Information Processing & Management* (Elsevier, IF: 8.6, Q1 SCIE/SSCI)  \n",
                "**Manuscript Track:** Critical Application Manuscript (System Design Research in Social Computing)  \n",
                "**Authors:** Shixiang Yu$^1$, Muhammad Khubaib Ahmad$^{2,3,*}$  \n",
                "*$^1$School of Computing, National University of Singapore; $^2$Department of Computer Science, Emerson University Multan; $^3$INFERENCE Lab*  \n",
                "\n",
                "---\n",
                "### Quick Start Instructions for Google Colab / VS Code:\n",
                "1. **GPU Runtime:** Connect to a GPU runtime (`Runtime -> Change runtime type -> T4 / A100 GPU`).\n",
                "2. **One-Click Replication:** Select `Runtime -> Run all`. All four multi-annotator datasets (**HateXplain**, **MD-Agreement**, **HS-Brexit**, **ArMIS**) are automatically streamed directly from official GitHub research repositories.\n",
                "3. **Outputs:** All empirical tables (Tables 1-6) and 300 DPI figures (Figures 1-2) are generated and saved to `outputs_v2/`.\n"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# CELL 1: Environment Setup, Dependencies & Hardware Verification\n",
                "import sys, os, subprocess\n",
                "print('Python version:', sys.version)\n",
                "\n",
                "required_packages = ['torch', 'transformers', 'sentence-transformers', 'scikit-learn', 'scipy', 'matplotlib', 'seaborn', 'pandas', 'numpy', 'tabulate']\n",
                "for pkg in required_packages:\n",
                "    try:\n",
                "        __import__(pkg.replace('-', '_'))\n",
                "    except ImportError:\n",
                "        print(f'Installing {pkg}...')\n",
                "        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', pkg])\n",
                "\n",
                "import torch, numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns\n",
                "device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')\n",
                "print(f'\\n[HARDWARE]: Running on: {device}')\n",
                "if torch.cuda.is_available():\n",
                "    print(f'  GPU Device: {torch.cuda.get_device_name(0)}')\n",
                "    print(f'  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB')\n",
                "\n",
                "os.makedirs('outputs_v2/figures', exist_ok=True)\n",
                "os.makedirs('outputs_v2/tables', exist_ok=True)\n",
                "os.makedirs('data/raw', exist_ok=True)\n",
                "print('Output directories initialized.')\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Automated Dataset Streaming from Official Repositories\n",
                "Downloads raw JSON datasets from official GitHub repositories, retaining individual annotator identities, demographic groups, and original divisions."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# CELL 2: Data Ingestion & Harmonization\n",
                "import urllib.request, json\n",
                "from collections import Counter\n",
                "\n",
                "URLS = {\n",
                "    'hatexplain_data': 'https://raw.githubusercontent.com/punyajoy/HateXplain/master/Data/dataset.json',\n",
                "    'hatexplain_div': 'https://raw.githubusercontent.com/punyajoy/HateXplain/master/Data/post_id_divisions.json',\n",
                "    'md_train': 'https://raw.githubusercontent.com/Le-Wi-Di/le-wi-di.github.io/master/MD-Agreement/MDA_train.json',\n",
                "    'md_dev': 'https://raw.githubusercontent.com/Le-Wi-Di/le-wi-di.github.io/master/MD-Agreement/MDA_dev.json',\n",
                "    'md_test': 'https://raw.githubusercontent.com/Le-Wi-Di/le-wi-di.github.io/master/MD-Agreement/MDA_test.json',\n",
                "    'brexit_train': 'https://raw.githubusercontent.com/Le-Wi-Di/le-wi-di.github.io/master/HS-Brexit/HS-Brexit_train.json',\n",
                "    'brexit_dev': 'https://raw.githubusercontent.com/Le-Wi-Di/le-wi-di.github.io/master/HS-Brexit/HS-Brexit_dev.json',\n",
                "    'brexit_test': 'https://raw.githubusercontent.com/Le-Wi-Di/le-wi-di.github.io/master/HS-Brexit/HS-Brexit_test.json',\n",
                "    'armis_train': 'https://raw.githubusercontent.com/Le-Wi-Di/le-wi-di.github.io/master/ArMIS/ArMIS_train.json',\n",
                "    'armis_dev': 'https://raw.githubusercontent.com/Le-Wi-Di/le-wi-di.github.io/master/ArMIS/ArMIS_dev.json',\n",
                "    'armis_test': 'https://raw.githubusercontent.com/Le-Wi-Di/le-wi-di.github.io/master/ArMIS/ArMIS_test.json',\n",
                "}\n",
                "\n",
                "def fetch(url, dest):\n",
                "    if not os.path.exists(dest):\n",
                "        print(f'Fetching {os.path.basename(dest)}...')\n",
                "        urllib.request.urlretrieve(url, dest)\n",
                "\n",
                "for k, u in URLS.items():\n",
                "    fname = u.split('/')[-1]\n",
                "    if 'hatexplain' in k:\n",
                "        fname = 'hatexplain_' + fname\n",
                "    fetch(u, os.path.join('data/raw', fname))\n",
                "print('All benchmark datasets cached successfully.')\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Core Formulations: Panel Value $f_k(p)$ and Held-out Agreement (HAA)\n",
                "Implements the exact Condorcet multi-class simplex panel value and the non-circular HAA metric."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# CELL 3: Mathematical Formulations\n",
                "import itertools\n",
                "from math import lgamma\n",
                "\n",
                "def compositions(k, K):\n",
                "    if K == 1:\n",
                "        yield (k,)\n",
                "        return\n",
                "    for i in range(k + 1):\n",
                "        for rest in compositions(k - i, K - 1):\n",
                "            yield (i,) + rest\n",
                "\n",
                "def plurality_decision(counts):\n",
                "    c = np.asarray(counts, float)\n",
                "    tie = (c == c.max()).astype(float)\n",
                "    return tie / tie.sum()\n",
                "\n",
                "def panel_value(P, k):\n",
                "    P = np.clip(np.asarray(P, float), 0.0, 1.0)\n",
                "    n, K = P.shape\n",
                "    out = np.zeros(n)\n",
                "    for c in compositions(k, K):\n",
                "        logm = lgamma(k + 1) - sum(lgamma(ci + 1) for ci in c)\n",
                "        prob = np.exp(logm) * np.prod(P ** np.asarray(c), axis=1)\n",
                "        out += prob * (P @ plurality_decision(c))\n",
                "    return out\n",
                "\n",
                "def empirical_panel_haa(V, K, k, G=None, group=None):\n",
                "    n, M = V.shape\n",
                "    num, den = np.zeros(n), np.zeros(n)\n",
                "    for S in itertools.combinations(range(M), k):\n",
                "        H = [j for j in range(M) if j not in S]\n",
                "        counts = np.stack([(V[:, S] == y).sum(1) for y in range(K)], 1).astype(float)\n",
                "        tie = (counts == counts.max(1, keepdims=True)).astype(float)\n",
                "        d = tie / tie.sum(1, keepdims=True)\n",
                "        if G is None:\n",
                "            agree = np.stack([(V[:, H] == y).mean(1) for y in range(K)], 1)\n",
                "            num += (d * agree).sum(1)\n",
                "            den += 1.0\n",
                "        else:\n",
                "            m = (G[:, H] == group).astype(float)\n",
                "            cnt = m.sum(1)\n",
                "            ok = cnt > 0\n",
                "            agree = np.stack([((V[:, H] == y) * m).sum(1) / np.maximum(cnt, 1) for y in range(K)], 1)\n",
                "            num += np.where(ok, (d * agree).sum(1), 0.0)\n",
                "            den += ok\n",
                "    return np.where(den > 0, num / np.maximum(den, 1), np.nan)\n",
                "\n",
                "def machine_haa(V, yhat, G=None, group=None):\n",
                "    agree = (V == yhat[:, None]).astype(float)\n",
                "    if G is None:\n",
                "        return agree.mean(1)\n",
                "    m = (G == group).astype(float)\n",
                "    return (agree * m).sum(1) / np.maximum(m.sum(1), 1)\n",
                "print('Mathematical formulations compiled.')\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Second-Order Bootstrap Modeling & Conformal Autonomy Gates\n",
                "Trains the second-order perspectivist ensemble and applies Conformal Risk Control."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# CELL 4: Study Runner Execution\n",
                "print('Starting study execution across all 4 multi-annotator benchmarks...')\n",
                "# Executes the master study runner\n",
                "import run_ipm_v2_study\n",
                "run_ipm_v2_study.run_study()\n",
                "print('\\n[SUCCESS]: Replication complete! All outputs generated in outputs_v2/')\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Inspection of Generated Publication Figures & Tables\n",
                "Displays the Pareto frontiers (Figure 1), sociodemographic overrule disparity audit (Figure 2), and verified empirical result tables."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# CELL 5: Display Figures & Print Formatted Tables\n",
                "from IPython.display import Image, display\n",
                "\n",
                "print('=== FIGURE 1: PARETO FRONTIERS ACROSS ALL FOUR BENCHMARKS ===')\n",
                "display(Image('outputs_v2/figures/fig1_pareto_frontiers_four_benchmarks.png'))\n",
                "\n",
                "print('=== FIGURE 2: SOCIOMODERATION OVERRULE DISPARITY MITIGATION ===')\n",
                "display(Image('outputs_v2/figures/fig2_demographic_disparity_mitigation.png'))\n",
                "\n",
                "print('\\n=== TABLE 1: HELD-OUT ANNOTATOR AGREEMENT (HAA) ===')\n",
                "print(pd.read_csv('outputs_v2/tables/table1_heldout_annotator_agreement.csv').to_markdown(index=False))\n",
                "\n",
                "print('\\n=== TABLE 4: STATISTICAL SIGNIFICANCE (PAIRED BOOTSTRAP) ===')\n",
                "print(pd.read_csv('outputs_v2/tables/table4_statistical_significance_bootstrap.csv').to_markdown(index=False))\n",
                "\n",
                "print('\\n=== TABLE 6: CONFORMAL RISK CONTROL (AUTONOMOUS OVERRULE RATE) ===')\n",
                "print(pd.read_csv('outputs_v2/tables/table6_conformal_risk_certification.csv').to_markdown(index=False))\n"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

with open(OUT_NB, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)
print(f"Created {OUT_NB}")
