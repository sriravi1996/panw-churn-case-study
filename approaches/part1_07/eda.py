"""
part1_07 eda.py — exploratory analysis.

Required: top ordered items; highest-value customer/product relationships.
Angle-specific: STATED (survey) vs REVEALED (behavioral) account health —
  does the survey agree with what the account actually does, and what does
  the fraud filter + nonresponse bias change?

Writes outputs/eda_findings.json.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if pd.isna(o):
        return None
    return str(o)


mt = pd.read_csv(ROOT / "modeling_table.csv")
subs = pd.read_csv(ROOT / "cleaned" / "subscriptions.csv")
products = pd.read_csv(ROOT / "raw" / "products.csv")
pname = dict(zip(products["product_id"], products["product_name"]))
surveys_raw = pd.read_csv(ROOT / "raw" / "surveys.csv")
surveys_valid = pd.read_csv(ROOT / "cleaned" / "surveys_valid.csv")
surveys_q = pd.read_csv(ROOT / "cleaned" / "surveys_quarantined.csv")

findings = {}

# ------------------------------------------------ top ordered items
item_counts = subs.groupby("product_id").agg(
    orders=("order_item_id", "nunique"), arr_usd=("arr_usd", "sum"),
    accounts=("account_id", "nunique")).reset_index()
item_counts["product_name"] = item_counts["product_id"].map(pname)
by_orders = item_counts.sort_values("orders", ascending=False).head(5)
by_arr = item_counts.sort_values("arr_usd", ascending=False).head(5)
findings["top_ordered_items_by_order_count"] = [
    {"product": r["product_name"], "orders": int(r["orders"]),
     "accounts": int(r["accounts"])} for _, r in by_orders.iterrows()]
findings["top_ordered_items_by_arr"] = [
    {"product": r["product_name"], "arr_usd_mm": round(float(r["arr_usd"]) / 1e6, 2),
     "accounts": int(r["accounts"])} for _, r in by_arr.iterrows()]

# ------------------------------------------------ highest-value relationships
acct_arr = mt.sort_values("total_arr_usd", ascending=False).head(10)
findings["top_accounts_by_arr"] = [
    {"account_id": r["account_id"], "total_arr_usd": int(r["total_arr_usd"]),
     "n_products": int(r["n_products"]), "hero_share": float(r["hero_share_of_arr"]),
     "churned": int(r["churned"])}
    for _, r in acct_arr.iterrows()]
top_pairs = subs.sort_values("arr_usd", ascending=False).head(10)
findings["top_account_product_pairs"] = [
    {"account_id": r["account_id"], "product": pname[r["product_id"]],
     "arr_usd": int(r["arr_usd"])} for _, r in top_pairs.iterrows()]
hero_arr = float(mt["hero_arr_usd"].sum())
total_arr = float(mt["total_arr_usd"].sum())
top10_share = float(mt.sort_values("total_arr_usd", ascending=False)
                    .head(200)["total_arr_usd"].sum() / total_arr)
findings["value_concentration"] = {
    "hero_product_share_of_total_arr": round(hero_arr / total_arr, 3),
    "top_10pct_accounts_share_of_arr": round(top10_share, 3),
    "mean_products_per_account": round(float(mt["n_products"].mean()), 2),
}

# ------------------------------------------------ stated vs revealed health
valid_nps = mt["valid_nps_mean"]
behav = mt["behavioral_health"]
findings["stated_vs_revealed"] = {
    "corr_valid_nps_vs_behavioral_health": round(float(valid_nps.corr(behav)), 3),
    "corr_naive_nps_vs_behavioral_health": round(
        float(mt["naive_nps_mean"].corr(behav)), 3),
    "corr_valid_nps_vs_churned": round(float(valid_nps.corr(mt["churned"])), 3),
    "corr_behavioral_health_vs_churned": round(float(behav.corr(mt["churned"])), 3),
}
# "inflated stated health": stated health far ABOVE revealed behavior
# (top gap decile) — courtesy bias makes these accounts look safer than
# their usage suggests. Compare against the bottom gap decile.
mt["gap_decile"] = pd.qcut(mt["stated_vs_revealed_gap"], 10,
                           labels=False, duplicates="drop")
gap_churn = mt.groupby("gap_decile")["churned"].mean()
top_gap = mt[mt["gap_decile"] == mt["gap_decile"].max()]
bot_gap = mt[mt["gap_decile"] == mt["gap_decile"].min()]
findings["stated_vs_revealed_gap"] = {
    "definition": "gap = z(valid_nps) - z(behavioral_health); top decile = "
                  "stated health far above revealed behavior",
    "top_gap_decile_churn": round(float(gap_churn.iloc[-1]), 3),
    "bottom_gap_decile_churn": round(float(gap_churn.iloc[0]), 3),
    "top_gap_decile_mean_nps": round(float(top_gap["valid_nps_mean"].mean()), 2),
    "top_gap_decile_mean_active_user_ratio": round(
        float(top_gap["active_user_ratio"].mean()), 3),
    "bottom_gap_decile_mean_nps": round(float(bot_gap["valid_nps_mean"].mean()), 2),
    "bottom_gap_decile_mean_active_user_ratio": round(
        float(bot_gap["active_user_ratio"].mean()), 3),
}
# "dark accounts": no valid survey response AND usage falling off —
# the nonresponse-bias blind spot
dark = mt[(mt["has_valid_survey"] == 0) & (mt["usage_decay_90d"] < 0.80)]
rest = mt[~mt.index.isin(dark.index)]
findings["dark_accounts"] = {
    "definition": "no valid survey response AND usage_decay_90d < 0.80",
    "n_accounts": int(len(dark)),
    "pct_of_base": round(len(dark) / len(mt), 3),
    "churn_rate": round(float(dark["churned"].mean()), 3),
    "churn_rate_rest": round(float(rest["churned"].mean()), 3),
}

# ------------------------------------------------ nonresponse bias
respondents = mt[mt["has_valid_survey"] == 1]
nonresp = mt[mt["has_valid_survey"] == 0]
findings["nonresponse_bias"] = {
    "response_rate": round(float(mt["has_valid_survey"].mean()), 3),
    "churn_rate_respondents": round(float(respondents["churned"].mean()), 3),
    "churn_rate_nonrespondents": round(float(nonresp["churned"].mean()), 3),
    "mean_behavioral_health_respondents": round(float(respondents["behavioral_health"].mean()), 3),
    "mean_behavioral_health_nonrespondents": round(float(nonresp["behavioral_health"].mean()), 3),
}
resp_by_seg = mt.groupby("segment")["has_valid_survey"].mean().round(3).to_dict()
findings["response_rate_by_segment"] = {str(k): float(v) for k, v in resp_by_seg.items()}

# ------------------------------------------------ fraud-filter impact
findings["fraud_filter_impact"] = {
    "raw_responses": int(len(surveys_raw)),
    "valid_responses": int(len(surveys_valid)),
    "quarantine_rate": round(1 - len(surveys_valid) / len(surveys_raw), 3),
    "naive_mean_nps": round(float(surveys_raw["nps_score"].mean()), 2),
    "valid_mean_nps": round(float(surveys_valid["nps_score"].mean()), 2),
    "naive_promoter_pct": round(float((surveys_raw["nps_score"] >= 9).mean()), 3),
    "valid_promoter_pct": round(float((surveys_valid["nps_score"] >= 9).mean()), 3),
    "quarantined_promoter_pct": round(float((surveys_q["nps_score"] >= 9).mean()), 3),
    "quarantined_pct_scoring_10": round(float((surveys_q["nps_score"] == 10).mean()), 3),
}

# ------------------------------------------------ fraud pattern decomposition
# which of the four flags actually drives the promoter inflation seen above?
flag_cols = ["flag_straightliner", "flag_speeder", "flag_duplicate", "flag_copypasta"]
flag_names = {"flag_straightliner": "straightliner", "flag_speeder": "speeder",
              "flag_duplicate": "duplicate", "flag_copypasta": "copy_paste_farm"}
profiles = {}
for f in flag_cols:
    g = surveys_q[surveys_q[f] == 1]
    profiles[flag_names[f]] = {
        "n_responses": int(len(g)),
        "mean_nps": round(float(g["nps_score"].mean()), 2),
        "pct_scoring_10": round(float((g["nps_score"] == 10).mean()), 3),
        "median_duration_seconds": int(g["duration_seconds"].median()),
    }
flags_int = surveys_q[flag_cols].astype(int)
profiles["straightliner_speeder_overlap"] = int(
    ((flags_int["flag_straightliner"] == 1) & (flags_int["flag_speeder"] == 1)).sum())
profiles["responses_with_multiple_flags"] = int((flags_int.sum(axis=1) > 1).sum())
profiles["valid_pct_scoring_10_baseline"] = round(
    float((surveys_valid["nps_score"] == 10).mean()), 3)
findings["fraud_pattern_profiles"] = profiles

with open(OUT / "eda_findings.json", "w") as f:
    json.dump(findings, f, indent=2, default=_json_default)
print(json.dumps(findings, indent=2, default=_json_default))
