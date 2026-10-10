"""p2_07 - Behavioral change-point / velocity triggers.

Deployable early-warning trigger catalog. Thresholds are chosen on TRAIN ONLY
(precision-maximizing grid search with alert-volume bounds); holdout
evaluation reads precision, alert volume, and a lead-time proxy on the
untouched TEST set.

Snapshot honesty: the table is a single as-of snapshot, so "velocity" is
honestly limited to the snapshot's trajectory proxies (usage_decay_90d, DAU
decay signals). True change-point detection needs the longitudinal data
contract specified in shadow_pilot.md. Lead time is proxied by
days_to_renewal at firing (stated limitation, not measured lead time).
"""
import numpy as np
import pandas as pd

from prep import (load_table, feature_frame, make_split, fit_reference,
                  reference_ranking, business_metrics, save_json, SEED, ARR,
                  LABEL, FORBIDDEN)

K_FRAC = 0.10


def imp_median(a):
    return np.where(np.isnan(a), np.nanmedian(a), a)


def train_threshold(y, x, direction, lo=0.03, hi=0.40):
    """Pick threshold maximizing train precision with alert rate in [lo, hi].
    direction: 'le' (fire when x <= t) or 'ge'."""
    x = np.asarray(x, float)
    grid = np.unique(np.nanquantile(x, np.linspace(0.02, 0.98, 49)))
    best, best_t = -1.0, None
    for t in grid:
        fire = (x <= t) if direction == "le" else (x >= t)
        rate = fire.mean()
        if rate < lo or rate > hi or fire.sum() < 10:
            continue
        prec = y[fire].mean()
        if prec > best:
            best, best_t = prec, t
    return best_t, best


def main():
    df = load_table()
    split = make_split(df)
    ytr, yte = split["y_train"], split["y_test"]
    arr_tr, arr_te = split["arr_train"], split["arr_test"]
    dtr = split["Xn_train"]
    dte = split["Xn_test"]
    n_test = split["n_test"]
    K = int(round(K_FRAC * n_test))

    # ---- p2_01 reference (probabilities reused for EV columns; triggers
    #      emit no probabilities - stated in memo) ----
    ref = fit_reference(split)

    # ---- trigger definitions: thresholds chosen on TRAIN ONLY ----
    decay_tr = imp_median(dtr["usage_decay_90d"].to_numpy())
    decay_te = np.where(np.isnan(dte["usage_decay_90d"].to_numpy()),
                        np.nanmedian(dtr["usage_decay_90d"].to_numpy()),
                        dte["usage_decay_90d"].to_numpy())
    aur_tr = imp_median(dtr["active_user_ratio"].to_numpy())
    aur_te = np.where(np.isnan(dte["active_user_ratio"].to_numpy()),
                      np.nanmedian(dtr["active_user_ratio"].to_numpy()),
                      dte["active_user_ratio"].to_numpy())
    champ_tr = imp_median(dtr["champion_logins_30d"].to_numpy())
    champ_te = np.where(np.isnan(dte["champion_logins_30d"].to_numpy()),
                        np.nanmedian(dtr["champion_logins_30d"].to_numpy()),
                        dte["champion_logins_30d"].to_numpy())
    esc_tr = dtr["escalations_12m"].to_numpy()
    esc_te = dte["escalations_12m"].to_numpy()
    p1_tr = dtr["p1_tickets_12m"].to_numpy()
    p1_te = dte["p1_tickets_12m"].to_numpy()
    down_tr = dtr["downgraded_12m"].to_numpy()
    down_te = dte["downgraded_12m"].to_numpy()
    dark_tr = dtr["has_valid_survey"].to_numpy() == 0
    dark_te = dte["has_valid_survey"].to_numpy() == 0
    dtr_days = dtr["days_to_renewal"].to_numpy()
    dte_days = dte["days_to_renewal"].to_numpy()
    bh_tr = dtr["behavioral_health"].to_numpy()
    bh_te = dte["behavioral_health"].to_numpy()
    bh_q25 = np.nanquantile(bh_tr, 0.25)

    t_decay, _ = train_threshold(ytr, decay_tr, "le")
    t_aur, _ = train_threshold(ytr, aur_tr, "le")
    t_champ, _ = train_threshold(ytr, champ_tr, "le")
    t_dark_decay, _ = train_threshold(ytr[dark_tr], decay_tr[dark_tr], "le",
                                      lo=0.05, hi=0.60)
    t_esc, _ = train_threshold(ytr, esc_tr, "ge")

    triggers = [
        {"id": "T1", "name": "Usage-decay cliff",
         "rule": "usage_decay_90d <= {t:.2f} (90-day lookback)",
         "thr": t_decay, "owner": "CSM", "sla": "Outreach within 2 business days",
         "fire_tr": decay_tr <= t_decay, "fire_te": decay_te <= t_decay},
        {"id": "T2", "name": "Active-user-ratio cliff",
         "rule": "active_user_ratio <= {t:.2f}",
         "thr": t_aur, "owner": "CSM", "sla": "Outreach within 2 business days",
         "fire_tr": aur_tr <= t_aur, "fire_te": aur_te <= t_aur},
        {"id": "T3", "name": "Champion login gap",
         "rule": "champion_logins_30d <= {t:.0f} (30-day lookback)",
         "thr": t_champ, "owner": "CSM", "sla": "Champion check-in within 5 business days",
         "fire_tr": champ_tr <= t_champ, "fire_te": champ_te <= t_champ},
        {"id": "T4", "name": "Escalation burst",
         "rule": "escalations_12m >= {t:.0f}",
         "thr": t_esc, "owner": "Support lead", "sla": "Exec review within 24 hours",
         "fire_tr": esc_tr >= t_esc, "fire_te": esc_te >= t_esc},
        {"id": "T5", "name": "P1 pain",
         "rule": "p1_tickets_12m >= 1",
         "thr": 1, "owner": "Support lead", "sla": "Post-incident review within 5 business days",
         "fire_tr": p1_tr >= 1, "fire_te": p1_te >= 1},
        {"id": "T6", "name": "Downgrade event",
         "rule": "downgraded_12m == 1",
         "thr": 1, "owner": "Account executive", "sla": "Save conversation within 3 business days",
         "fire_tr": down_tr == 1, "fire_te": down_te == 1},
        {"id": "T7", "name": "Dark account + decay",
         "rule": "has_valid_survey == 0 AND usage_decay_90d <= {t:.2f}",
         "thr": t_dark_decay, "owner": "CSM",
         "sla": "Discovery call within 5 business days",
         "fire_tr": dark_tr & (decay_tr <= t_dark_decay),
         "fire_te": dark_te & (decay_te <= t_dark_decay)},
        {"id": "T8", "name": "Renewal pressure + low health",
         "rule": "days_to_renewal <= 90 AND behavioral_health <= train-Q25",
         "thr": np.nan, "owner": "Account executive",
         "sla": "Renewal plan within 5 business days",
         "fire_tr": (dtr_days <= 90) & (bh_tr <= bh_q25),
         "fire_te": (dte_days <= 90) & (bh_te <= bh_q25)},
    ]

    catalog_rows, union_tr = [], np.zeros(len(ytr), bool)
    union_te = np.zeros(len(yte), bool)
    for tg in triggers:
        ftr, fte = tg["fire_tr"], tg["fire_te"]
        union_tr |= ftr
        union_te |= fte
        alert_tr = ftr.mean()
        n_fire = int(fte.sum())
        prec = float(yte[fte].mean()) if n_fire else float("nan")
        lead = float(np.median(dte_days[fte])) if n_fire else float("nan")
        rule_txt = tg["rule"].format(t=tg["thr"]) if "{t" in tg["rule"] else tg["rule"]
        catalog_rows.append({
            "trigger": tg["id"], "name": tg["name"], "rule": rule_txt,
            "lookback": "as stated in rule",
            "threshold": (None if np.isnan(tg["thr"]) else round(float(tg["thr"]), 3)),
            "owner": tg["owner"], "sla": tg["sla"],
            "train_alert_rate": round(float(alert_tr), 4),
            "train_precision": round(float(ytr[ftr].mean()), 4),
            "test_alerts_n": n_fire,
            "test_alert_rate": round(float(n_fire / len(yte)), 4),
            "test_precision": (round(prec, 4) if n_fire else None),
            "leadtime_proxy_median_days_to_renewal": (round(lead, 1) if n_fire else None),
        })
    catalog = pd.DataFrame(catalog_rows)
    catalog.to_csv("trigger_catalog.csv", index=False)
    print(catalog.to_string(index=False))

    # ---- trigger-routed worklist: fired accounts ranked by calibrated EV ----
    p, arr = ref["p_cal"], arr_te
    fired_idx = np.where(union_te)[0]
    # fired accounts first, ranked by calibrated p x ARR desc; unfired never
    # enter the worklist. If fewer than K fire, the worklist is the full
    # fired set (n_flagged < K, disclosed in metrics).
    order_trig = fired_idx[np.argsort(-(p[fired_idx] * arr[fired_idx]))]
    # sensitivity at 5% / 15%
    K5, K15 = int(round(0.05 * n_test)), int(round(0.15 * n_test))

    work = business_metrics(order_trig, K, p, arr, yte)
    sens5 = business_metrics(order_trig, K5, p, arr, yte)
    sens15 = business_metrics(order_trig, K15, p, arr, yte)

    # ---- p2_01 reference head-to-head (same split) ----
    ref_order = reference_ranking(ref, split)
    ref_work = business_metrics(ref_order, K, p, arr, yte)

    metrics = {
        "n_rows": int(df.shape[0]),
        "n_features": int(len(feature_frame(df)[0].columns)
                          + len(feature_frame(df)[1].columns)),
        "churn_rate": float(df[LABEL].mean()),
        "test_churn_rate": float(yte.mean()),
        "n_test": int(n_test),
        "seed": SEED,
        "split": "stratified_80_20",
        # triggers emit no probabilities; threshold-free metrics reuse the
        # p2_01 reference (stated in approach.md)
        "auc": ref["auc"], "pr_auc": ref["pr_auc"],
        "brier_before": ref["brier_before"], "brier_after": ref["brier_after"],
        "calibration_method": ref["calibration_method"],
        "probabilities_source": "p2_01_reference_reused",
        "worklist": work,
        "sensitivity": {"5pct": sens5, "15pct": sens15},
        "incumbent_head_to_head": {
            "comparison_baseline": "p2_01_reference",
            "baseline_actual_churners_caught": ref_work["actual_churners_caught"],
            "baseline_expected_arr_at_risk": ref_work["expected_arr_at_risk"],
            "baseline_actual_churned_arr_captured":
                ref_work["actual_churned_arr_captured"],
            "self_actual_churners_caught": work["actual_churners_caught"],
            "self_expected_arr_at_risk": work["expected_arr_at_risk"],
            "self_actual_churned_arr_captured":
                work["actual_churned_arr_captured"],
        },
        "trigger_union_test_alerts": int(union_te.sum()),
        "trigger_union_test_alert_rate": float(union_te.mean()),
        "run_command": "bash run.sh",
        "notes": (
            "p2_07 triggers emit rules, not probabilities: auc/pr_auc/brier and "
            "expected_arr_at_risk reuse the p2_01 reference calibrator (same "
            "split, seed 42). Thresholds chosen on train only via "
            "precision-maximizing grid with alert-rate bounds [3%, 40%]. "
            "Lead time is proxied by days_to_renewal at firing (snapshot "
            "limitation); true change-point lead time needs the longitudinal "
            "contract in shadow_pilot.md. No tuning or threshold selection on "
            "test. n_test=400, K=40."
        ),
    }
    save_json(metrics, "metrics.json")
    print(f"union fired on test: {union_te.sum()}/{len(yte)}; "
          f"K={K}; worklist caught {work['actual_churners_caught']} churners")


if __name__ == "__main__":
    main()
