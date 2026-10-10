"""Shared Phase 2 pipeline primitives for Builder C (p2_07 / p2_08 / p2_09).

Winner table: approaches/part1_07/modeling_table.csv (2000 x 47).
Label: `churned` = hero cancellation/non-renewal within 90 days of 2026-10-01,
base rate 11.85% (canonical 90-day full-account churn, spec 1.6 case 1).
Dollar currency: `total_arr_usd` (map-designated, p50 ~$789K).

Contract enforced here:
- stratified 80/20 train/test, seed 42, test touched ONCE per pipeline run
- all preprocessing statistics fit on TRAIN only
- forbidden columns dropped in code BEFORE any modeling (see FORBIDDEN)
- calibration: CalibratedClassifierCV(cv=5, isotonic) fit on train only
- K = 10% of test rows (absolute), thresholds chosen on train only
"""
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

SEED = 42
TABLE_PATH = ("/home/hatch/workspace/goals/senior-staff-data-scientist-job-search"
              "/files/panw-case-study/approaches/part1_07/modeling_table.csv")
LABEL = "churned"
ARR = "total_arr_usd"

# (column, spec-1.5 leakage class / reason)
FORBIDDEN = [
    ("account_id",      "class 8: identifier, never a feature"),
    ("p_churn_latent",  "class 1: latent ground truth (corr ~0.55 with label)"),
    ("clv_12m",         "auxiliary target only (task-forbidden; truth-derived)"),
    ("n_order_items",   "class 6: exact duplicate of n_products (corr 1.0)"),
    ("max_item_arr",    "class 6: exact duplicate of top_product_arr_usd (corr 1.0)"),
    ("z_valid_nps",     "class 6: exact duplicate of valid_nps_mean (corr 1.0)"),
    ("product_id",      "class 6: constant (PRD-01 for all rows)"),
    ("naive_nps_mean",  "survey-trust distractor: untrusted self-report"),
    ("naive_csat_mean", "survey-trust distractor: untrusted self-report"),
    ("n_all_responses", "trust machinery, not a model feature"),
    ("n_valid_responses","trust machinery, not a model feature"),
    ("validity_rate",   "trust machinery, not a model feature"),
]

CATEGORICALS = ["industry_clean", "region", "segment", "top_product_name"]

NUMERICS = [
    "employee_count", "tenure_years", "days_to_renewal", "total_arr_usd",
    "n_products", "hero_arr_usd", "hero_share_of_arr", "top_product_arr_usd",
    "licensed_users", "active_user_ratio", "usage_decay_90d", "feature_depth",
    "api_calls_weekly", "champion_logins_30d", "tickets_opened_12m",
    "ticket_resolution_rate", "p1_tickets_12m", "escalations_12m",
    "webinars_watched", "content_downloads", "sales_calls_12m",
    "qbr_attended_12m", "downgraded_12m", "expansion_revenue_pct",
    "valid_nps_mean", "valid_csat_mean", "behavioral_health",
    "stated_vs_revealed_gap", "has_valid_survey",
]


def load_table():
    df = pd.read_csv(TABLE_PATH)
    assert df.shape[0] == 2000 and df.shape[1] == 47, df.shape
    assert df["account_id"].nunique() == df.shape[0], "account_id not unique"
    assert set(df[LABEL].unique()) <= {0, 1}
    rate = df[LABEL].mean()
    assert 0.10 <= rate <= 0.18, f"base rate {rate} outside 10-18% band"
    return df


def feature_frame(df):
    """Drop forbidden columns, return (X_num, X_cat) with train-fitted stats
    handled by the caller. Categorical frame left as strings here."""
    for col, _reason in FORBIDDEN:
        assert col in df.columns, f"expected forbidden col {col} present"
    X = df.drop(columns=[c for c, _ in FORBIDDEN] + [LABEL])
    return X[NUMERICS].copy(), X[CATEGORICALS].copy()


class Preprocessor:
    """Train-only statistics: numeric median imputation, categorical mode,
    ordinal encoding with unknown -> -1."""

    def fit(self, Xn, Xc):
        self.medians_ = Xn.median()
        self.cat_maps_ = {}
        for c in Xc.columns:
            cats = sorted(Xc[c].dropna().unique().tolist())
            self.cat_maps_[c] = {v: i for i, v in enumerate(cats)}
        return self

    def transform(self, Xn, Xc):
        Xn2 = Xn.fillna(self.medians_)
        out = [Xn2.reset_index(drop=True)]
        for c in Xc.columns:
            m = self.cat_maps_[c]
            out.append(Xc[c].map(lambda v: m.get(v, -1)).astype(int)
                       .rename(c).reset_index(drop=True))
        return pd.concat(out, axis=1)

    def fit_transform(self, Xn, Xc):
        return self.fit(Xn, Xc).transform(Xn, Xc)


def make_split(df):
    Xn, Xc = feature_frame(df)
    y = df[LABEL].to_numpy()
    arr = df[ARR].to_numpy()
    idx = np.arange(len(df))
    tr, te = train_test_split(idx, test_size=0.20, random_state=SEED,
                              stratify=y)
    return {
        "train_idx": tr, "test_idx": te,
        "y_train": y[tr], "y_test": y[te],
        "arr_train": arr[tr], "arr_test": arr[te],
        "Xn_train": Xn.iloc[tr], "Xc_train": Xc.iloc[tr],
        "Xn_test": Xn.iloc[te], "Xc_test": Xc.iloc[te],
        "n_test": len(te),
    }


def reference_model():
    """p2_01 reference: HGBT(class_weight='balanced') + isotonic calibration."""
    base = HistGradientBoostingClassifier(class_weight="balanced",
                                         random_state=SEED)
    return CalibratedClassifierCV(base, method="isotonic", cv=5)


def fit_reference(split):
    """Fit reference on train; return dict with train-fit objects and
    test-set readouts (test touched once, for final numbers)."""
    prep = Preprocessor()
    Xtr = prep.fit_transform(split["Xn_train"], split["Xc_train"])
    Xte = prep.transform(split["Xn_test"], split["Xc_test"])
    cal = reference_model().fit(Xtr, split["y_train"])
    # uncalibrated base for Brier-before: refit plain HGBT on full train
    base = HistGradientBoostingClassifier(class_weight="balanced",
                                         random_state=SEED).fit(Xtr,
                                                                 split["y_train"])
    p_uncal = base.predict_proba(Xte)[:, 1]
    p_cal = cal.predict_proba(Xte)[:, 1]
    y = split["y_test"]
    return {
        "prep": prep, "cal": cal,
        "p_cal": p_cal, "p_uncal": p_uncal,
        "auc": float(roc_auc_score(y, p_cal)),
        "pr_auc": float(average_precision_score(y, p_cal)),
        "brier_before": float(brier_score_loss(y, p_uncal)),
        "brier_after": float(brier_score_loss(y, p_cal)),
        "calibration_method": "isotonic",
    }


def business_metrics(order, K, p, arr, y):
    """order: indices (into test arrays) sorted best-first by the worklist rule.
    Returns the spec-2.2 column set at fixed capacity K."""
    sel = order[:K]
    caught = y[sel]
    n_caught = int(caught.sum())
    n_flag = len(sel)
    return {
        "capacity": int(K),
        "n_flagged": int(n_flag),
        "actual_churners_caught": n_caught,
        "precision_at_k": float(n_caught / n_flag) if n_flag else 0.0,
        "recall_at_k": float(n_caught / y.sum()) if y.sum() else 0.0,
        "expected_arr_at_risk": float(np.sum(p[sel] * arr[sel])),
        "actual_churned_arr_captured": float(np.sum(arr[sel][caught == 1])),
    }


def reference_ranking(ref, split):
    """p2_01 EV ranking: calibrated p_churn x arr_portfolio, descending."""
    ev = ref["p_cal"] * split["arr_test"]
    return np.argsort(-ev)


def save_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
    print(f"wrote {path}")
