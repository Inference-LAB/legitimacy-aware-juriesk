# How Many Humans Does a Decision Need? Legitimacy-Aware Jury Allocation and Conformal Overrule Guarantees for Content Moderation

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Target: IPM Elsevier](https://img.shields.io/badge/Target-Information%20Processing%20%26%20Management-brightgreen.svg)](https://www.sciencedirect.com/journal/information-processing-and-management)

This repository contains the official implementation, replication notebooks, and experimental evaluation for the manuscript:

> **"How Many Humans Does a Decision Need? Legitimacy-Aware Jury Allocation and Conformal Overrule Guarantees for Content Moderation"**  
> **Authors:** Shixiang Yu$^1$, Muhammad Khubaib Ahmad$^{2,3,*}$  
> *School of Computing, National University of Singapore; Emerson University Multan; INFERENCE Lab*  
> **Track:** *Critical Application Manuscript* (System Design Research in Social Computing)  
> **Target Venue:** *Information Processing & Management* (Elsevier, Impact Factor: **8.6**, Q1 SCIE/SSCI)

---

## 📌 Overview

Modern content moderation systems face a fundamental socio-technical crisis: scalable AI classifiers must regulate online speech, yet toxic language and hate speech are inherently subjective and culturally situated. Conventional "learning-to-defer" paradigms operate under a flawed binary assumption: routing each post either entirely to machine autonomy or to a single human reviewer, while treating inter-annotator disagreement as label noise. Consequently, autonomous systems disproportionately overrule vulnerable demographic minorities, while single-human review fails to resolve contested interpretations.

To solve this, we propose **Legitimacy-Aware Jury Allocation (LAJ)**:
1. **Condorcet Simplex Panel Value ($f_k(p)$):** Closed-form generalization of the Condorcet Jury Theorem over the multi-class probability simplex $\Delta^{K-1}$, quantifying the exact expected agreement between a $k$-person human jury and the broader annotator community.
2. **Second-Order Perspectivist Modeling:** Uses a bootstrap soft-label ensemble to decouple epistemic model uncertainty from aleatoric societal contestation.
3. **Dynamic Panel Sizing ($k^*(x)$):** Resolves *"How many humans does a decision need?"* by dynamically allocating variable panel sizes $k \in \{0, 1, \dots, M-1\}$ based on marginal legitimacy gain per review cost $\mu$.
4. **Distribution-Free Conformal Safety Certification:** Uses Conformal Risk Control (CRC) to mathematically guarantee that the Autonomous Overrule Rate satisfies $\mathbb{E}[\text{AOR}] \le \alpha$ with finite-sample validity under exchangeability.
5. **Non-Circular Held-out Annotator Agreement (HAA):** Scores panel decisions strictly against independent held-out annotators not serving on the panel across 4 multi-annotator corpora (**HateXplain**, **MD-Agreement**, **HS-Brexit**, and **ArMIS**).

---

## 📂 Repository Structure

```
.
├── code/
│   ├── core.py                      # Mathematical engine: f_k(p), HAA, LAJ policy, Conformal Risk Control
│   ├── data.py                      # Automatic dataset downloader and parser
│   ├── embeddings.py                # Dense multilingual MiniLM representation extractor
│   ├── run_ipm_v2_study.py          # Master experimental suite runner
│   ├── convert_to_word.py           # Native Word & OMML math compiler
│   └── audit_references.py          # Reference verification & citation integrity auditor
├── outputs_v2/
│   ├── figures/
│   │   ├── fig1_pareto_frontiers_four_benchmarks.png  # 300 DPI Publication Figure 1 (Pareto Frontiers)
│   │   └── fig2_demographic_disparity_mitigation.png  # 300 DPI Publication Figure 2 (Minority Overrule Audit)
│   └── tables/
│       ├── table1_heldout_annotator_agreement.csv     # Exact Held-out Annotator Agreement (HAA)
│       ├── table2_aupf_frontier_summary.csv           # Area Under Pareto Frontier (AUPF)
│       ├── table3_matched_budget_legitimacy.csv       # Pointwise Matched-Budget Comparisons
│       ├── table4_statistical_significance_bootstrap.csv # Paired Bootstrap Significance (Holm-corrected)
│       ├── table5_demographic_disparity_audit.csv     # HS-Brexit & ArMIS Sociodemographic Audit
│       └── table6_conformal_risk_certification.csv    # Distribution-Free Conformal Guarantees
├── IPM_v2_Replication_Notebook.ipynb# 1-Click Interactive Google Colab / VS Code GPU Notebook
├── IPM_Manuscript.docx              # Complete Word Manuscript (~9,500 words, native OMML math, tables, figures)
├── IPM_Manuscript.md                # Markdown manuscript source with verified DOIs
├── IPM_Title_Page.docx              # Formal Elsevier Title Page (Word)
├── IPM_Cover_Letter.docx            # Cover Letter to EiC Prof. Jiming Liu (Word)
├── IPM_Highlights.md                # 5 Highlights (strictly <= 85 characters each)
├── requirements.txt                 # Project dependencies
└── README.md
```

---

## 🚀 Quick Start & Installation

### 1. Local Environment Setup
```bash
# Clone the repository
git clone https://github.com/Khubaib-Ahmad/legitimacy-aware-juries.git
cd legitimacy-aware-juries

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Full Experimental Suite
```bash
python code/run_ipm_v2_study.py
```
*Datasets are automatically streamed and parsed directly from official research repositories on the first run.*

### 3. Interactive Replication in Google Colab
Open [`IPM_v2_Replication_Notebook.ipynb`](IPM_v2_Replication_Notebook.ipynb) in Google Colab with GPU acceleration enabled (`Runtime -> Change runtime type -> T4 / A100 GPU`). Run all cells to reproduce all 6 empirical tables and 2 publication figures in one click.

---

## 📊 Benchmark Datasets Analyzed

| Benchmark | Domain & Task | Classes ($K$) | Annotators ($M$) | Samples (Train / Val / Test) | Disagreement Characterization |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **HateXplain** | Hate & Offensive Speech | 3 | 3 | 15,383 / 1,922 / 1,924 | Multi-target annotations across Twitter and Gab |
| **MD-Agreement** | Online Toxicity | 2 | 5 | 6,592 / 1,104 / 3,057 | High-variance multi-annotator crowdsourced tweets |
| **HS-Brexit** | Hate Speech against Immigrants | 2 | 6 | 784 / 168 / 168 | 3 Targeted Muslim Immigrants vs. 3 Control Locals |
| **ArMIS** | Arabic Misogyny & Sexism | 2 | 3 | 657 / 141 / 145 | Annotators with distinct gender and political profiles |

---

## 🔬 Key Empirical Findings

1. **The Multi-Person Deliberation Dividend:** On MD-Agreement ($M=5$), increasing panel size from $k=1$ (single reviewer) to $k=3$ (three-person jury) increases held-out agreement from 0.7131 to **0.7445** (+3.14% absolute gain).
2. **Pareto Dominance:** LAJ systematically out-deliberates conventional Maximum Softmax Probability (MSP), disagreement-entropy routing, and fixed 3-tier heuristics, achieving statistically significant improvements ($p < 0.05$ under Holm-Bonferroni correction).
3. **Sociodemographic Disparity Mitigation:** Under matched review budgets, LAJ reduces the autonomous overrule rate of targeted minorities (Muslim immigrants on HS-Brexit and female annotators on ArMIS) by **42.8% to 73.9%**.
4. **Distribution-Free Safety Guarantees:** Conformal Risk Control mathematically bounds the Autonomous Overrule Rate below user-specified safety thresholds ($\mathbb{E}[\text{AOR}] \le \alpha$) with high operational throughput.

---

## 📄 Citation

```bibtex
@article{yu2026howmanyhumans,
  title={How Many Humans Does a Decision Need? Legitimacy-Aware Jury Allocation and Conformal Overrule Guarantees for Content Moderation},
  author={Yu, Shixiang and Ahmad, Muhammad Khubaib},
  journal={Information Processing \& Management},
  volume={--},
  pages={--},
  year={2026},
  publisher={Elsevier},
  note={Under Review}
}
```

---

## 📜 License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
