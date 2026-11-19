# Cover Letter for Submission to Information Processing & Management

**To:**  
The Editor-in-Chief  
*Information Processing & Management* (Elsevier)

**Date:** November 19, 2026  
**Subject:** Submission of Critical Application Manuscript

Dear Editor-in-Chief,

We are pleased to submit our original research manuscript entitled:

> **"How Many Humans Does a Decision Need? Legitimacy-Aware Jury Allocation and Conformal Overrule Guarantees for Content Moderation"**

authored by **Shixiang Yu** and **Muhammad Khubaib Ahmad** (Corresponding Author), for publication in *Information Processing & Management* as a **Critical Application Manuscript** in the domain of **Social Computing and Intelligent Information Systems**.

### Context and Core Scientific Contribution
Content moderation across online social platforms is a mission-critical socio-technical information process. Due to severe legal and ethical liabilities, complete automation is tenable only on clear-cut cases; platforms rely on selective classification (learning to abstain) to route ambiguous inputs to human reviewers. 

However, existing selective prediction frameworks presuppose a binary decision: either automate ($k=0$) or defer to a single human reviewer ($k=1$). In subjective language—such as hate speech, misogyny, and offensive rhetoric—human annotators themselves systematically disagree along demographic, cultural, and political lines. Deferring a contested post to a single reviewer merely reduces moderation to an arbitrary coin toss governed by that reviewer's personal background, while convening a full jury for every post is economically impossible.

In this paper, we resolve this foundational dilemma by asking: **How many humans does a decision actually need?**

We make four primary contributions at the intersection of computing and information science:
1. **Legitimacy-Aware Jury Allocation (LAJ):** We derive a closed-form Condorcet-style Bayesian formulation of panel value $f_k(p)$ on the annotator probability simplex. LAJ dynamically allocates the cost-optimal panel size $k^*(x) \in \{0, 1, \dots, M-1\}$ based on second-order epistemic uncertainty and predicted panel consensus value.
2. **Non-Circular Held-out Annotator Agreement (HAA):** Unlike prior work that evaluates models against the same majority vote used for training, we introduce a rigorous combinatorial evaluation protocol: a panel of size $k$ is evaluated strictly against independent annotators who were *not* on the panel.
3. **Distribution-Free Conformal Risk Control (MO-CRC):** We provide finite-sample mathematical guarantees bounding the **Autonomous Overrule Rate (AOR)**—the fraction of human judgments overridden without human review—under distribution-free exchangeability ($\mathbb{E}[\text{AOR}] \le \alpha$).
4. **Demographic Disparity Audit:** Using real multi-annotator demographic profiles (**HS-Brexit** with target Muslim immigrant vs control raters, and **ArMIS** with female vs male raters), we demonstrate that standard confidence thresholding systematically overrules marginalized minority annotators at a significantly higher rate than control annotators. LAJ restores demographic overrule parity.

### Manuscript Details
- **Manuscript Type:** Critical Application Manuscript
- **Target Journal:** *Information Processing & Management* (Elsevier)
- **Primary Area:** Social Computing and Decision Support Systems
- **Word Count:** ~9,200 words
- **Reproducibility:** Complete executable code repository, benchmark schemas, and high-resolution vector figures are provided.

### Declarations
- This manuscript represents original work that has not been published previously and is not under consideration for publication elsewhere.
- All authors have reviewed and approved the manuscript.
- The authors declare no competing financial or personal interests.

### Suggested Reviewers
1. **Prof. Valerio Basile**, University of Turin, Italy (`valerio.basile@unito.it`) — Leading pioneer in Perspectivist NLP and multi-annotator benchmarks.
2. **Prof. Federico Cabitza**, University of Milano-Bicocca, Italy (`federico.cabitza@unimib.it`) — Expert on perspectivist machine learning and human-in-the-loop decision systems.
3. **Dr. Aida Mostafazadeh Davani**, Google Research, USA (`adavani@google.com`) — Author of foundational multi-annotator modeling architectures (TACL 2022).
4. **Prof. Anastasios Angelopoulos**, UC Berkeley, USA (`angelopoulos@berkeley.edu`) — Leading authority on Conformal Risk Control and distribution-free prediction guarantees.

Thank you very much for your time and editorial consideration.

Sincerely,

**Muhammad Khubaib Ahmad**  
Department of Artificial Intelligence, Emerson University Multan, Multan, Pakistan  
INFERENCE Lab, Multan, Pakistan  
Email: `khubaib.ahmad@inference-lab.org`  
*(Corresponding Author on behalf of all co-authors)*
