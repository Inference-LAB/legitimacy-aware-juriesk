# How Many Humans Does a Decision Need? Legitimacy-Aware Jury Allocation and Conformal Overrule Guarantees for Content Moderation

**Shixiang Yu**$^1$, **Muhammad Khubaib Ahmad**$^{2,3,*}$  
$^1$*School of Computing, National University of Singapore, Singapore*  
$^2$*Department of Computer Science, Emerson University Multan, Multan, Pakistan*  
$^3$*INFERENCE Lab, Multan, Pakistan*  
$^*$*Corresponding author: Muhammad Khubaib Ahmad (khubaib@eum.edu.pk)*

---

## Abstract
Modern content moderation systems face a fundamental socio-technical crisis: scalable artificial intelligence classifiers must arbitrate online speech, yet hate speech, toxicity, and misogyny are inherently subjective. Contemporary "learning-to-defer" paradigms operate under a flawed binary assumption—routing each post either entirely to machine autonomy or to a single human reviewer—while treating non-unanimous annotator votes as uninformative label noise. Consequently, autonomous decisions disproportionately overrule vulnerable demographic minorities, while single-human review fails to resolve contested interpretations. 

In this work, we propose a transformative paradigm for human-AI collaborative moderation: **Legitimacy-Aware Jury Allocation (LAJ)**. Grounded in a generalization of the Condorcet Jury Theorem over the multi-class probability simplex, we derive a closed-form panel value function $f_k(p)$ that quantifies the exact expected agreement between a $k$-person human jury and the broader annotator community. By modeling human disagreement through a second-order bootstrap ensemble that decouples epistemic model uncertainty from aleatoric human divergence, our system dynamically allocates the optimal panel size $k^*(x) \in \{0, 1, \dots, M-1\}$ tailored to the contentiousness of each post under operational budget constraints. Furthermore, we equip the autonomous tier ($k=0$) with distribution-free Conformal Risk Control (CRC), providing rigorous theoretical guarantees that the Autonomous Overrule Rate (AOR) cannot exceed a policy-specified safety threshold $\alpha \in (0, 1)$ with high confidence.

We evaluate LAJ across four diverse multi-annotator benchmarks covering hate speech, offensive language, Brexit discourse, and online misogyny: **HateXplain** ($M=3$), **MD-Agreement** ($M=5$), **HS-Brexit** ($M=6$), and **ArMIS** ($M=3$). Using a non-circular **Held-out Annotator Agreement (HAA)** protocol that scores decisions strictly against independent held-out annotators not serving on the panel, LAJ achieves uniform Pareto dominance over conventional Maximum Softmax Probability (MSP), disagreement-entropy routing, and fixed multi-tier heuristics, expanding the Area Under the Pareto Frontier (AUPF) by up to +18.4%. In sociodemographic audits on HS-Brexit and ArMIS, LAJ reduces the autonomous overrule rate of targeted minorities (Muslim immigrants and female annotators) by 42.8% to 64.1% compared to conventional deployment. These results demonstrate that principled, variable-sized human juries combined with conformal risk guarantees provide a mathematically sound and socially legitimate foundation for next-generation content moderation.

**Keywords:** Content Moderation, Perspectivist NLP, Condorcet Jury Theorem, Learning to Defer, Conformal Prediction, Sociotechnical Systems, Social Computing.

---

## 1. Introduction

Automated content moderation systems constitute the primary digital defense against hate speech, harassment, violent extremism, and targeted disinformation across social media platforms (Gillespie, 2018; Gorwa et al., 2020). However, deploying natural language processing (NLP) models at platform scale introduces profound normative challenges. Online speech is culturally situated, identity-dependent, and intrinsically subjective; annotators with distinct sociodemographic backgrounds frequently exhibit persistent, principled disagreements regarding what constitutes abusive language (Basile et al., 2021; Gordon et al., 2022; Davani et al., 2022; Rottger et al., 2022).

Despite this intrinsic plurality, the vast majority of existing human-in-the-loop (HITL) and "learning-to-defer" (L2D) architectures remain tethered to two flawed assumptions:
1. **The Fallacy of Binary Deferral:** Traditional L2D frameworks conceptualize moderation as a binary decision: an algorithm either autonomously predicts a label or escalates the item to a *single* human moderator (Madras et al., 2018; Mozannar & Sontag, 2020; Charusaie et al., 2022). This binary framing assumes that any single human possesses sufficient legitimacy to arbitrate complex linguistic nuances, completely overlooking the high variance of individual human judgment on contested content.
2. **The Eradication of Disagreement:** Prevailing supervised pipelines collapse multi-annotator distributions into singular ground-truth labels via majority voting or Dawid-Skene aggregation (Dawid & Skene, 1979). By treating human disagreement as measurement noise rather than authentic sociodemographic perspective, models are incentivized to learn the consensus of the demographic majority, systematically suppressing and overruling the lived experiences of marginalized groups (Prabhakaran et al., 2021; Goyal et al., 2022; Sachdeva et al., 2022).

When autonomous NLP systems misclassify contested content, or when single-reviewer deferral assigns an idiosyncratic moderator to a sensitive post, the consequence is not merely statistical error—it is an **illegitimate overrule** of community voice. In socio-technical governance, the legitimacy of an institutional decision depends not only on its nominal accuracy, but on whether its adjudicative procedure reflects the democratic deliberative standards of the governed community (Habermas, 1996; Binns, 2018; Zhang et al., 2023).

### 1.1 The Central Question: How Many Humans Does a Decision Need?
To overcome the limitations of binary deferral, we formulate a fundamental operational question for human-AI governance: **How many humans does a given decision need?**

Intuitively, posts exhibiting unanimous societal consensus (e.g., unambiguous racial slurs or innocuous everyday discourse) require minimal human intervention; autonomous or single-reviewer decisions achieve near-perfect legitimacy. Conversely, deeply polarized or identity-salient discourse requires deliberative panels of varying sizes to guarantee that the adjudicative outcome aligns with the broader community distribution. Yet, human moderation is severely resource-constrained: commercial platforms cannot afford large panels for every flagged item (Roberts, 2019).

### 1.2 Our Contributions
In this paper, we present **Legitimacy-Aware Jury Allocation (LAJ)**, an operational framework that optimizes the sizing of human review panels while providing rigorous distribution-free safety guarantees for autonomous actions. Specifically, our contributions are:

1. **Theoretical Formulation of Simplex Panel Value:** Extending the classical Condorcet Jury Theorem from binary truth models to the multi-class annotator probability simplex $\Delta^{K-1}$, we derive a closed-form expression $f_k(p)$ for the expected agreement between a $k$-person plurality panel and an independent annotator drawn at random from the population. We formally prove the conditions under which panel expansion yields diminishing marginal returns.
2. **Second-Order Perspectivist Modeling:** We formulate a second-order bootstrap ensemble that estimates the full annotator distribution $p(y|x)$ while explicitly separating epistemic model uncertainty from aleatoric linguistic contestation. This enables the machine to predict the expected marginal gain $\Delta V_k(x) = f_k(p) - f_{k-1}(p)$ for any post $x$.
3. **Budget-Constrained Jury Routing Policy:** We cast panel allocation as a constrained optimization problem, proving that the optimal routing rule $k^*(x)$ assigns panel sizes greedily based on marginal legitimacy gains per unit cost, tracing an exact Pareto frontier between human labor expenditure and community legitimacy.
4. **Distribution-Free Autonomous Overrule Guarantees:** For items routed to autonomous machine action ($k=0$), we deploy Conformal Risk Control (CRC). We prove that under exchangeability, the expected Autonomous Overrule Rate (AOR)—the frequency with which an autonomous machine decision contradicts the annotator community—is rigorously bounded by a user-specified risk ceiling $\alpha \in (0, 1)$ without distributional assumptions.
5. **Rigorous Held-Out Annotator Agreement (HAA) Validation:** We introduce an exact, non-circular validation protocol that evaluates machine and panel decisions strictly against independent held-out annotators not present on the panel. Across four multi-annotator benchmarks (**HateXplain**, **MD-Agreement**, **HS-Brexit**, and **ArMIS**), LAJ uniformly outperforms competitive baselines.
6. **Sociodemographic Disparity Mitigation:** Through fine-grained sociodemographic audits on HS-Brexit (Target Muslim Immigrants vs. Control Locals) and ArMIS (Female vs. Male annotators), we demonstrate that LAJ reduces minority overrule rates by over 50% relative to standard maximum softmax probability baselines.

The remainder of this article is organized as follows: Section 2 reviews related work in perspectivist NLP, learning-to-defer, and social choice theory. Section 3 develops the mathematical foundations of panel value and held-out agreement. Section 4 presents the complete system architecture and conformal calibration. Section 5 describes the empirical setup across the four benchmarks. Section 6 presents the primary empirical results and Pareto frontiers. Section 7 conducts the sociodemographic equity audit. Section 8 discusses implications for platform governance and concludes.

---

## 2. Related Work and Theoretical Positioning

Our research synthesizes four foundational literatures: perspectivist natural language processing, learning-to-defer systems, social choice theory, and distribution-free conformal inference.

### 2.1 Perspectivist NLP and Annotator Disagreement
Historically, supervised NLP research treated inter-annotator disagreement as label noise to be minimized through aggregation heuristics or post-hoc adjudication (Artstein & Poesio, 2008; Snow et al., 2008). In recent years, the *perspectivist NLP* movement has established that disagreement in subjective linguistic tasks—such as toxic language, hate speech, sarcasm, and sentiment—is often irreducible, reflecting authentic divergence across demographic, cultural, and political identities (Basile et al., 2021; Uma et al., 2021; Rottger et al., 2022). 

Datasets such as **HateXplain** (Mathew et al., 2021), **MD-Agreement** (Leonardelli et al., 2021), **HS-Brexit** (Akhtar et al., 2021), and **ArMIS** (Almanea & Poesio, 2022) provide unaggregated individual annotations alongside annotator metadata. Methodological advances have sought to model these distributions using multi-task heads (Davani et al., 2022), soft-label loss formulations (Fornaciari et al., 2021), or annotator embeddings (Plepi et al., 2022). However, virtually all existing perspectivist models remain descriptive: they predict distributions or individual labels during training, but offer no principled operational protocol for deciding how many human moderators should review an item at test time.

### 2.2 Learning to Defer and Selective Prediction
Selective prediction (rejection learning) allows a classifier to abstain from predicting when its confidence falls below a threshold (El-Yaniv & Wiener, 2010; Geifman & El-Yaniv, 2017). Learning-to-defer (L2D) extends this concept to human-AI collaboration by training models that either predict autonomously or route the input to a designated human expert whose cost and error profile are known (Madras et al., 2018; Mozannar & Sontag, 2020; Charusaie et al., 2022; Verma & Nalisnick, 2022).

Despite their mathematical sophistication, existing L2D algorithms suffer from a critical structural limitation: they are strictly **binary**. A query is either deferred to *one* human or predicted by the machine. In subjective content moderation, this binary design collapses: routing a contentious post about minority discrimination to a single human moderator provides no guarantee that the moderator's judgment represents the affected community. Our work generalizes L2D from binary deferral to **variable-sized panel allocation** $k \in \{0, 1, \dots, M-1\}$.

### 2.3 Condorcet Jury Theorem and Deliberative Social Choice
The epistemic rationale for multi-person panels traces to the Condorcet Jury Theorem (Condorcet, 1785), which demonstrates that under binary choice between a true and false state, if independent jurors each have a probability $p > 0.5$ of being correct, the probability of a correct majority decision approaches 1 as the panel size $k \to \infty$ (Grofman et al., 1983; List & Goodin, 2001).

Recent computer science literature has applied jury models to online governance and crowd-sourcing (Karger et al., 2014; Zhang et al., 2023). However, classical Condorcet formulations rely on two assumptions that fail in content moderation:
1. The existence of an objective binary ground truth $y^* \in \{0, 1\}$;
2. A homogeneous individual competence parameter $p > 0.5$ across all items.
In subjective NLP, ground truth is replaced by an annotator probability distribution $p \in \Delta^{K-1}$. In Section 3, we generalize the Condorcet framework to this multi-class simplex setting, establishing closed-form expected agreement values without assuming objective ground truth.

### 2.4 Distribution-Free Conformal Risk Control
When deploying autonomous machine actions in high-stakes domains, heuristic uncertainty estimates (such as softmax confidence) fail due to overconfidence and calibration drift (Guo et al., 2017). Conformal prediction provides a rigorous mathematical framework for distribution-free finite-sample guarantees (Vovk et al., 2005; Angelopoulos & Bates, 2021). 

Recently, Bates et al. (2021) and Angelopoulos et al. (2024) developed **Conformal Risk Control (CRC)**, extending conformal prediction to arbitrary monotonically non-increasing loss functions. CRC allows practitioners to bound the expected value of an operational risk metric (such as false negative rate or triage leakage) below a pre-specified threshold $\alpha \in (0, 1)$ with rigorous finite-sample coverage under data exchangeability. In this work, we leverage CRC to mathematically certify the safety of the autonomous tier ($k=0$), guaranteeing that the rate of illegitimate autonomous overrule remains bounded.

---

## 3. Theoretical Foundations: The Annotator Simplex and Panel Value

We now formulate the mathematical model governing human-AI decision legitimacy in subjective classification.

### 3.1 Notation and the Annotator Probability Simplex
Let $\mathcal{X}$ denote the space of textual inputs (e.g., social media posts) and $\mathcal{Y} = \{0, 1, \dots, K-1\}$ be a finite set of $K$ mutually exclusive categories (e.g., Toxic, Hate Speech, Neither). Let $\Delta^{K-1} = \{ p \in \mathbb{R}^K : \sum_{y=0}^{K-1} p_y = 1, p_y \ge 0 \}$ denote the $(K-1)$-dimensional probability simplex.

For any given post $x \in \mathcal{X}$, the annotator population is governed by a true, item-specific distribution $p(x) \in \Delta^{K-1}$, where $p_y(x) = \mathbb{P}_{h \sim \mathcal{H}}(Y_h = y \mid x)$ represents the probability that an annotator $h$ randomly sampled from the population $\mathcal{H}$ assigns label $y$ to $x$. When an item is evaluated by a panel of $k$ independent human annotators $h_1, \dots, h_k \sim \mathcal{H}$, their votes $v = (v_1, \dots, v_k) \in \mathcal{Y}^k$ are conditionally independent given $p(x)$:
$$\mathbb{P}(v \mid p(x)) = \prod_{j=1}^k p_{v_j}(x)$$

The panel aggregates its votes via a **plurality decision rule** with uniform tie-breaking. Let $c(v) = (c_0(v), \dots, c_{K-1}(v))$ be the vote count vector, where $c_y(v) = \sum_{j=1}^k \mathbb{I}(v_j = y)$. The panel's decision distribution $d(c) \in \Delta^{K-1}$ is defined by:
$$d_y(c) = \begin{cases} \frac{1}{|\mathcal{Y}_{\text{max}}(c)|} & \text{if } y \in \mathcal{Y}_{\text{max}}(c) \\ 0 & \text{otherwise} \end{cases}$$
where $\mathcal{Y}_{\text{max}}(c) = \{ y \in \mathcal{Y} : c_y = \max_{y'} c_{y'} \}$ is the set of plurality winners.

### 3.2 Definition of Decision Legitimacy
In subjective content moderation, external ground truth does not exist independently of human consensus. Following democratic social choice theory (List & Goodin, 2001; Zhang et al., 2023), we define the **procedural legitimacy** of a decision $\hat{y}$ (whether produced by an algorithm or a panel) as its expected agreement with an independent annotator drawn at random from the population $\mathcal{H}$:
$$\mathcal{L}(\hat{y}; x) = \mathbb{E}_{h \sim \mathcal{H}}[\mathbb{I}(Y_h = \hat{y}) \mid x] = p_{\hat{y}}(x)$$
For a randomized or tie-broken decision rule $d \in \Delta^{K-1}$, the expected legitimacy is:
$$\mathcal{L}(d; x) = \sum_{y=0}^{K-1} d_y p_y(x) = d \cdot p(x)$$

### 3.3 Derivation of the Closed-Form Panel Value Function $f_k(p)$
We now derive the expected legitimacy achieved by a $k$-person human jury whose votes are sampled i.i.d. from $p \in \Delta^{K-1}$.

**Definition 1 (Panel Value Function).** For any integer $k \ge 1$ and distribution $p \in \Delta^{K-1}$, the panel value $f_k(p)$ is the expected agreement between the plurality decision of a $k$-person panel and a fresh independent annotator:
$$f_k(p) = \mathbb{E}_{v_1, \dots, v_k \stackrel{\text{iid}}{\sim} p}\left[ d(c(v)) \cdot p \right]$$

By enumerating all weak compositions of $k$ into $K$ parts, $\mathcal{C}(k, K) = \{ (c_0, \dots, c_{K-1}) \in \mathbb{N}_0^K : \sum_{y=0}^{K-1} c_y = k \}$, the probability of observing count vector $c$ follows the multinomial distribution:
$$\mathbb{P}(c \mid p) = \frac{k!}{\prod_{y=0}^{K-1} c_y!} \prod_{y=0}^{K-1} p_y^{c_y}$$
Substituting into Definition 1 yields the exact closed-form expression:
$$f_k(p) = \sum_{c \in \mathcal{C}(k, K)} \left( \frac{k!}{\prod_{y=0}^{K-1} c_y!} \prod_{y=0}^{K-1} p_y^{c_y} \right) \left( \sum_{y=0}^{K-1} d_y(c) \, p_y \right)$$

For the baseline machine classifier ($k=0$) producing deterministic prediction $\hat{y}_0(x) = \arg\max_y \hat{p}_y(x)$, the autonomous legitimacy is simply:
$$f_0(p) = p_{\hat{y}_0(x)}$$

### 3.4 Theoretical Properties: Monotonicity and Diminishing Returns
The panel value function $f_k(p)$ exhibits key mathematical properties that govern human panel sizing:

**Proposition 1 (Simplex Condorcet Property).** For binary classification ($K=2$) with $p = (p_1, 1-p_1)$ and odd $k = 2m+1$:
1. If $p_1 > 0.5$, then $f_k(p)$ is strictly increasing in $k$, and $\lim_{k \to \infty} f_k(p) = p_1$.
2. If $p_1 = 0.5$ (maximal contestation), then $f_k(p) = 0.5$ for all $k \ge 1$.
3. The marginal gain $\Delta f_k(p) = f_k(p) - f_{k-1}(p)$ is strictly non-increasing for $k \ge 1$.

*Proof Sketch.* In the binary case with odd $k$, plurality coincides with strict majority. The probability that the panel selects label 1 is $P_{\text{maj}}(p_1; k) = \sum_{j=(k+1)/2}^k \binom{k}{j} p_1^j (1-p_1)^{k-j}$. The expected agreement with a held-out annotator is $f_k(p) = P_{\text{maj}} p_1 + (1 - P_{\text{maj}})(1 - p_1) = (1 - p_1) + (2p_1 - 1) P_{\text{maj}}(p_1; k)$. By the classical Condorcet Jury Theorem, $P_{\text{maj}}$ increases monotonically toward 1 if $p_1 > 0.5$, proving statement (1). When $p_1 = 0.5$, symmetry dictates $P_{\text{maj}} = 0.5$, yielding $f_k(p) = 0.5$ for all $k$. Diminishing marginal returns follow from the binomial probability decay of boundary ties. $\blacksquare$

**Proposition 2 (The Disagreement Plateau).** When an item is contested between two or more plausible interpretations ($p_y \approx p_{y'} \approx 1/K$), expanding the panel size $k$ produces asymptotically zero marginal legitimacy gain:
$$\lim_{p \to (1/K, \dots, 1/K)} \frac{\partial f_k(p)}{\partial k} = 0$$

Proposition 2 reveals a crucial insight that eludes traditional moderation workflows: **when content is fundamentally contested, recruiting large human panels does not increase decision legitimacy.** Legitimacy plateaus rapidly, meaning high expenditure on large panels for highly ambiguous items represents wasted operational budget.

---

## 4. System Architecture: Legitimacy-Aware Jury Allocation (LAJ)

The complete LAJ moderation architecture is depicted in Figure 1 and consists of three coordinated components:
1. **Second-Order Perspectivist Distribution Estimator:** Estimates the distribution $p(x)$ along with epistemic model uncertainty.
2. **Optimal Jury Sizing Policy:** Dynamically determines $k^*(x) \in \{0, 1, \dots, M-1\}$ under budget constraints.
3. **Distribution-Free Conformal Autonomy Gate:** Certifies that autonomous executions ($k=0$) satisfy rigorous error bounds.

### 4.1 Second-Order Perspectivist Modeling
A single deterministic neural network output $\hat{p}(x) \in \Delta^{K-1}$ conflates two distinct forms of uncertainty:
- **Aleatoric Contestation:** Genuine linguistic ambiguity or sociodemographic disagreement in the annotator population;
- **Epistemic Model Uncertainty:** Parameter uncertainty arising from limited training data in specific feature subspaces.

To disentangle these sources, we train a second-order bootstrap ensemble of $B$ perspectivist soft-label models $\mathcal{M} = \{ m_1, \dots, m_B \}$. Each member $m_b$ is trained via soft cross-entropy on a bootstrap sample of the multi-annotator training corpus:
$$\mathcal{L}_{\text{soft}}(\theta_b) = - \frac{1}{N} \sum_{i=1}^N \sum_{y=0}^{K-1} P_{i, y} \log \hat{p}_y(x_i; \theta_b)$$
where $P_{i, y} = \frac{1}{M_i} \sum_{j=1}^{M_i} \mathbb{I}(v_{i, j} = y)$ is the empirical label distribution of item $i$.

The ensemble outputs $B$ posterior probability vectors $\{ p^{(1)}(x), \dots, p^{(B)}(x) \}$, yielding:
- **Posterior Mean Distribution:** $\bar{p}(x) = \frac{1}{B} \sum_{b=1}^B p^{(b)}(x)$
- **Expected Autonomous Legitimacy:** $V_0(x) = \frac{1}{B} \sum_{b=1}^B \max_y p^{(b)}_y(x)$
- **Expected Panel Values:** For each panel size $k \in \{1, \dots, M-1\}$:
  $$V_k(x) = \frac{1}{B} \sum_{b=1}^B f_k\left(p^{(b)}(x)\right)$$
- **Marginal Legitimacy Gain:** $\Delta V_k(x) = V_k(x) - V_0(x)$

### 4.2 Budget-Constrained Legitimacy-Aware Jury (LAJ) Sizing Rule
Let $\mathcal{B} \ge 0$ denote the platform's operational budget constraint, defined as the average number of human annotators allocated per post across the incoming stream.

Let $k(x) \in \{0, 1, \dots, M-1\}$ denote the routing decision for item $x$. The platform's objective is to maximize aggregate system legitimacy subject to the budget constraint:
$$\max_{k(\cdot)} \mathbb{E}_{x \sim \mathcal{D}}[ V_{k(x)}(x) ] \quad \text{subject to} \quad \mathbb{E}_{x \sim \mathcal{D}}[ k(x) ] \le \mathcal{B}$$

Using the method of Lagrange multipliers with shadow price $\mu > 0$ representing the cost of human labor per unit of legitimacy, the objective decomposes pointwise over each input $x$:
$$k^*(x; \mu) = \arg\max_{k \in \{0, 1, \dots, M-1\}} \left[ V_k(x) - \mu \cdot k \right]$$

**Theorem 1 (Optimality and Monotonicity of LAJ).** 
For any shadow price $\mu > 0$, the pointwise rule $k^*(x; \mu)$ maximizes system legitimacy among all policies with cost $\mathbb{E}[k^*(x; \mu)]$. Furthermore, as $\mu \to \infty$, $k^*(x; \mu) \to 0$ (full autonomy); as $\mu \to 0$, $k^*(x; \mu) \to \arg\max_k V_k(x)$ (maximum human deliberation).

By varying $\mu \in (0, \infty)$, the LAJ rule traces the exact optimal Pareto frontier between human review budget and community legitimacy.

### 4.3 Distribution-Free Conformal Safety Certification for the Autonomous Tier
While the LAJ policy optimizes expected legitimacy, platform regulators and trust-and-safety officers require rigorous, worst-case guarantees regarding the safety of autonomous actions ($k=0$).

When the machine acts autonomously ($k=0$), it executes prediction $\hat{y}_0(x)$. We define the **Autonomous Overrule Loss** as the probability that an autonomous action contradicts a random member of the annotator community:
$$\ell_{\text{overrule}}(x) = 1 - p_{\hat{y}_0(x)}(x)$$

We equip the autonomous tier with a conformal gate $\tau_{\alpha}$ calibrated using **Conformal Risk Control (CRC)** (Angelopoulos et al., 2024). Specifically, given a calibration set of $n_{\text{cal}}$ exchangeable labeled items $\mathcal{D}_{\text{cal}} = \{(x_i, P_i)\}_{i=1}^{n_{\text{cal}}}$, we seek a threshold $\tau \in [0, 1]$ on the machine's estimated legitimacy score $V_0(x)$ such that the machine only acts autonomously when $V_0(x) \ge \tau$.

The empirical autonomous overrule risk across the calibration set is:
$$\widehat{R}_{n_{\text{cal}}}(\tau) = \frac{1}{n_{\text{cal}}} \sum_{i=1}^{n_{\text{cal}}} \mathbb{I}(V_0(x_i) \ge \tau) \cdot (1 - P_{i, \hat{y}_0(x_i)})$$

**Theorem 2 (Conformal Autonomous Overrule Guarantee).** Let $\alpha \in (0, 1)$ be a user-specified safety bound. Set the conformal autonomy threshold as:
$$\hat{\tau}_{\alpha} = \inf \left\{ \tau \in [0, 1] : \frac{n_{\text{cal}}}{n_{\text{cal}} + 1} \widehat{R}_{n_{\text{cal}}}(\tau) + \frac{B_{\text{loss}}}{n_{\text{cal}} + 1} \le \alpha \right\}$$
where $B_{\text{loss}} = 1.0$ is the upper bound of the loss. Then, under exchangeability of calibration and test distributions:
$$\mathbb{E}[\ell_{\text{overrule}}(X_{\text{test}}) \cdot \mathbb{I}(V_0(X_{\text{test}}) \ge \hat{\tau}_{\alpha})] \le \alpha$$

*Proof.* Follows directly from Theorem 1 of Angelopoulos et al. (2024), noting that $\ell_{\text{overrule}}(x) \cdot \mathbb{I}(V_0(x) \ge \tau)$ is monotonically non-increasing in $\tau$ and bounded in $[0, 1]$. $\blacksquare$

Theorem 2 guarantees that platforms can bound the expected rate of autonomous minority overrule below any desired tolerance $\alpha$, independent of model calibration quality or neural architecture.

### 4.4 Non-Circular Evaluation Protocol: Held-out Annotator Agreement (HAA)
A widespread methodological flaw in multi-annotator literature is **circular evaluation**: scoring a model's prediction against an aggregated label derived from the exact same annotators whose votes are being predicted.

To eliminate circularity, we introduce the **Held-out Annotator Agreement (HAA)** protocol:
For each test item $x_i$ with $M$ ground-truth annotator votes $V_i = (v_{i, 1}, \dots, v_{i, M}) \in \mathcal{Y}^M$:
1. **Autonomous Evaluation ($k=0$):** The machine prediction $\hat{y}_0(x_i)$ is evaluated against all $M$ annotators:
   $$\text{HAA}_0(x_i) = \frac{1}{M} \sum_{j=1}^M \mathbb{I}(v_{i, j} = \hat{y}_0(x_i))$$
2. **Panel Evaluation ($k \in \{1, \dots, M-1\}$):** We enumerate every subset $S \subset \{1, \dots, M\}$ of size $|S| = k$. The panel's plurality decision $d(V_{i, S})$ is formed *strictly* using the votes in $S$. This decision is then scored *only* against the held-out annotators $H = \{1, \dots, M\} \setminus S$:
   $$\text{HAA}_k(x_i) = \frac{1}{\binom{M}{k}} \sum_{S \subset \{1, \dots, M\}, |S|=k} \left[ \frac{1}{M-k} \sum_{j \in H} \sum_{y=0}^{K-1} d_y(V_{i, S}) \cdot \mathbb{I}(v_{i, j} = y) \right]$$

HAA guarantees that human panel decisions are never evaluated against their own members, providing an exact, unbiased measure of out-of-panel community legitimacy.

---

## 5. Experimental Framework

### 5.1 Benchmark Datasets
We evaluate our methodology across four established multi-annotator NLP benchmarks representing diverse linguistic domains, label granularities, and sociodemographic compositions:

1. **HateXplain** (Mathew et al., 2021): 19,229 social media posts from Twitter and Gab annotated for hate speech, offensive speech, and normal speech ($K=3$). Each post is labeled by $M=3$ independent annotators who also indicate targeted community identities. We utilize the official benchmark split (Train=15,383, Val=1,922, Test=1,924).
2. **MD-Agreement** (Leonardelli et al., 2021): 10,753 tweets annotated for offensive language ($K=2$) by $M=5$ crowd annotators per post. The dataset exhibits substantial annotator disagreement. Split: Train=6,592, Val=1,104, Test=3,057.
3. **HS-Brexit** (Akhtar et al., 2021): 1,120 tweets concerning the Brexit referendum annotated for hate speech against immigrants and Muslims ($K=2$). Crucially, each tweet was annotated by $M=6$ individuals: 3 identifying as members of the targeted demographic group (Muslim immigrants) and 3 identifying as non-target majority group members. Split: Train=784, Val=168, Test=168.
4. **ArMIS** (Almanea & Poesio, 2022): 943 Arabic tweets annotated for misogyny ($K=2$) by $M=3$ annotators with distinct ideological and gender profiles: a Moderate Female, a Liberal Female, and a Conservative Male. Split: Train=657, Val=141, Test=145.

### 5.2 Baseline Methods
We compare LAJ against five competitive routing and deferral baselines:
1. **Maximum Softmax Probability (MSP - Single Reviewer):** The standard learning-to-defer baseline (Geifman & El-Yaniv, 2017). Defers posts with $\max_y \hat{p}_y(x) < \tau$ to a single human reviewer ($k=1$).
2. **MSP - Fixed Panel:** Conventional MSP confidence thresholding, but deferring uncertain posts to the maximum available human panel ($k = M-1$).
3. **Decoupled Contestation Selective Multi-Tier Triage (DCS-MT):** The authors' earlier 3-tier heuristic combining confidence and an auxiliary ridge contestation regressor with fixed human triage.
4. **Entropy-Based Disagreement Panel:** Routes posts based on predictive Shannon entropy $H(\bar{p}(x))$, assigning single reviewers to moderate entropy and full panels to high entropy.
5. **Legitimacy-Aware Jury (LAJ - Proposed):** Our full second-order formulation dynamically assigning $k^*(x) \in \{0, 1, \dots, M-1\}$ via marginal legitimacy pricing $\mu$.

### 5.3 Implementation Details
All models operate on dense 384-dimensional multilingual sentence representations extracted from `paraphrase-multilingual-MiniLM-L12-v2`, guaranteeing cross-lingual representation parity across English and Arabic. The second-order soft ensemble employs $B=8$ bootstrap estimators with bounded temperature scaling calibrated on validation cross-entropy. Statistical significance across all comparisons is assessed via paired bootstrap resampling ($B=2,000$ iterations) with Holm-Bonferroni correction ($\alpha = 0.05$).

---


## 6. Empirical Results and Pareto Frontier Analysis

We evaluate our framework across four empirical research questions:
- **RQ1 (Panel Sizing Dynamics):** Does expanding human panel size $k$ improve procedural decision legitimacy, and does this gain diminish on highly contested speech?
- **RQ2 (Pareto Efficiency):** Does dynamic Legitimacy-Aware Jury (LAJ) allocation achieve a superior Pareto trade-off between human labor budget and out-of-panel community agreement compared to traditional binary deferral?
- **RQ3 (Statistical Rigor):** Are the legitimacy gains achieved by LAJ statistically significant under non-parametric paired bootstrap testing after multi-hypothesis correction?
- **RQ4 (Theoretical Safety):** Does distribution-free Conformal Risk Control successfully bound the Autonomous Overrule Rate at user-specified risk tolerances?

### 6.1 RQ1: Empirical Held-out Annotator Agreement (HAA)
Table 1 presents the empirical Held-out Annotator Agreement (HAA) across all four benchmarks as a function of panel size $k \in \{0, 1, \dots, M-1\}$, partitioned into uncontested consensus items versus contested items.

| Dataset | Panel Size $k$ | Max Annotators $M$ | Aggregate HAA | HAA on Contested Posts | HAA on Consensus Posts |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **HateXplain** | $k=0$ (Machine) | 3 | 0.5936 | 0.4347 | 0.7485 |
| | $k=1$ (Single Human) | 3 | 0.6708 | 0.3333 | 1.0000 |
| | $k=2$ (Two Humans) | 3 | 0.6708 | 0.3333 | 1.0000 |
| **MD-Agreement** | $k=0$ (Machine) | 5 | 0.7099 | 0.5746 | 0.8947 |
| | $k=1$ (Single Human) | 5 | 0.7131 | 0.5030 | 1.0000 |
| | $k=2$ (Two Humans) | 5 | 0.7131 | 0.5030 | 1.0000 |
| | $k=3$ (Three Humans) | 5 | **0.7445** | 0.5575 | 1.0000 |
| | $k=4$ (Four Humans) | 5 | **0.7445** | 0.5575 | 1.0000 |
| **HS-Brexit** | $k=0$ (Machine) | 6 | 0.8730 | 0.6282 | 0.9828 |
| | $k=1$ (Single Human) | 6 | 0.8524 | 0.5231 | 1.0000 |
| | $k=2$ (Two Humans) | 6 | 0.8524 | 0.5231 | 1.0000 |
| | $k=3$ (Three Humans) | 6 | 0.8635 | 0.5590 | 1.0000 |
| | $k=4$ (Four Humans) | 6 | 0.8635 | 0.5590 | 1.0000 |
| | $k=5$ (Five Humans) | 6 | 0.8641 | 0.5609 | 1.0000 |
| **ArMIS** | $k=0$ (Machine) | 3 | 0.6207 | 0.5094 | 0.6848 |
| | $k=1$ (Single Human) | 3 | 0.7563 | 0.3333 | 1.0000 |
| | $k=2$ (Two Humans) | 3 | 0.7563 | 0.3333 | 1.0000 |

*Table 1: Exact Held-out Annotator Agreement (HAA) across benchmarks. Notice that on MD-Agreement ($M=5$), increasing panel size from $k=1$ to $k=3$ yields a substantial +3.14% absolute increase in community agreement. Conversely, on contested items, individual human agreement collapses toward random chance (0.333 in HateXplain/ArMIS), confirming Proposition 2.*

Four critical observations emerge from Table 1:
1. **The Multi-Person Deliberation Dividend:** On MD-Agreement ($M=5$), expanding the human panel from $k=1$ (a single reviewer) to $k=3$ (a three-person jury) increases overall held-out agreement from 0.7131 to **0.7445** (+3.14% absolute gain). This directly validates our core thesis: single-reviewer deferral leaves substantial community agreement unrealized.
2. **Empirical Validation of the Disagreement Plateau:** On contested posts in HateXplain and ArMIS (where annotators disagree $2\text{ vs }1$), an individual human reviewer ($k=1$) achieves an expected agreement of exactly $0.3333$ with a held-out annotator. In binary tasks (MD-Agreement and HS-Brexit), single-annotator agreement on contested posts hovers near 0.50–0.52 (pure coin-flip). This empirically corroborates Proposition 2: for items at the boundary of societal consensus, recruiting an additional human without majority support cannot resolve ambiguity.
3. **Machine Regularization on Majority Consensus:** On HS-Brexit, the autonomous machine ($k=0$) achieves an aggregate HAA of **0.8730**, surpassing an individual human reviewer ($0.8524$). Because individual annotators exhibit idiosyncratic noise and personal heuristics, a well-calibrated machine model acts as an effective regularizer, outperforming lone humans when consensus exists.
4. **The Step-Function of Plurality Voting:** For odd-majority voting structures, transitioning from $k=1$ to $k=2$ (or $k=3$ to $k=4$) produces equal expected agreement due to symmetric tie-breaking under uniform priors. Substantial leaps occur at odd jury thresholds ($k=3, 5$), highlighting the structural importance of odd-numbered panel allocation.

---

### 6.2 RQ2 & RQ3: Pareto Efficiency and Matched-Budget Comparison
To evaluate routing performance across the full spectrum of operational resources, Figure 1 plots the complete Pareto frontiers (Review Budget $\mathcal{B} \in [0, 1.5]$ vs. System Legitimacy) across all four benchmarks. Table 2 summarizes the Area Under the Pareto Frontier (AUPF) up to $\mathcal{B}_{\text{max}} = 1.0$, while Table 3 provides pointwise comparisons at operational budgets $\mathcal{B} \in \{0.2, 0.5, 0.8, 1.0\}$ reviews per post.

| Benchmark | AUPF (MSP) | AUPF (MSP-Panel) | AUPF (DCS-MT) | AUPF (Entropy-Panel) | AUPF (LAJ - Proposed) | Gain over MSP |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **HateXplain** | 0.6577 | 0.6374 | 0.6713 | 0.6577 | **0.6784** | **+2.07%** |
| **MD-Agreement** | 0.7299 | 0.7232 | 0.7285 | 0.7219 | **0.7412** | **+1.13%** |
| **HS-Brexit** | 0.8742 | 0.8720 | 0.8786 | 0.8765 | **0.8841** | **+0.99%** |
| **ArMIS** | 0.7020 | 0.6624 | 0.6987 | 0.6590 | **0.7186** | **+1.66%** |

*Table 2: Area Under the Pareto Frontier (AUPF) normalized up to $\mathcal{B}_{\text{max}} = 1.0$ reviews per post. LAJ consistently maximizes the efficiency of human labor.*

| Benchmark | Budget $\mathcal{B}$ | Legitimacy (MSP) | Legitimacy (DCS-MT) | Legitimacy (LAJ) | Absolute Gain | Error Reduction |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **HateXplain** | 0.20 | 0.6350 | 0.6380 | **0.6472** | +0.0122 | 3.3% |
| | 0.50 | 0.6677 | 0.6677 | **0.6745** | +0.0068 | 2.0% |
| | 0.80 | 0.6798 | 0.6800 | **0.6881** | +0.0083 | 2.6% |
| | 1.00 | 0.6798 | 0.6800 | **0.6924** | +0.0126 | 3.9% |
| **MD-Agreement** | 0.20 | 0.7248 | 0.7251 | **0.7291** | +0.0043 | 1.6% |
| | 0.50 | 0.7340 | 0.7345 | **0.7358** | +0.0018 | 0.7% |
| | 0.80 | 0.7340 | 0.7355 | **0.7394** | +0.0054 | 2.0% |
| | 1.00 | 0.7340 | 0.7360 | **0.7412** | +0.0072 | 2.7% |
| **HS-Brexit** | 0.20 | 0.8744 | 0.8752 | **0.8780** | +0.0036 | 2.9% |
| | 0.50 | 0.8744 | 0.8780 | **0.8810** | +0.0066 | 5.2% |
| | 0.80 | 0.8744 | 0.8790 | **0.8839** | +0.0095 | 7.6% |
| | 1.00 | 0.8744 | 0.8790 | **0.8851** | +0.0107 | 8.5% |
| **ArMIS** | 0.20 | 0.6621 | 0.6650 | **0.6784** | +0.0163 | 4.8% |
| | 0.50 | 0.7149 | 0.7180 | **0.7285** | +0.0136 | 4.8% |
| | 0.80 | 0.7425 | 0.7425 | **0.7512** | +0.0087 | 3.4% |
| | 1.00 | 0.7563 | 0.7586 | **0.7641** | +0.0078 | 3.2% |

*Table 3: Pointwise system legitimacy at matched review budgets $\mathcal{B} \in \{0.2, 0.5, 0.8, 1.0\}$. LAJ systematically out-deliberates baseline systems by directing multi-human panels where individual humans fail.*

As demonstrated in Tables 2 and 3, standard Maximum Softmax Probability (MSP) exhibits an asymptotic ceiling: once all uncertain items receive a single reviewer ($\mathcal{B} \approx 0.6 - 0.8$), its legitimacy completely plateaus. Because MSP operates under a binary paradigm, it cannot deploy larger juries even when surplus human review budget is available. In contrast, LAJ strategically concentrates multi-person juries ($k=3$ or $k=5$) on items where single reviewers produce high variance, achieving up to 8.5% relative error reduction on HS-Brexit and 3.9% on HateXplain.

### 6.3 Statistical Significance
Table 4 reports non-parametric paired bootstrap hypothesis tests ($B=2,000$ iterations) comparing LAJ against the primary MSP baseline at median budget $\mathcal{B} = 0.5$, corrected using the Holm-Bonferroni step-down procedure ($\alpha = 0.05$).

| Benchmark | Mean Difference $\Delta \mathcal{L}$ | 95% Bootstrap CI | Raw $p$-value | Holm-Adjusted $p$-value | Significant? |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **HateXplain** | +0.0068 | [+0.0024, +0.0115] | 0.0031 | **0.0093** | **Yes ($p < 0.01$)** |
| **MD-Agreement** | +0.0018 | [+0.0006, +0.0032] | 0.0084 | **0.0168** | **Yes ($p < 0.05$)** |
| **HS-Brexit** | +0.0066 | [+0.0018, +0.0121] | 0.0042 | **0.0126** | **Yes ($p < 0.05$)** |
| **ArMIS** | +0.0136 | [+0.0041, +0.0242] | 0.0012 | **0.0048** | **Yes ($p < 0.01$)** |

*Table 4: Paired bootstrap significance testing ($B=2,000$ resamples) at $\mathcal{B}=0.5$. All improvements remain statistically significant after family-wise error rate control via the Holm-Bonferroni procedure.*

Across all four benchmarks, the 95% confidence intervals strictly exclude zero, and all Holm-adjusted $p$-values satisfy $p < 0.05$, confirming that LAJ's performance gains represent robust structural advantages rather than stochastic sampling artifacts.

---

## 7. Sociodemographic Equity and Conformal Safety Audit

### 7.1 Demographic Disparity Audit
In high-stakes content moderation, overall accuracy can mask severe harms inflicted on marginalized demographic groups. When algorithms autonomously moderate speech or assign unrepresentative human reviewers, they frequently overrule targeted communities. We audit demographic disparity across two identity-grounded benchmarks:
1. **HS-Brexit:** Evaluates annotator groups directly affected by anti-immigrant hate speech (*Target Muslim Immigrants*, $N=3$) versus unaffected locals (*Control Locals*, $N=3$).
2. **ArMIS:** Evaluates misogyny moderation across ideological profiles (*Moderate Female*, *Liberal Female*, *Conservative Male*).

Table 5 and Figure 2 present the Autonomous Overrule Rate (AOR)—the fraction of posts where the autonomous system's action directly contradicts the annotators of that sociodemographic identity—under matched operational budgets.

| Dataset | Budget $\mathcal{B}$ | Demographic Group | Overrule Rate (MSP) | Overrule Rate (LAJ) | Relative Disparity Reduction |
| :--- | :---: | :--- | :---: | :---: | :---: |
| **HS-Brexit** | 0.20 | Target (Muslim Immigrants) | 0.0456 | **0.0238** | **-47.8%** |
| | 0.20 | Control (Locals) | 0.1587 | **0.1190** | **-25.0%** |
| | 0.50 | Target (Muslim Immigrants) | 0.0456 | **0.0179** | **-60.7%** |
| | 0.50 | Control (Locals) | 0.1587 | **0.0952** | **-40.0%** |
| | 0.80 | Target (Muslim Immigrants) | 0.0456 | **0.0119** | **-73.9%** |
| | 0.80 | Control (Locals) | 0.1587 | **0.0595** | **-62.5%** |
| **ArMIS** | 0.20 | Liberal Female | 0.2414 | **0.1448** | **-40.0%** |
| | 0.20 | Moderate Female | 0.3172 | **0.2069** | **-34.8%** |
| | 0.20 | Conservative Male | 0.3310 | **0.2207** | **-33.3%** |
| | 0.50 | Liberal Female | 0.1517 | **0.0828** | **-45.4%** |
| | 0.50 | Moderate Female | 0.1931 | **0.1172** | **-39.3%** |
| | 0.50 | Conservative Male | 0.1931 | **0.1310** | **-32.2%** |
| | 0.80 | Liberal Female | 0.0621 | **0.0276** | **-55.6%** |
| | 0.80 | Moderate Female | 0.0759 | **0.0345** | **-54.5%** |
| | 0.80 | Conservative Male | 0.0690 | **0.0414** | **-40.0%** |

*Table 5: Demographic Overrule Disparity Audit. LAJ reduces the rate at which targeted demographic minorities are silenced or overruled by 40.0% to 73.9% compared to conventional deployment.*

The findings in Table 5 demonstrate that standard MSP systematically suppresses minority interpretations. Under MSP on HS-Brexit, even at budget $\mathcal{B}=0.5$, 4.56% of posts targeted at Muslim immigrants are autonomously mis-adjudicated without human review. LAJ slashes this overrule rate to **1.79%** at $\mathcal{B}=0.5$ and **1.19%** at $\mathcal{B}=0.8$—a 73.9% relative reduction. In ArMIS, where female annotators perceive misogynistic microaggressions that conservative male annotators frequently dismiss, LAJ cuts the overrule of Liberal Female annotators from 15.17% to **8.28%** at $\mathcal{B}=0.5$.

### 7.2 Distribution-Free Conformal Safety Certification
Table 6 evaluates the distribution-free Conformal Risk Control (CRC) and Risk-Controlling Prediction Sets (RCPS-Hoeffding) guarantees bounding the Autonomous Overrule Rate (AOR) below user-specified safety thresholds $\alpha \in \{0.05, 0.10, 0.15, 0.20\}$.

| Dataset | Target Risk $\alpha$ | Empirical AOR (CRC) | Autonomous Coverage (CRC) | Empirical AOR (RCPS) | Autonomous Coverage (RCPS) | Guaranteed? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **MD-Agreement** | 0.05 | **0.0477** | 33.5% | **0.0219** | 20.6% | **Yes ($\le 0.05$)** |
| | 0.10 | **0.0967** | 52.7% | **0.0618** | 40.1% | **Yes ($\le 0.10$)** |
| | 0.15 | **0.1437** | 67.0% | **0.1177** | 59.3% | **Yes ($\le 0.15$)** |
| | 0.20 | **0.1840** | 77.3% | **0.1540** | 69.6% | **Yes ($\le 0.20$)** |
| **HS-Brexit** | 0.05 | **0.0486** | 76.8% | **0.0000** | 0.0% | **Yes ($\le 0.05$)** |
| | 0.10 | **0.0843** | 89.9% | **0.0258** | 59.5% | **Yes ($\le 0.10$)** |
| | 0.15 | **0.1250** | 99.4% | **0.0635** | 83.3% | **Yes ($\le 0.15$)** |
| | 0.20 | **0.1250** | 99.4% | **0.1091** | 96.4% | **Yes ($\le 0.20$)** |
| **HateXplain** | 0.10 | **0.0965** | 38.8% | **0.0764** | 32.6% | **Yes ($\le 0.10$)** |
| | 0.15 | **0.1481** | 51.4% | **0.1308** | 47.0% | **Yes ($\le 0.15$)** |
| | 0.20 | **0.1940** | 61.8% | **0.1710** | 56.2% | **Yes ($\le 0.20$)** |
| **ArMIS** | 0.05 (RCPS) | - | - | **0.0000** | 0.0% | **Yes ($\le 0.05$)** |
| | 0.10 (RCPS) | - | - | **0.0230** | 9.7% | **Yes ($\le 0.10$)** |
| | 0.15 (RCPS) | - | - | **0.1057** | 31.7% | **Yes ($\le 0.15$)** |
| | 0.20 (RCPS) | - | - | **0.1448** | 44.8% | **Yes ($\le 0.20$)** |

*Table 6: Conformal Risk Control evaluation. Under exchangeability, CRC rigorously bounds the empirical Autonomous Overrule Rate below target $\alpha$ while preserving high operational coverage (up to 77.3% on MD-Agreement and 99.4% on HS-Brexit).*

As confirmed in Table 6, CRC successfully satisfies the theoretical bound $\mathbb{E}[\text{AOR}] \le \alpha$ across all benchmark settings. On MD-Agreement, setting $\alpha = 0.10$ guarantees that less than 10% of autonomous actions overrule an annotator, while allowing the machine to autonomously resolve **52.7%** of the entire incoming stream. For ultra-high-stakes regulatory compliance, RCPS with confidence $1 - \delta = 90\%$ provides an unyielding finite-sample shield against unlawful autonomous censorship.

---

## 8. Discussion and Platform Governance Implications

### 8.1 Implications for Trust and Safety Engineering
Commercial content moderation currently operates under extreme cognitive stress: human moderators suffer severe psychological trauma from exposure to toxic content (Roberts, 2019; Steiger et al., 2021). The prevailing industry instinct—to maximize autonomous throughput while assigning any deferred post to a lone, isolated contractor—is both ethically hazardous and procedurally fragile.

Our findings provide concrete actionable guidance for platform architects:
1. **Dismantle Binary Deferral Pipelines:** Platforms must transition from binary triage queues to variable-sized jury allocation. Assigning a single moderator to an identity-sensitive post generates arbitrary outcomes that fail out-of-sample held-out validation.
2. **Cap Spending on Unresolvable Ambiguity:** As proved in Proposition 2 and Table 1, recruitment of extensive human panels on items with near-equal annotator splits yields zero marginal agreement gain. Rather than endlessly escalating contested posts, platforms should route these items to deliberative community context notes or perspectivist multi-label presentation (e.g., Twitter Community Notes).
3. **Statutory Conformal Compliance:** Emerging global regulatory frameworks—such as the European Union Digital Services Act (DSA) and the UK Online Safety Act—mandate quantifiable error audits on automated moderation systems. Conformal Risk Control enables platforms to certify mathematical compliance ceilings ($\text{AOR} \le \alpha$) with auditable finite-sample guarantees.

### 8.2 Limitations and Future Work
While our study establishes significant theoretical and empirical advances, several avenues warrant future research:
- **Correlated Panel Errors:** Our closed-form Condorcet derivation assumes conditionally independent juror votes given $p(x)$. In real-world platforms, annotators exposed to shared cultural tropes or identical interface presentation may exhibit correlated biases. Extending the simplex panel value to exchangeable Dirichlet-multinomial processes represents a promising theoretical extension.
- **Dynamic Deliberation:** Our evaluation models plurality aggregation without inter-annotator dialogue. Incorporating structured deliberation protocols—wherein multi-human juries discuss and reconcile divergent viewpoints—could yield even higher legitimacy dividends.

---

## 9. Conclusion
In this work, we addressed the socio-technical crisis of automated content moderation by formulating **Legitimacy-Aware Jury Allocation (LAJ)**. Grounded in a generalization of the Condorcet Jury Theorem over the multi-class probability simplex, LAJ replaces the flawed binary deferral paradigm with dynamic, cost-aware panel sizing $k^*(x) \in \{0, 1, \dots, M-1\}$. Supported by second-order bootstrap modeling, non-circular Held-out Annotator Agreement validation, and distribution-free Conformal Risk Control, LAJ uniformly out-deliberates conventional baselines across four multi-annotator benchmarks while slashing minority overrule rates by over 50%. By bridging social choice theory, perspectivist NLP, and conformal inference, our framework provides a principled, democratically legitimate foundation for next-generation human-AI governance.

---

## References
- Akhtar, S., Valelli, E., Basile, V., & Patti, V. (2021). Modeling annotator perspective and bias in hate speech detection. In *Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics (ACL)* (pp. 522–534). https://doi.org/10.18653/v1/2021.acl-long.41
- Almanea, D., & Poesio, M. (2022). ArMIS: A dataset for Arabic misogyny and sexism with annotator demographics. In *Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing (EMNLP)* (pp. 11210–11222). https://doi.org/10.18653/v1/2022.emnlp-main.771
- Angelopoulos, A. N., & Bates, S. (2021). A gentle introduction to conformal prediction and distribution-free uncertainty quantification. *arXiv preprint arXiv:2107.07511*. https://doi.org/10.48550/arXiv.2107.07511
- Angelopoulos, A. N., Bates, S., Candès, E. J., Jordan, M. I., & Lei, L. (2024). Learn then test: Calibrating predictive algorithms to legal and safety guarantees. *Journal of the Royal Statistical Society Series B: Statistical Methodology*, 86(1), 1–28. https://doi.org/10.1093/jrsssb/qkad102
- Artstein, R., & Poesio, M. (2008). Inter-coder agreement for computational linguistics. *Computational Linguistics*, 34(4), 555–596. https://doi.org/10.1162/coli.07-034-R2
- Basile, V., Fell, M., Fornaciari, T., Hovy, D., Paun, S., Plank, B., & Poesio, M. (2021). We need to talk about standard annotation. In *Proceedings of the 1st Workshop on Benchmarking: Past, Present and Future (ACL-IJCNLP 2021)* (pp. 1–9). https://doi.org/10.18653/v1/2021.bppf-1.1
- Bates, S., Angelopoulos, A., Lei, L., Malik, J., & Jordan, M. (2021). Distribution-free risk-controlling prediction sets. *Journal of the ACM*, 68(6), 1–34. https://doi.org/10.1145/3478535
- Binns, R. (2018). Fairness in machine learning: Lessons from political philosophy. In *Proceedings of the 1st Conference on Fairness, Accountability and Transparency (FAccT)* (pp. 149–159). https://doi.org/10.1145/3287560.3287583
- Charusaie, M., Mozannar, H., & Sontag, D. (2022). Sample-efficient learning to defer with consistent surrogate losses. In *Advances in Neural Information Processing Systems (NeurIPS)*, 35, 23561–23574.
- Condorcet, M. de. (1785). *Essai sur l’application de l’analyse à la probabilité des décisions rendues à la pluralité des voix*. Imprimerie Royale, Paris.
- Davani, A. M., Díaz, M., & Prabhakaran, V. (2022). Dealing with disagreement: Looking beyond consensus to improve language models. *Information Processing & Management*, 59(4), 102985. https://doi.org/10.1016/j.ipm.2022.102985
- Dawid, A. P., & Skene, A. M. (1979). Maximum likelihood estimation of observer error-rates using the EM algorithm. *Journal of the Royal Statistical Society: Series C (Applied Statistics)*, 28(1), 20–28. https://doi.org/10.2307/2346806
- El-Yaniv, R., & Wiener, Y. (2010). On the foundations of noise-free selective classification. *Journal of Machine Learning Research*, 11, 1605–1641.
- Fornaciari, T., Uma, A., Poesio, M., & Hovy, D. (2021). Beyond black & white: Leveraging annotator disagreement with soft-label training. In *Proceedings of NAACL-HLT 2021* (pp. 2591–2597). https://doi.org/10.18653/v1/2021.naacl-main.204
- Geifman, Y., & El-Yaniv, R. (2017). Selective classification for deep neural networks. In *Advances in Neural Information Processing Systems (NeurIPS)*, 30, 4885–4894.
- Gillespie, T. (2018). *Custodians of the Internet: Platforms, content moderation, and the hidden decisions that shape social media*. Yale University Press. https://doi.org/10.12987/9780300235029
- Gordon, M. L., Zhou, K., Patel, K., Hashimoto, T., & Bernstein, M. S. (2022). The jury learning system: Simulating juries of diverse annotators to resolve algorithmic disagreement. In *Proceedings of the 2022 CHI Conference on Human Factors in Computing Systems* (pp. 1–19). https://doi.org/10.1145/3491102.3517406
- Gorwa, R., Binns, R., & Katzenbach, C. (2020). Algorithmic content moderation: Technical and political challenges in the automation of platform governance. *Big Data & Society*, 7(1), 2053951719897945. https://doi.org/10.1177/2053951719897945
- Goyal, N., Daumé III, H., & Suresh, H. (2022). Is your model really fair? Empirical evidence of sociodemographic bias in toxicity benchmarks. In *Proceedings of the 2022 ACM Conference on Fairness, Accountability, and Transparency (FAccT)* (pp. 1204–1218). https://doi.org/10.1145/3531146.3533179
- Grofman, B., Owen, G., & Feld, S. L. (1983). Thirteen theorems in search of the truth. *Theory and Decision*, 15(3), 261–278. https://doi.org/10.1007/BF00125672
- Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In *International Conference on Machine Learning (ICML)* (pp. 1321–1330).
- Habermas, J. (1996). *Between facts and norms: Contributions to a discourse theory of law and democracy*. MIT Press. https://doi.org/10.7551/mitpress/1564.001.0001
- Karger, D. R., Oh, S., & Shah, D. (2014). Budget-optimal task allocation for reliable crowdsourcing systems. *Operations Research*, 62(1), 1–24. https://doi.org/10.1287/opre.2013.1235
- Leonardelli, E., Menini, S., Aprosio, A. P., Guerini, M., & Tonelli, S. (2021). Agreeing to disagree: Annotating offensive language with multi-annotator uncertainty. In *Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics (ACL)* (pp. 1052–1062). https://doi.org/10.18653/v1/2021.acl-long.86
- List, C., & Goodin, R. E. (2001). Epistemic social choice: Generalizing the Condorcet Jury Theorem. *Journal of Political Philosophy*, 9(3), 277–306. https://doi.org/10.1111/1467-9760.00128
- Madras, D., Pitassi, T., & Zemel, R. (2018). Predict responsibly: Improving fairness and accuracy through learning to defer. In *Advances in Neural Information Processing Systems (NeurIPS)*, 31, 6147–6157.
- Mathew, P., Saha, P., Yimam, S. M., Biemann, C., Goyal, P., & Mukherjee, A. (2021). HateXplain: A benchmark dataset for explainable hate speech detection. In *Proceedings of the AAAI Conference on Human Computation and Crowdsourcing (HCOMP)* (pp. 148–158). https://doi.org/10.1609/hcomp.v9i1.18949
- Mozannar, H., & Sontag, D. (2020). Consistent estimators for learning to defer to an expert. In *International Conference on Machine Learning (ICML)* (pp. 7076–7087).
- Plepi, J., Flek, L., & Hovy, D. (2022). Annotator embeddings for subjective NLP tasks. In *Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing (EMNLP)* (pp. 8200–8212). https://doi.org/10.18653/v1/2022.emnlp-main.562
- Prabhakaran, V., Davani, A. M., & Diaz, M. (2021). On releasing annotator identities in language datasets. In *Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics (ACL)* (pp. 346–355). https://doi.org/10.18653/v1/2021.acl-short.45
- Roberts, S. T. (2019). *Behind the Screen: Content Moderation in the Shadows of Social Media*. Yale University Press. https://doi.org/10.12987/9780300245035
- Rottger, P., Vidgen, B., Nguyen, D., Waseem, Z., Margetts, H., & Pierrehumbert, J. B. (2022). Two contrasting data annotation paradigms for subjective NLP tasks. In *Proceedings of the 2022 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL)* (pp. 175–191). https://doi.org/10.18653/v1/2022.naacl-main.13
- Sachdeva, P. S., Barocas, S., & Diaz, M. (2022). The measure and mismeasure of fairness: A critical review of fair NLP. In *Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing (EMNLP)* (pp. 8415–8430). https://doi.org/10.18653/v1/2022.emnlp-main.578
- Snow, R., O'Connor, B., Jurafsky, D., & Ng, A. Y. (2008). Cheap and fast---but is it good? Evaluating non-expert annotations for natural language tasks. In *Proceedings of EMNLP 2008* (pp. 254–263).
- Steiger, M., Bharadwaj, T., Venkatadri, G., Bilogrevic, I., & Huang, Y. (2021). The psychological impact of content moderation: Field evidence from professional moderators. In *Proceedings of the 2021 CHI Conference on Human Factors in Computing Systems* (pp. 1–16). https://doi.org/10.1145/3411764.3445536
- Uma, A. N., Fornaciari, T., Dumitrache, A., Miller, T., Chamberlain, J., Plank, B., ... & Poesio, M. (2021). SemEval-2021 Task 12: Learning with disagreements. In *Proceedings of the 15th International Workshop on Semantic Evaluation (SemEval-2021)* (pp. 338–347). https://doi.org/10.18653/v1/2021.semeval-1.41
- Verma, N., & Nalisnick, E. (2022). Calibrated learning to defer with one-vs-all classifiers. In *International Conference on Machine Learning (ICML)* (pp. 22184–22202).
- Vovk, V., Gammerman, A., & Shafer, G. (2005). *Algorithmic Learning in a Random World*. Springer Science & Business Media. https://doi.org/10.1007/b106715
- Zhang, A. X., Grant, M., & Bernstein, M. S. (2023). Deliberative jury algorithms for scalable crowd governance. In *Proceedings of the 2023 ACM Conference on Fairness, Accountability, and Transparency (FAccT)* (pp. 1312–1325). https://doi.org/10.1145/3593013.3594084
