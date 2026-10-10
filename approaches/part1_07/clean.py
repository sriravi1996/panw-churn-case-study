"""
part1_07 clean.py — cleaning / dedup / entity resolution.

Standard tables: industry label normalization, mixed date parsing,
subscription dedup + product_id case fix.

Survey table (the angle): response-quality filtering pipeline.
  Flags per response:
    - straightliner : std of the 5 CSAT grid items == 0  (grid fraud)
    - speeder       : duration_seconds < 60s              (speeding)
    - duplicate     : same respondent_email submitted >1x (keep earliest)
    - copypasta     : open_text repeated across >3 distinct accounts
  A response is VALID only if none of the flags fire.
  Duplicates/copy-paste are ENTITY RESOLUTION problems: same respondent,
  same canned text -> resolved to a single canonical record.

Outputs:
  cleaned/accounts.csv, subscriptions.csv, telemetry.csv, support.csv,
  engagement.csv (standard cleaning)
  cleaned/surveys_valid.csv        (quality-passing responses)
  cleaned/surveys_quarantined.csv  (flagged responses + flag columns)
  outputs/data_quality_report.json (short DQ report)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW, CLEANED, OUT = ROOT / "raw", ROOT / "cleaned", ROOT / "outputs"
CLEANED.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

GRID = ["csat_onboarding", "csat_support", "csat_value",
        "csat_documentation", "csat_renewal_intent"]


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

report = {"tables": {}, "survey_quality": {}}

# ------------------------------------------------------------ accounts
# keep_default_na=False so the dirty "N/A" date tokens survive the read
accounts = pd.read_csv(RAW / "accounts.csv", keep_default_na=False)
ind_map = {
    "technology": "technology", "tech": "technology", "software": "technology",
    "financial services": "financial services", "finserv": "financial services",
    "banking": "financial services",
    "healthcare": "healthcare", "retail": "retail",
    "manufacturing": "manufacturing", "mfg": "manufacturing",
    "energy": "energy",
}
accounts["industry_clean"] = (accounts["industry"].astype(str).str.strip().str.lower()
                              .map(ind_map))
unmapped_ind = int(accounts["industry_clean"].isna().sum())
accounts["contract_start_date_parsed"] = pd.to_datetime(
    accounts["contract_start_date"], errors="coerce", format="mixed")
unparsed_dates = int(accounts["contract_start_date_parsed"].isna().sum()
                     - accounts["contract_start_date"].isin(["N/A", "TBD"]).sum())
report["tables"]["accounts"] = {
    "rows": len(accounts),
    "industry_labels_before": int(accounts["industry"].nunique()),
    "industry_labels_after": int(accounts["industry_clean"].nunique()),
    "industry_unmapped": unmapped_ind,
    "date_parse_failures_beyond_known_tokens": unparsed_dates,
}
accounts.to_csv(CLEANED / "accounts.csv", index=False)

# ------------------------------------------------------------ subscriptions
subs = pd.read_csv(RAW / "subscriptions.csv")
n_raw_subs = len(subs)
n_case_fixed = int((subs["product_id"] != subs["product_id"].str.upper()).sum())
subs["product_id"] = subs["product_id"].str.upper()  # ER: case variants -> canonical
# dedup on business key (account_id, product_id) keeping first order_item_id
n_dupes = int(subs.duplicated(subset=["account_id", "product_id"], keep="first").sum())
subs = subs.drop_duplicates(subset=["account_id", "product_id"], keep="first")
report["tables"]["subscriptions"] = {
    "rows_raw": n_raw_subs, "rows_clean": len(subs),
    "duplicate_order_rows_removed": n_dupes,
    "product_id_case_variants_fixed": n_case_fixed,
}
subs.to_csv(CLEANED / "subscriptions.csv", index=False)

# ------------------------------------------------------------ telemetry / support / engagement
for name in ["telemetry", "support", "engagement"]:
    df = pd.read_csv(RAW / f"{name}.csv")
    report["tables"][name] = {"rows": len(df),
                              "missing_cells": int(df.isna().sum().sum())}
    df.to_csv(CLEANED / f"{name}.csv", index=False)

# ------------------------------------------------------------ surveys: quality pipeline
surveys = pd.read_csv(RAW / "surveys.csv")
n_raw = len(surveys)

# 1) straight-lining: zero variance across the 5-item grid AND rushed.
# (Honest satisficers can also pick all-3s, so require a fast completion
# to call it fraud rather than laziness.)
grid_std = surveys[GRID].std(axis=1)
surveys["flag_straightliner"] = (grid_std == 0) & (surveys["duration_seconds"] < 180)

# 2) speeders: < 60s for a 5-grid + NPS + open-text instrument
surveys["flag_speeder"] = surveys["duration_seconds"] < 60

# 3) duplicate submissions: same respondent_email, keep earliest submitted_date
surveys["submitted_date"] = pd.to_datetime(surveys["submitted_date"])
surveys = surveys.sort_values("submitted_date")
dup_mask = surveys.duplicated(subset=["respondent_email"], keep="first")
surveys["flag_duplicate"] = dup_mask

# 4) copy-paste open text (fraud-farm signature): the IDENTICAL long text
# submitted across >3 distinct accounts inside a tight burst window.
# Honest template reuse spreads over the full 90-day field period, so the
# burst condition separates farm batches from coincidental wording.
txt = surveys.groupby("open_text").agg(
    n_accounts=("account_id", "nunique"),
    date_min=("submitted_date", "min"),
    date_max=("submitted_date", "max"),
)
txt["date_range_days"] = (txt["date_max"] - txt["date_min"]).dt.days
canned = set(txt[(txt["n_accounts"] > 3) & (txt["date_range_days"] <= 7)
                & (txt.index.str.len() > 20)].index)
surveys["flag_copypasta"] = surveys["open_text"].isin(canned)

flag_cols = ["flag_straightliner", "flag_speeder", "flag_duplicate", "flag_copypasta"]
surveys["is_valid"] = ~surveys[flag_cols].any(axis=1)

valid = surveys[surveys["is_valid"]].copy()
quarantined = surveys[~surveys["is_valid"]].copy()

# account-level aggregates: VALID-ONLY vs NAIVE (all responses)
def _agg(df):
    df = df.copy()
    df["csat_row_mean"] = df[GRID].mean(axis=1)
    g = df.groupby("account_id")
    return pd.DataFrame({
        "nps_mean": g["nps_score"].mean(),
        "csat_mean": g["csat_row_mean"].mean(),
        "n_responses": g.size(),
    })

agg_valid = _agg(valid).rename(columns={"nps_mean": "valid_nps_mean",
                                        "csat_mean": "valid_csat_mean",
                                        "n_responses": "n_valid_responses"})
agg_naive = _agg(surveys).rename(columns={"nps_mean": "naive_nps_mean",
                                          "csat_mean": "naive_csat_mean",
                                          "n_responses": "n_all_responses"})
survey_acct = agg_naive.join(agg_valid, how="left")
survey_acct["validity_rate"] = (survey_acct["n_valid_responses"]
                                / survey_acct["n_all_responses"]).fillna(0)
survey_acct.to_csv(CLEANED / "survey_account_aggregates.csv")

valid.drop(columns=flag_cols + ["is_valid"]).to_csv(
    CLEANED / "surveys_valid.csv", index=False)
quarantined.to_csv(CLEANED / "surveys_quarantined.csv", index=False)

nps_naive = surveys["nps_score"].mean()
nps_valid = valid["nps_score"].mean()
report["survey_quality"] = {
    "responses_raw": n_raw,
    "responses_valid": int(valid["is_valid"].sum()),
    "responses_quarantined": int((~surveys["is_valid"]).sum()),
    "flag_counts": {c: int(surveys[c].sum()) for c in flag_cols},
    "accounts_with_any_response": int(surveys["account_id"].nunique()),
    "accounts_with_valid_response": int(valid["account_id"].nunique()),
    "naive_mean_nps_all_responses": round(float(nps_naive), 2),
    "valid_mean_nps": round(float(nps_valid), 2),
    "fraud_filter_nps_shift": round(float(nps_naive - nps_valid), 2),
    "median_validity_rate_per_account": round(float(survey_acct["validity_rate"].median()), 3),
}

with open(OUT / "data_quality_report.json", "w") as f:
    json.dump(report, f, indent=2, default=_json_default)

print(json.dumps(report, indent=2, default=_json_default))
