"""
Master experiment runner for "How many humans does a decision need?" (IPM v2).
Runs all 4 experimental suites:
  Suite 1: Empirical Held-out Annotator Agreement (HAA) vs Theoretical Panel Value
  Suite 2: Pareto Frontiers of System Legitimacy vs Review Budget (LAJ vs All Baselines)
  Suite 3: Demographic Disparity & Overrule Equity (HS-Brexit & ArMIS)
  Suite 4: Distribution-Free Conformal Risk Certification of Autonomous Overrule Rate
Generates Markdown tables, CSVs, and publication figures in outputs_v2/.
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from data import load, DATASETS
from embeddings import get_embeddings
from core import (
    empirical_panel_haa, machine_haa, SoftEnsemble, HardModel, fit_ridge_contestation,
    ensemble_summaries, panel_values_second_order, policy_threshold, policy_dcs3,
    policy_laj, policy_entropy_panel, evaluate, pareto_frontier, legit_at_budget,
    area_under_frontier, paired_bootstrap, holm, certify_gate
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs_v2"
TABLES_DIR = OUT_DIR / "tables"
FIGS_DIR = OUT_DIR / "figures"

TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGS_DIR.mkdir(parents=True, exist_ok=True)

def run_study():
    print("=" * 80)
    print("   STARTING IPM v2 EXPERIMENTAL SUITE: LEGITIMACY-AWARE JURY ALLOCATION   ")
    print("=" * 80)
    
    suite1_rows = []
    frontier_rows = []
    budget_comparison_rows = []
    bootstrap_rows = []
    disparity_rows = []
    conformal_rows = []
    
    all_frontiers = {}
    
    for ds in DATASETS:
        print(f"\n>>> Processing Benchmark: {ds} <<<")
        df, V, P, K = load(ds)
        
        # Splits
        tr_m = (df.split == "train").values
        va_m = (df.split == "val").values
        te_m = (df.split == "test").values
        
        V_tr, V_va, V_te = V[tr_m], V[va_m], V[te_m]
        P_tr, P_va, P_te = P[tr_m], P[va_m], P[te_m]
        
        plurality_te = df.loc[te_m, "plurality"].values
        contested_te = df.loc[te_m, "contested"].values
        groups_te = np.array(df.loc[te_m, "groups"].tolist())
        
        M = V.shape[1]
        valid_ks = list(range(1, M)) # k in {1, ..., M-1}
        max_panel_k = M - 1
        
        # Load aligned dense multilingual embeddings
        X_tr, X_va, X_te = get_embeddings(ds, df)
        print(f"  Data ready: Train={len(X_tr)}, Val={len(X_va)}, Test={len(X_te)} | M={M}, K={K}")
        
        # Compute exact empirical Held-Out Annotator Agreement (HAA) for every k on Test set
        HAA_te = {}
        for k in valid_ks:
            val, ok = empirical_panel_haa(V_te, K, k)
            HAA_te[k] = val
            suite1_rows.append({
                "Dataset": ds, "Panel_Size_k": k, "Max_Available_M": M,
                "Empirical_HAA": float(np.nanmean(val)),
                "HAA_on_Contested": float(np.nanmean(val[contested_te == 1])),
                "HAA_on_Consensus": float(np.nanmean(val[contested_te == 0]))
            })
            
        # 1. Fit Soft Ensemble (Second-order distribution estimator)
        print("  Fitting Soft-Label Bootstrap Ensemble (B=8)...")
        ensemble = SoftEnsemble(B=8, seed=42)
        ensemble.fit(X_tr, P_tr, X_va, P_va, K)
        
        Pm_va = ensemble.member_probs(X_va)
        Pm_te = ensemble.member_probs(X_te)
        
        summ_va = ensemble_summaries(Pm_va, M)
        summ_te = ensemble_summaries(Pm_te, M)
        
        # Machine HAA on test set
        m_haa_te = machine_haa(V_te, summ_te["yhat"])
        suite1_rows.append({
            "Dataset": ds, "Panel_Size_k": 0, "Max_Available_M": M,
            "Empirical_HAA": float(m_haa_te.mean()),
            "HAA_on_Contested": float(m_haa_te[contested_te == 1].mean()),
            "HAA_on_Consensus": float(m_haa_te[contested_te == 0].mean())
        })
        
        # Theoretical panel values V_k(x)
        Vk_va = panel_values_second_order(Pm_va, valid_ks)
        Vk_te = panel_values_second_order(Pm_te, valid_ks)
        
        # 2. Fit Hard Baseline Model (Plurality + Temperature Scaling)
        print("  Fitting Hard Plurality Baseline (Standard MSP)...")
        hard_model = HardModel()
        hard_model.fit(X_tr, df.loc[tr_m, "plurality"].values, X_va, df.loc[va_m, "plurality"].values, K, seed=42)
        
        hard_probs_va = hard_model.probs(X_va)
        hard_probs_te = hard_model.probs(X_te)
        hard_msp_te = hard_probs_te.max(1)
        hard_yhat_te = hard_probs_te.argmax(1)
        
        # 3. Fit Auxiliary Contestation Regressor (DCS-MT baseline)
        print("  Fitting Auxiliary Ridge Contestation Head (DCS-MT)...")
        ridge_cont = fit_ridge_contestation(X_tr, df.loc[tr_m, "h_norm"].values)
        cont_pred_te = np.clip(ridge_cont.predict(X_te), 0.0, 1.0)
        
        # -------------------------------------------------------------------
        # SUITE 2: PARETO FRONTIER SWEEP (BUDGET vs LEGITIMACY)
        # -------------------------------------------------------------------
        print("  Generating Pareto Frontiers across all decision policies...")
        
        # Policy 1: Traditional MSP thresholding (defer to single reviewer k=1)
        pts_msp = []
        for t in np.linspace(0.3, 0.999, 100):
            acts = policy_threshold(hard_msp_te, t, k_defer=1)
            ev = evaluate(acts, hard_yhat_te, P_te, HAA_te, plurality_te, contested_te)
            pts_msp.append((ev["budget"], ev["legitimacy"], ev))
        front_msp = pareto_frontier(pts_msp)
        
        # Policy 2: MSP deferral to maximum panel (k=max_panel_k)
        pts_msp_panel = []
        for t in np.linspace(0.3, 0.999, 100):
            acts = policy_threshold(hard_msp_te, t, k_defer=max_panel_k)
            ev = evaluate(acts, hard_yhat_te, P_te, HAA_te, plurality_te, contested_te)
            pts_msp_panel.append((ev["budget"], ev["legitimacy"], ev))
        front_msp_panel = pareto_frontier(pts_msp_panel)
        
        # Policy 3: Authors' Previous DCS-MT (Fixed 3-tier heuristic)
        pts_dcs = []
        for tc in np.linspace(0.5, 0.95, 15):
            for th in np.linspace(0.1, 0.6, 15):
                acts = policy_dcs3(hard_msp_te, cont_pred_te, tc, th, k_panel=max_panel_k)
                ev = evaluate(acts, hard_yhat_te, P_te, HAA_te, plurality_te, contested_te)
                pts_dcs.append((ev["budget"], ev["legitimacy"], ev))
        front_dcs = pareto_frontier(pts_dcs)
        
        # Policy 4: Entropy Disagreement Panel (Aleatoric uncertainty routing)
        pts_ent = []
        for ta in np.linspace(0.5, 0.95, 15):
            for te in np.linspace(0.1, 0.7, 15):
                acts = policy_entropy_panel(summ_te["V0"], summ_te["aleatoric"], ta, te, k_panel=max_panel_k)
                ev = evaluate(acts, summ_te["yhat"], P_te, HAA_te, plurality_te, contested_te)
                pts_ent.append((ev["budget"], ev["legitimacy"], ev))
        front_ent = pareto_frontier(pts_ent)
        
        # Policy 5: PROPOSED Legitimacy-Aware Jury (LAJ) Rule
        pts_laj = []
        mu_grid = np.logspace(-4, 0.3, 200)
        for mu in mu_grid:
            acts = policy_laj(summ_te["V0"], Vk_te, mu=mu)
            ev = evaluate(acts, summ_te["yhat"], P_te, HAA_te, plurality_te, contested_te)
            pts_laj.append((ev["budget"], ev["legitimacy"], ev))
        front_laj = pareto_frontier(pts_laj)
        
        all_frontiers[ds] = {
            "MSP": front_msp, "MSP_Panel": front_msp_panel,
            "DCS_MT": front_dcs, "Entropy_Panel": front_ent, "Proposed_LAJ": front_laj
        }
        
        # Compute Area Under Pareto Frontier (AUPF) up to B_max = 1.0 reviews/post
        aupf_msp = area_under_frontier(front_msp, Bmax=1.0)
        aupf_panel = area_under_frontier(front_msp_panel, Bmax=1.0)
        aupf_dcs = area_under_frontier(front_dcs, Bmax=1.0)
        aupf_ent = area_under_frontier(front_ent, Bmax=1.0)
        aupf_laj = area_under_frontier(front_laj, Bmax=1.0)
        
        frontier_rows.append({
            "Dataset": ds,
            "AUPF_MSP": aupf_msp, "AUPF_MSP_Panel": aupf_panel,
            "AUPF_DCS_MT": aupf_dcs, "AUPF_Entropy_Panel": aupf_ent,
            "AUPF_Proposed_LAJ": aupf_laj,
            "Gain_over_MSP": aupf_laj - aupf_msp,
            "Gain_over_DCS": aupf_laj - aupf_dcs
        })
        
        # Pointwise comparisons at matched budgets B in {0.2, 0.5, 0.8, 1.0}
        for b_target in [0.2, 0.5, 0.8, 1.0]:
            r_msp = legit_at_budget(front_msp, b_target)
            r_dcs = legit_at_budget(front_dcs, b_target)
            r_laj = legit_at_budget(front_laj, b_target)
            
            if r_msp and r_laj:
                leg_msp = r_msp[1]
                leg_laj = r_laj[1]
                leg_dcs = r_dcs[1] if r_dcs else np.nan
                
                budget_comparison_rows.append({
                    "Dataset": ds, "Budget_Constraint": b_target,
                    "Legitimacy_MSP": leg_msp, "Legitimacy_DCS_MT": leg_dcs,
                    "Legitimacy_Proposed_LAJ": leg_laj,
                    "Absolute_Gain": leg_laj - leg_msp,
                    "Rel_Error_Reduction": ( (1.0 - leg_msp) - (1.0 - leg_laj) ) / (1.0 - leg_msp)
                })
                
                # Paired bootstrap test at B = 0.5
                if b_target == 0.5:
                    item_laj = r_laj[2]["per_item"]
                    item_msp = r_msp[2]["per_item"]
                    diff, ci_l, ci_u, p_val = paired_bootstrap(item_laj, item_msp, B=2000, seed=42)
                    bootstrap_rows.append({
                        "Dataset": ds, "Budget": 0.5, "Mean_Difference": diff,
                        "CI_95_Lower": ci_l, "CI_95_Upper": ci_u, "Raw_p_val": p_val
                    })
                    
        # -------------------------------------------------------------------
        # SUITE 3: DEMOGRAPHIC DISPARITY AUDIT (HS-BREXIT & ARMIS)
        # -------------------------------------------------------------------
        if ds in ["HS-Brexit", "ArMIS"]:
            print(f"  Auditing demographic group disparity for {ds}...")
            unique_groups = sorted(set(groups_te.reshape(-1)))
            
            for b_eval in [0.2, 0.5, 0.8]:
                r_m = legit_at_budget(front_msp, b_eval)
                r_l = legit_at_budget(front_laj, b_eval)
                
                if r_m and r_l:
                    acts_msp = np.where(hard_msp_te >= r_m[2]["coverage"], 0, 1) # approx
                    acts_laj = r_l[2]["coverage"]
                    
                    # For each group, compute Overrule Rate = mean( 1[auto] * (1 - p_group) )
                    for grp in unique_groups:
                        # evaluate agreement strictly against annotators of grp
                        haa_m_grp = machine_haa(V_te, hard_yhat_te, G=groups_te, group=grp)
                        haa_l_grp = machine_haa(V_te, summ_te["yhat"], G=groups_te, group=grp)
                        
                        auto_m = (hard_msp_te >= np.percentile(hard_msp_te, (1.0 - r_m[2]["coverage"])*100))
                        
                        overrule_msp = (auto_m * (1.0 - haa_m_grp)).mean()
                        overrule_laj = ((summ_te["V0"] >= np.percentile(summ_te["V0"], (1.0 - r_l[2]["coverage"])*100)) * (1.0 - haa_l_grp)).mean()
                        
                        disparity_rows.append({
                            "Dataset": ds, "Budget": b_eval, "Group": grp,
                            "Autonomous_Overrule_MSP": float(overrule_msp),
                            "Autonomous_Overrule_LAJ": float(overrule_laj),
                            "Disparity_Mitigation": float(overrule_msp - overrule_laj)
                        })

        # -------------------------------------------------------------------
        # SUITE 4: CONFORMAL RISK CERTIFICATION (AUTONOMOUS OVERRULE RATE)
        # -------------------------------------------------------------------
        print("  Evaluating distribution-free Conformal Risk Control...")
        loss_va = 1.0 - P_va[np.arange(len(summ_va["yhat"])), summ_va["yhat"]]
        loss_te = 1.0 - P_te[np.arange(len(summ_te["yhat"])), summ_te["yhat"]]
        
        score_va = summ_va["V0"]
        score_te = summ_te["V0"]
        
        for alpha in [0.05, 0.10, 0.15, 0.20]:
            t_crc = certify_gate(score_va, loss_va, alpha=alpha, method="crc")
            t_rcps = certify_gate(score_va, loss_va, alpha=alpha, method="rcps", delta=0.1)
            t_naive = certify_gate(score_va, loss_va, alpha=alpha, method="naive")
            
            # Evaluate empirical test risk
            def test_risk(t):
                if np.isinf(t): return 0.0, 0.0
                acc = (score_te >= t)
                r = float((acc * loss_te).mean())
                cov = float(acc.mean())
                return r, cov
                
            r_crc, cov_crc = test_risk(t_crc)
            r_rcps, cov_rcps = test_risk(t_rcps)
            r_naive, cov_naive = test_risk(t_naive)
            
            conformal_rows.append({
                "Dataset": ds, "Target_Alpha": alpha,
                "Empirical_AOR_CRC": r_crc, "Coverage_CRC": cov_crc,
                "Empirical_AOR_RCPS": r_rcps, "Coverage_RCPS": cov_rcps,
                "Empirical_AOR_Naive": r_naive, "Coverage_Naive": cov_naive,
                "Guaranteed": (r_crc <= alpha)
            })

    # Save Tables
    df_s1 = pd.DataFrame(suite1_rows)
    df_front = pd.DataFrame(frontier_rows)
    df_budget = pd.DataFrame(budget_comparison_rows)
    df_boot = pd.DataFrame(bootstrap_rows)
    
    # Adjust p-values via Holm
    df_boot["Holm_p_val"] = holm(df_boot["Raw_p_val"].values)
    
    df_disp = pd.DataFrame(disparity_rows)
    df_conf = pd.DataFrame(conformal_rows)
    
    df_s1.to_csv(TABLES_DIR / "table1_heldout_annotator_agreement.csv", index=False)
    df_front.to_csv(TABLES_DIR / "table2_aupf_frontier_summary.csv", index=False)
    df_budget.to_csv(TABLES_DIR / "table3_matched_budget_legitimacy.csv", index=False)
    df_boot.to_csv(TABLES_DIR / "table4_statistical_significance_bootstrap.csv", index=False)
    if not df_disp.empty:
        df_disp.to_csv(TABLES_DIR / "table5_demographic_disparity_audit.csv", index=False)
    df_conf.to_csv(TABLES_DIR / "table6_conformal_risk_certification.csv", index=False)
    
    # Render High-Resolution Figures
    print("\nRendering Publication Figures (300 DPI)...")
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    
    # FIG 1: 4-Panel Pareto Frontiers (Legitimacy vs Budget)
    fig, axes = plt.subplots(2, 2, figsize=(14, 11), dpi=300)
    for idx, ds in enumerate(DATASETS):
        ax = axes[idx // 2, idx % 2]
        fr = all_frontiers[ds]
        
        # Plot curves
        for name, col, ls, lab in [
            ("MSP", "#7f8c8d", "--", "Baseline: MSP (Single Reviewer)"),
            ("MSP_Panel", "#95a5a6", ":", "Baseline: MSP (Fixed Panel)"),
            ("DCS_MT", "#e67e22", "-.", "Prev: DCS-MT (3-Tier Heuristic)"),
            ("Entropy_Panel", "#8e44ad", "-.", "Baseline: Disagreement Panel"),
            ("Proposed_LAJ", "#2980b9", "-", "PROPOSED: Legitimacy-Aware Jury (LAJ)")
        ]:
            b_vals = [p[0] for p in fr[name]]
            l_vals = [p[1] for p in fr[name]]
            ax.plot(b_vals, l_vals, color=col, linestyle=ls, linewidth=2.2 if "LAJ" in name else 1.6, label=lab)
            
        ax.set_title(f"{ds} (M={6 if 'Brexit' in ds else (5 if 'MD' in ds else 3)})", fontsize=13, fontweight="bold")
        ax.set_xlabel("Review Budget (Average Human Annotators per Post)", fontsize=11)
        ax.set_ylabel("Held-Out Decision Legitimacy (HAA)", fontsize=11)
        ax.set_xlim(-0.02, 1.5)
        ax.legend(fontsize=9, loc="lower right")
        
    plt.tight_layout()
    plt.savefig(FIGS_DIR / "fig1_pareto_frontiers_four_benchmarks.png", dpi=300, bbox_inches="tight")
    plt.close()
    
    # FIG 2: Demographic Disparity on HS-Brexit & ArMIS
    if not df_disp.empty:
        fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
        
        # Subplot 1: HS-Brexit Target vs Control
        sub_hb = df_disp[(df_disp.Dataset == "HS-Brexit") & (df_disp.Budget == 0.5)]
        if not sub_hb.empty:
            sns.barplot(data=sub_hb, x="Group", y="Autonomous_Overrule_MSP", color="#e74c3c", ax=axes[0], alpha=0.7, label="Baseline MSP")
            sns.barplot(data=sub_hb, x="Group", y="Autonomous_Overrule_LAJ", color="#27ae60", ax=axes[0], alpha=0.85, label="Proposed LAJ")
            axes[0].set_title("HS-Brexit: Autonomous Overrule of Minorities (B=0.5)", fontsize=11, fontweight="bold")
            axes[0].set_ylabel("Autonomous Overrule Rate (Fraction Silenced)", fontsize=10)
            axes[0].set_xlabel("Annotator Sociodemographic Group", fontsize=10)
            axes[0].legend(loc="upper right")
            
        # Subplot 2: ArMIS Gender / Ideology
        sub_ar = df_disp[(df_disp.Dataset == "ArMIS") & (df_disp.Budget == 0.5)]
        if not sub_ar.empty:
            sns.barplot(data=sub_ar, x="Group", y="Autonomous_Overrule_MSP", color="#e74c3c", ax=axes[1], alpha=0.7, label="Baseline MSP")
            sns.barplot(data=sub_ar, x="Group", y="Autonomous_Overrule_LAJ", color="#27ae60", ax=axes[1], alpha=0.85, label="Proposed LAJ")
            axes[1].set_title("ArMIS: Misogyny Moderation Overrule Disparity (B=0.5)", fontsize=11, fontweight="bold")
            axes[1].set_ylabel("Autonomous Overrule Rate (Fraction Silenced)", fontsize=10)
            axes[1].set_xlabel("Annotator Sociodemographic Profile", fontsize=10)
            axes[1].legend(loc="upper right")
            
        plt.tight_layout()
        plt.savefig(FIGS_DIR / "fig2_demographic_disparity_mitigation.png", dpi=300, bbox_inches="tight")
        plt.close()
        
    print("\n" + "="*80)
    print("   ALL EXPERIMENTS COMPLETED SUCCESSFULLY! OUTPUTS PERSISTED IN outputs_v2/   ")
    print("=" * 80)
    print(df_front.to_string())

if __name__ == "__main__":
    run_study()
