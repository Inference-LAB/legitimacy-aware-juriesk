"""
Core methods for "How many humans does a decision need?" (IPM v2).

Contents
  1. Panel value f_k(p): expected agreement between the plurality decision of a k-person panel and an
     independent annotator, when votes are i.i.d. draws from the annotator distribution p (Section 3).
  2. Held-out Annotator Agreement (HAA): exact, non-circular evaluation of machine and panel decisions
     on real multi-annotator data, by enumerating every k-subset of the item's actual annotators and
     scoring the panel's decision only against the annotators who were NOT on the panel (Section 4.4).
  3. Annotator-distribution estimators: soft-label bootstrap ensemble (second-order), hard-label model,
     ridge contestation regressor (the authors' earlier DCS-MT baseline).
  4. Routing policies: the proposed Legitimacy-Aware Jury (LAJ) rule and all baselines.
  5. Distribution-free certification of the Autonomous Overrule Rate (CRC and RCPS-Hoeffding).
"""
import itertools
from math import lgamma

import numpy as np
from scipy.optimize import minimize_scalar
from sklearn.linear_model import LogisticRegression, Ridge


# --------------------------------------------------------------------------- 1. panel value f_k(p)
def _compositions(k, K):
    if K == 1:
        yield (k,)
        return
    for i in range(k + 1):
        for rest in _compositions(k - i, K - 1):
            yield (i,) + rest


def _decision(counts):
    c = np.asarray(counts, float)
    tie = (c == c.max()).astype(float)
    return tie / tie.sum()                     # plurality, ties broken uniformly at random


def panel_value(P, k):
    """f_k(p) for every row of P (n, K): E[ agreement(plurality of k iid votes, fresh iid vote) ]."""
    P = np.clip(np.asarray(P, float), 0.0, 1.0)
    n, K = P.shape
    out = np.zeros(n)
    for c in _compositions(k, K):
        logm = lgamma(k + 1) - sum(lgamma(ci + 1) for ci in c)
        prob = np.exp(logm) * np.prod(P ** np.asarray(c), axis=1)
        out += prob * (P @ _decision(c))
    return out


# --------------------------------------------------------------------------- 2. held-out agreement
def empirical_panel_haa(V, K, k, G=None, group=None):
    """Exact expected HAA of a k-panel drawn without replacement from each item's real annotators.

    The panel decides by plurality (uniform tie-break); the decision is scored against the item's
    remaining M-k annotators (or only those of `group`). Returns (value, valid_mask)."""
    n, M = V.shape
    assert 1 <= k <= M - 1
    num = np.zeros(n)
    den = np.zeros(n)
    for S in itertools.combinations(range(M), k):
        H = [j for j in range(M) if j not in S]
        counts = np.stack([(V[:, S] == y).sum(1) for y in range(K)], 1).astype(float)
        tie = (counts == counts.max(1, keepdims=True)).astype(float)
        d = tie / tie.sum(1, keepdims=True)
        if G is None:
            agree = np.stack([(V[:, H] == y).mean(1) for y in range(K)], 1)
            num += (d * agree).sum(1)
            den += 1.0
        else:
            m = (G[:, H] == group).astype(float)
            cnt = m.sum(1)
            ok = cnt > 0
            agree = np.stack([((V[:, H] == y) * m).sum(1) / np.maximum(cnt, 1) for y in range(K)], 1)
            num += np.where(ok, (d * agree).sum(1), 0.0)
            den += ok
    valid = den > 0
    return np.where(valid, num / np.maximum(den, 1), np.nan), valid


def machine_haa(V, yhat, G=None, group=None):
    agree = (V == yhat[:, None]).astype(float)
    if G is None:
        return agree.mean(1)
    m = (G == group).astype(float)
    return (agree * m).sum(1) / np.maximum(m.sum(1), 1)


# --------------------------------------------------------------------------- 3. estimators
def softmax(Z):
    Z = Z - Z.max(1, keepdims=True)
    E = np.exp(Z)
    return E / E.sum(1, keepdims=True)


def _logits(lr, X, K):
    Z = lr.decision_function(X)
    if Z.ndim == 1:
        Z = np.stack([np.zeros_like(Z), Z], 1)
    full = np.full((X.shape[0], K), -1e4)
    full[:, lr.classes_] = Z
    return full


def soft_ce(P_true, P_pred):
    return float(-(P_true * np.log(np.clip(P_pred, 1e-12, 1))).sum(1).mean())


def fit_temperature(Z_list, target, soft=True):
    """One temperature for all members, chosen on validation data by (soft) cross-entropy of the mean."""
    def obj(logT):
        T = np.exp(logT)
        Pm = np.mean([softmax(Z / T) for Z in Z_list], 0)
        return soft_ce(target, Pm)
    r = minimize_scalar(obj, bounds=(np.log(0.05), np.log(20)), method="bounded")
    return float(np.exp(r.x))


def _fit_lr(X, Y_soft, C, seed, idx=None):
    n, K = Y_soft.shape
    idx = np.arange(n) if idx is None else idx
    Xr = np.repeat(X[idx], K, axis=0)
    yr = np.tile(np.arange(K), len(idx))
    w = Y_soft[idx].reshape(-1)
    keep = w > 0
    lr = LogisticRegression(C=C, max_iter=3000, random_state=seed)
    lr.fit(Xr[keep], yr[keep], sample_weight=w[keep])
    return lr


class SoftEnsemble:
    """Second-order annotator-distribution model: B bootstrap soft-label logistic models.

    Each member estimates p_h(.|x); the spread across members expresses epistemic uncertainty about p_h."""

    def __init__(self, B=8, C_grid=(0.1, 0.3, 1.0, 3.0), seed=0):
        self.B, self.C_grid, self.seed = B, C_grid, seed

    def fit(self, Xtr, Ptr, Xva, Pva, K, C=None):
        self.K = K
        if C is None:
            scores = {}
            for c in self.C_grid:
                m = _fit_lr(Xtr, Ptr, c, self.seed)
                scores[c] = soft_ce(Pva, softmax(_logits(m, Xva, K)))
            C = min(scores, key=scores.get)
        self.C = C
        rng = np.random.default_rng(self.seed)
        n = len(Xtr)
        self.members = [_fit_lr(Xtr, Ptr, C, self.seed + b, rng.integers(0, n, n)) for b in range(self.B)]
        self.T = fit_temperature([_logits(m, Xva, K) for m in self.members], Pva)
        return self

    def member_probs(self, X):
        return np.stack([softmax(_logits(m, X, self.K) / self.T) for m in self.members], 0)  # (B, n, K)


class HardModel:
    """Conventional classifier trained on plurality labels + temperature scaling (MSP baselines)."""

    def fit(self, Xtr, ytr, Xva, yva, K, C_grid=(0.1, 0.3, 1.0, 3.0), seed=0):
        self.K = K
        Ytr = np.eye(K)[ytr]
        Yva = np.eye(K)[yva]
        best = None
        for c in C_grid:
            m = _fit_lr(Xtr, Ytr, c, seed)
            s = soft_ce(Yva, softmax(_logits(m, Xva, K)))
            if best is None or s < best[0]:
                best = (s, m)
        self.lr = best[1]
        self.T = fit_temperature([_logits(self.lr, Xva, K)], Yva)
        return self

    def probs(self, X):
        return softmax(_logits(self.lr, X, self.K) / self.T)


def fit_ridge_contestation(Xtr, htr, alpha=10.0):
    return Ridge(alpha=alpha).fit(Xtr, htr)


# --------------------------------------------------------------------------- uncertainty summaries
def entropy_rows(P):
    K = P.shape[-1]
    return -(np.where(P > 0, P * np.log(np.clip(P, 1e-12, 1)), 0.0)).sum(-1) / np.log(K)


def ensemble_summaries(Pm, M):
    """Pm: (B, n, K). Returns plug-in quantities used by the router and the diagnostics."""
    Pbar = Pm.mean(0)
    yhat = Pbar.argmax(1)
    total = entropy_rows(Pbar)
    aleatoric = entropy_rows(Pm).mean(0)                     # predicted human disagreement
    epistemic = np.maximum(total - aleatoric, 0.0)           # mutual information (model disagreement)
    p_contested = 1.0 - (Pm ** M).sum(2).mean(0)             # P(not unanimous among M annotators)
    V0 = Pbar[np.arange(len(yhat)), yhat]                    # predicted legitimacy of the machine decision
    return dict(Pbar=Pbar, yhat=yhat, total=total, aleatoric=aleatoric, epistemic=epistemic,
                p_contested=p_contested, V0=V0)


def panel_values_second_order(Pm, ks):
    """V_k(x) = E_{p ~ ensemble}[ f_k(p) ]: averages over members, so epistemic spread is kept."""
    return {k: np.mean([panel_value(P, k) for P in Pm], 0) for k in ks}


# --------------------------------------------------------------------------- 4. policies
def policy_threshold(score, t, k_defer):
    """Autonomous iff score >= t, otherwise a fixed panel of k_defer."""
    return np.where(score >= t, 0, k_defer)


def policy_dcs3(conf, cont, t_conf, t_cont, k_panel):
    """Authors' earlier DCS-MT rule: Tier0 auto, Tier1 single reviewer, Tier2 panel (k_panel)."""
    a = np.where(cont > t_cont, k_panel, np.where(conf >= t_conf, 0, 1))
    return a


def policy_laj(V0, Vk, mu, proc=0.0, p_contested=None, gate=None):
    """Legitimacy-Aware Jury rule: a*(x) = argmax_{a in {0} U K} V_a(x) - mu*k(a) - proc*1[a=0]*P(contested).

    gate (optional boolean array) forces deferral where the certified autonomy gate is closed."""
    ks = sorted(Vk)
    util0 = V0 - (proc * p_contested if proc and p_contested is not None else 0.0)
    U = np.stack([util0] + [Vk[k] - mu * k for k in ks], 1)
    if gate is not None:
        U[~gate, 0] = -np.inf
    choice = U.argmax(1)
    return np.array([0] + ks)[choice]


def policy_entropy_panel(V0, aleatoric, t_auto, t_ent, k_panel):
    """Disagreement-aware heuristic: auto if V0 >= t_auto; else panel if predicted disagreement high, else 1."""
    return np.where(V0 >= t_auto, 0, np.where(aleatoric > t_ent, k_panel, 1))


# --------------------------------------------------------------------------- evaluation
def evaluate(actions, yhat, P, HAA, plurality, contested):
    """System-level metrics. HAA: dict k -> exact empirical held-out agreement of a k-panel per item."""
    n = len(actions)
    ar = np.arange(n)
    haa = P[ar, yhat].copy()
    for k, v in HAA.items():
        m = actions == k
        haa[m] = v[m]
    auto = actions == 0
    cons = contested == 0
    return dict(
        legitimacy=float(haa.mean()),
        budget=float(actions.mean()),
        coverage=float(auto.mean()),
        AOR=float((auto * (1.0 - P[ar, yhat])).mean()),                           # autonomous overrule rate
        CAV=float((auto & (contested == 1)).sum() / max((contested == 1).sum(), 1)),
        cons_err=float((auto & cons & (yhat != plurality)).sum() / max(cons.sum(), 1)),
        per_item=haa,
    )


def pareto_frontier(points):
    """points: list of (budget, legitimacy, payload). Upper-left monotone frontier sorted by budget."""
    pts = sorted(points, key=lambda r: (r[0], -r[1]))
    front, best = [], -np.inf
    for b, l, p in pts:
        if l > best + 1e-12:
            front.append((b, l, p))
            best = l
    return front


def legit_at_budget(front, B):
    feas = [r for r in front if r[0] <= B + 1e-9]
    return max(feas, key=lambda r: r[1]) if feas else None


def area_under_frontier(front, Bmax=1.0, grid=201):
    xs = np.linspace(0, Bmax, grid)
    ys = []
    for x in xs:
        r = legit_at_budget(front, x)
        ys.append(r[1] if r else np.nan)
    ys = np.array(ys)
    ok = ~np.isnan(ys)
    return float(np.trapezoid(ys[ok], xs[ok]) / (xs[ok][-1] - xs[ok][0])) if ok.sum() > 1 else np.nan


def paired_bootstrap(a, b, B=2000, seed=0):
    rng = np.random.default_rng(seed)
    d = a - b
    n = len(d)
    bs = np.array([d[rng.integers(0, n, n)].mean() for _ in range(B)])
    p = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
    return float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), float(max(p, 1.0 / B))


def holm(pvals):
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    run = 0.0
    for r, i in enumerate(order):
        run = max(run, (len(p) - r) * p[i])
        adj[i] = min(1.0, run)
    return adj


# --------------------------------------------------------------------------- 5. certification
def certify_gate(score_cal, loss_cal, alpha, method="crc", delta=0.1):
    """Largest t such that autonomy {score >= t} keeps the Autonomous Overrule Rate <= alpha.

    loss_cal_i = 1 - p_h(yhat_i | x_i) in [0,1] is the share of item i's annotators that an autonomous
    decision would overrule; the per-item loss 1[score_i >= t] * loss_i is monotone in t.
      crc   : (n*R_hat + 1)/(n+1) <= alpha        -> E[test AOR] <= alpha   (Angelopoulos et al., 2024)
      rcps  : R_hat + sqrt(log(1/delta)/(2n)) <= alpha -> P(test AOR <= alpha) >= 1-delta (Bates et al., 2021)
      naive : R_hat <= alpha                        (no finite-sample correction; for comparison)
    Returns the threshold (np.inf = no autonomy)."""
    n = len(score_cal)
    order = np.argsort(-score_cal)                      # admit items from the most confident downward
    s = score_cal[order]
    R = np.cumsum(loss_cal[order]) / n                  # risk when the top-j items are autonomous
    if method == "crc":
        ok = (n * R + 1.0) / (n + 1.0) <= alpha
    elif method == "rcps":
        ok = R + np.sqrt(np.log(1.0 / delta) / (2 * n)) <= alpha
    else:
        ok = R <= alpha
    # R is non-decreasing in j, so the feasible set is a prefix; respect ties in the score
    if not ok[0]:
        return np.inf
    j = int(np.where(ok)[0].max())
    t = s[j]
    if j + 1 < n and s[j + 1] == t:                     # a tie would admit infeasible items: step back
        below = np.where(s > t)[0]
        return s[below.max()] if len(below) else np.inf
    return float(t)
