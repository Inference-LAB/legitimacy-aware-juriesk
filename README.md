# How Many Humans Does a Decision Need? Legitimacy-Aware Jury Allocation and Conformal Overrule Guarantees for Content Moderation

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Target: IPM Elsevier](https://img.shields.io/badge/Target-Information%20Processing%20%26%20Management-brightgreen.svg)](https://www.sciencedirect.com/journal/information-processing-and-management)

This repository provides the official implementation, replication pipelines, and evaluation benchmarks for the research manuscript:

> **"How Many Humans Does a Decision Need? Legitimacy-Aware Jury Allocation and Conformal Overrule Guarantees for Content Moderation"**  
> **Authors:** Shixiang Yu$^1$, Muhammad Khubaib Ahmad$^{2,3,*}$  
> *$^1$School of Computing, National University of Singapore; $^2$Department of Computer Science, Emerson University Multan; $^3$INFERENCE Lab*  
> **Track:** *Critical Application Manuscript* (System Design Research in Social Computing)  
> **Target Venue:** *Information Processing & Management* (Elsevier, Impact Factor: **8.6**, Q1 SCIE/SSCI, CAS Tier 1)  
> **Correspondence:** `khubaib@eum.edu.pk`

---

## 📌 Problem Formulation and Method Overview

Modern content moderation systems face a fundamental socio-technical crisis: scalable artificial intelligence classifiers must regulate online speech, yet toxic language and hate speech are inherently subjective and culturally situated. Conventional human-in-the-loop and learning-to-defer frameworks operate under a flawed binary assumption: routing each post either entirely to machine autonomy or to a single human reviewer, while treating inter-annotator disagreement as label noise. Consequently, autonomous systems disproportionately overrule vulnerable demographic minorities, while single-human review fails to resolve contentious interpretations.

```
+----------------------------------------------------------------------------------------------------+
|                                 LEGITIMACY-AWARE JURY ALLOCATION (LAJ)                             |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|      [ Incoming Post x ]                                                                           |
|               │                                                                                    |
|               ▼                                                                                    |
|  ┌─────────────────────────┐                                                                       |
|  │ Second-Order Bootstrap  │ ──► Epistemic Model Uncertainty Var[p]                                |
|  │   Soft-Label Ensemble   │ ──► Aleatoric Human Disagreement H(p)                                 |
|  └────────────┬────────────┘                                                                       |
|               │                                                                                    |
|               ▼                                                                                    |
|  ┌─────────────────────────┐     k*(x) = argmax [ V_k(x) - μ · k ]                                 |
|  │ Condorcet Simplex Panel │ ──────────────────────────────────────────┐                           |
|  │   Value Engine f_k(p)   │                                           │                           |
|  └─────────────────────────┘                                           ▼                           |
|                                                     ┌────────────────────────────────────┐         |
|                                                     │ Adaptive Sizing Routing Decision   │         |
|                                                     │      k*(x) ∈ {0, 1, ..., M-1}      │         |
|                                                     └──────────────────┬─────────────────┘         |
|                                                                        │                           |
|                    ┌───────────────────────────────────────────────────┴─────────────┐             |
|                    ▼                                                                 ▼             |
|         [ Case 1: k*(x) = 0 ]                                             [ Case 2: k*(x) ≥ 1 ]     |
|         AUTONOMOUS MACHINE ACTION                                         DELIBERATIVE HUMAN JURY  |
|                    │                                                                 │             |
|                    ▼                                                                 ▼             |
|      ┌───────────────────────────┐                                       ┌───────────────────────┐ |
|      │ Distribution-Free CRC     │                                       │ Plurality Jury Panel  │ |
|      │ Certified Safety Gate     │                                       │ with Held-Out Audit   │ |
|      │   E[ Overrule ] ≤ α       │                                       │   Size k* Annotators  │ |
|      └───────────────────────────┘                                       └───────────────────────┘ |
+----------------------------------------------------------------------------------------------------+
```

### Core Methodological Contributions

1. **Condorcet Simplex Panel Value ($f_k(p)$):**  
   We extend the classical Condorcet Jury Theorem to the multi-class probability simplex $\Delta^{K-1}$, deriving the exact closed-form expected agreement between a $k$-person plurality jury and an independent annotator:

$$f_k(p) = \sum_{c \in \mathcal{C}(k, K)} \left( rac{k!}{\prod_{y=0}^{K-1} c_y!} \prod_{y=0}^{K-1} p_y^{c_y} ight) \left( \sum_{y=0}^{K-1} d_y(c) \, p_y ight)$$

2. **Second-Order Perspectivist Modeling:**  
   A bootstrap ensemble of $B = 8$ soft-label estimators captures posterior probability vectors $p^{(b)}(x)$, disentangling epistemic classifier uncertainty from aleatoric societal contestation.

3. **Dynamic Budget-Constrained Panel Sizing ($k^*(x)$):**  
   Resolves *"How many humans does a decision need?"* by allocating variable panel sizes $k^*(x) \in \{0, 1, \dots, M-1\}$ via shadow labor pricing $\mu$, guaranteeing exact Pareto optimality between operational expenditure and community legitimacy:

$$k^*(x; \mu) = rg\max_{k \in \{0, 1, \dots, M-1\}} \left[ V_k(x) - \mu \cdot k ight]$$

4. **Distribution-Free Conformal Safety Certification:**  
   For autonomous executions ($k = 0$), Conformal Risk Control (CRC) guarantees that the Autonomous Overrule Rate (AOR) is bounded below a user-specified safety threshold $lpha$ with finite-sample validity under exchangeability:

$$\mathbb{E}\left[ \ell_{	ext{overrule}}(X) \cdot \mathbf{1}(V_0(X) \ge \hat{	au}_lpha) ight] \le lpha$$

5. **Non-Circular Held-out Annotator Agreement (HAA):**  
   Evaluates panel decisions strictly against independent held-out annotators who were not part of the adjudicating panel, completely avoiding circular majority-voting evaluation bias.

---

## 📂 Repository Organization

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

## 🚀 Quick Start and Installation

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/Inference-LAB/legitimacy-aware-juriesk.git
cd legitimacy-aware-juriesk

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Complete Experimental Suite
```bash
python code/run_ipm_v2_study.py
```
*Datasets are automatically downloaded and parsed directly from official research repositories on the first execution.*

### 3. Interactive Replication in Google Colab
Open [`IPM_v2_Replication_Notebook.ipynb`](IPM_v2_Replication_Notebook.ipynb) in Google Colab with GPU acceleration enabled (`Runtime -> Change runtime type -> T4 / A100 GPU`). Run all cells to reproduce all 6 empirical tables and 2 publication figures in one click.

---

## 📊 Benchmark Datasets

| Benchmark | Domain & Task | Classes ($K$) | Annotators ($M$) | Train / Val / Test Splits | Disagreement Characterization |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **HateXplain** | Hate & Offensive Speech | 3 | 3 | 15,383 / 1,922 / 1,924 | Multi-target annotations across Twitter and Gab |
| **MD-Agreement** | Online Toxicity | 2 | 5 | 6,592 / 1,104 / 3,057 | High-variance multi-annotator crowdsourced tweets |
| **HS-Brexit** | Hate Speech against Immigrants | 2 | 6 | 784 / 168 / 168 | 3 Targeted Muslim Immigrants vs. 3 Control Locals |
| **ArMIS** | Arabic Misogyny & Sexism | 2 | 3 | 657 / 141 / 145 | Annotators with distinct gender and political profiles |

---

## 🔬 Key Empirical Findings

### 1. The Multi-Person Deliberation Dividend (Table 1)
* On **MD-Agreement** ($M = 5$), expanding panel size from a single reviewer ($k = 1$) to a three-person jury ($k = 3$) increases held-out annotator agreement from 0.7131 to **0.7445** (+3.14% absolute gain).
* On contested items, single-human agreement drops to chance levels (0.333 on HateXplain and ArMIS), proving that lone reviewers cannot legitimately arbitrate contested content without jury deliberation.

### 2. Pareto Dominance across Operational Budgets (Tables 2 & 3)
* Standard Maximum Softmax Probability (MSP) plateaus once uncertain items receive a single reviewer (budget $pprox 0.6$). MSP cannot deploy multi-human juries even when review budget is available.
* At budget $\le 1.0$ reviews/post, LAJ achieves uniform Pareto dominance across all four benchmarks.
* Paired bootstrap hypothesis tests ($B = 2,000$ resamples) confirm that legitimacy gains are statistically significant ($p < 0.05$ under Holm-Bonferroni correction).

### 3. Sociodemographic Equity and Minority Protection (Table 5 & Figure 2)
* On **HS-Brexit**, conventional MSP autonomously overrules targeted Muslim immigrant annotators on 4.56% of posts. LAJ slashes this overrule rate to **1.19%** under matched budget (**73.9% relative reduction**).
* On **ArMIS**, LAJ cuts the autonomous overrule rate of female annotators from 15.17% to **8.28%**.

### 4. Certified Autonomous Safety (Table 6)
* Conformal Risk Control mathematically bounds the Autonomous Overrule Rate below target thresholds ($lpha \in \{0.05, 0.10, 0.15, 0.20\}$) while preserving operational throughput (safely resolving 52.7% of MD-Agreement and 89.9% of HS-Brexit autonomously at $lpha = 0.10$).

---

## 📄 Citation

```bibtex
@article{yu2026howmanyhumans,
  title={How Many Humans Does a Decision Need? Legitimacy-Aware Jury Allocation and Conformal Overrule Guarantees for Content Moderation},
  author={Yu, Shixiang and Ahmad, Muhammad Khubaib},
  journal={Information Processing & Management},
  year={2026},
  publisher={Elsevier},
  note={Under Review}
}
```

---

## 📜 License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
