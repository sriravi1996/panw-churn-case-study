"""
part1_07 integrate.py — build the account-level modeling table.

Joins (all on account_id, left-join from the account spine):
  accounts (cleaned)            1:1 firmographics + contract
  subscriptions (cleaned)       1:N order items -> account aggregates
  telemetry (cleaned)           1:1 hero-product usage
  support / engagement (clean)  1:1 health + relationship signals
  survey_account_aggregates     1:1 stated-health (valid-only + naive)
  labels                        1:1 churned / clv_12m

Derived:
  stated_vs_revealed_gap = z(valid_nps) - z(behavioral_health),
  where behavioral_health blends usage + support signals.

Outputs: modeling_table.csv, outputs/integration_summary.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
CLEANED, OUT = ROOT / "cleaned", ROOT / "outputs"

TARGET_PID = "PRD-01"


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


accounts = pd.read_csv(CLEANED / "accounts.csv", keep_default_na=False)
subs = pd.read_csv(CLEANED / "subscriptions.csv")
telemetry = pd.read_csv(CLEANED / "telemetry.csv")
support = pd.read_csv(CLEANED / "support.csv")
engagement = pd.read_csv(CLEANED / "engagement.csv")
survey_acct = pd.read_csv(CLEANED / "survey_account_aggregates.csv")
labels = pd.read_csv(ROOT / "raw" / "labels.csv")
products = pd.read_csv(ROOT / "raw" / "products.csv")
pname = dict(zip(products["product_id"], products["product_name"]))

# ---- subscription aggregates (order items -> account grain)
is_target = subs["product_id"] == TARGET_PID
sub_agg = subs.groupby("account_id").agg(
    total_arr_usd=("arr_usd", "sum"),
    n_products=("product_id", "nunique"),
    n_order_items=("order_item_id", "nunique"),
    max_item_arr=("arr_usd", "max"),
)
hero_arr = subs[is_target].groupby("account_id")["arr_usd"].sum().rename("hero_arr_usd")
sub_agg = sub_agg.join(hero_arr)
sub_agg["hero_arr_usd"] = sub_agg["hero_arr_usd"].fillna(0)
sub_agg["hero_share_of_arr"] = (sub_agg["hero_arr_usd"] / sub_agg["total_arr_usd"]).round(4)
# top product per account (by ARR); stable sort so ties resolve in raw row order
top_prod = (subs.sort_values("arr_usd", ascending=False, kind="stable")
            .drop_duplicates("account_id").set_index("account_id"))
sub_agg["top_product_id"] = top_prod["product_id"]
sub_agg["top_product_name"] = sub_agg["top_product_id"].map(pname)
sub_agg["top_product_arr_usd"] = top_prod["arr_usd"]

# ---- assemble
mt = accounts[["account_id", "industry_clean", "region", "employee_count",
               "segment", "tenure_years", "days_to_renewal"]].copy()
for frame in [sub_agg, telemetry.set_index("account_id"),
              support.set_index("account_id"), engagement.set_index("account_id"),
              survey_acct.set_index("account_id"), labels.set_index("account_id")]:
    mt = mt.join(frame, on="account_id")

# ---- stated vs revealed health
for c in ["active_user_ratio", "usage_decay_90d", "ticket_resolution_rate"]:
    mt[f"z_{c}"] = (mt[c] - mt[c].mean()) / mt[c].std()
mt["behavioral_health"] = (0.4 * mt["z_active_user_ratio"]
                            + 0.3 * mt["z_usage_decay_90d"]
                            + 0.3 * mt["z_ticket_resolution_rate"])
mt["z_valid_nps"] = ((mt["valid_nps_mean"] - mt["valid_nps_mean"].mean())
                     / mt["valid_nps_mean"].std())
mt["stated_vs_revealed_gap"] = (mt["z_valid_nps"] - mt["behavioral_health"]).round(3)
mt["has_valid_survey"] = mt["n_valid_responses"].notna().astype(int)
mt["valid_nps_mean"] = mt["valid_nps_mean"].fillna(mt["valid_nps_mean"].median())
mt["validity_rate"] = mt["validity_rate"].fillna(0)
mt.drop(columns=[c for c in mt.columns if c.startswith("z_")
                 and c not in ("z_valid_nps",)], inplace=True)

mt.to_csv(ROOT / "modeling_table.csv", index=False)

summary = {
    "modeling_rows": int(len(mt)),
    "modeling_cols": int(mt.shape[1]),
    "accounts_with_hero_subscription": int((mt["hero_arr_usd"] > 0).sum()),
    "accounts_with_valid_survey": int(mt["has_valid_survey"].sum()),
    "accounts_missing_telemetry_champion": int(mt["champion_logins_30d"].isna().sum()),
    "join_keys_verified": bool(mt["account_id"].is_unique),
    "label_balance": {"churned": int(mt["churned"].sum()),
                      "retained": int((mt["churned"] == 0).sum())},
    "total_arr_usd_mm": round(float(mt["total_arr_usd"].sum()) / 1e6, 1),
    "median_stated_vs_revealed_gap": round(float(mt["stated_vs_revealed_gap"].median()), 3),
}
with open(OUT / "integration_summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=_json_default)
print(json.dumps(summary, indent=2, default=_json_default))
