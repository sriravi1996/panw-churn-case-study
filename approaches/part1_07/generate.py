"""
part1_07 SURVEY-AUGMENTED — synthetic raw source tables.

Angle: core B2B account/subscription/usage tables PLUS a synthetic NPS/CSAT
survey table with realistic NONRESPONSE BIAS (at-risk accounts go silent) and
survey FRAUD patterns (straight-lining, speeders, duplicates, copy-paste open
text) that require response-quality filtering before any stated-vs-revealed
health analysis.

Hero product: PRD-01 "SentinelShield" (cloud workload protection).
Portfolio: 20 products across 6 security categories.

Raw tables -> raw/:
  accounts.csv, products.csv, subscriptions.csv (order items),
  telemetry.csv, support.csv, engagement.csv, surveys.csv, labels.csv

Deterministic: single seed (707) via numpy Generator only.
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 707
N_ACCOUNTS = 2000
SCORING_DATE = pd.Timestamp("2026-10-01")
BASE_LOGIT = -0.18  # tuned to land churn in the 12-18% band

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
RAW.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- products
product_names = [
    "SentinelShield", "ThreatScope", "NetBarrier", "IdentityVault", "DataCrypt",
    "PostureLens", "EndpointSentry", "SIEMFlow", "CloudTrail Guard", "ZeroTrust Mesh",
    "VulnRadar", "PhishBlock", "SecretsKeeper", "LogHarbor", "APIFortress",
    "ContainerArmor", "DNSWatch", "MailDefend", "AccessReview", "BreachSim",
]
categories = [
    "Cloud Security", "Threat Intel", "Network Security", "Identity", "Data Security",
    "Cloud Security", "Endpoint", "SOC", "Cloud Security", "Network Security",
    "Vulnerability Mgmt", "Email Security", "Identity", "SOC", "API Security",
    "Cloud Security", "Network Security", "Email Security", "Identity", "Breach & Attack Sim",
]
tiers = ["Enterprise"] * 12 + ["Business"] * 8
products = pd.DataFrame({
    "product_id": [f"PRD-{i:02d}" for i in range(1, 21)],
    "product_name": product_names,
    "category": categories,
    "price_tier": tiers,
})
TARGET_PID = "PRD-01"

# ---------------------------------------------------------------- accounts
industries_canonical = ["technology", "financial services", "healthcare",
                        "retail", "manufacturing", "energy"]
industry_probs = [0.30, 0.22, 0.15, 0.13, 0.12, 0.08]
industry_true = rng.choice(industries_canonical, size=N_ACCOUNTS, p=industry_probs)
variants = {
    "technology": ["technology", "Technology", "TECH", "technology ", "Software"],
    "financial services": ["financial services", "Financial Services", "FinServ",
                           "banking", "financial services "],
    "healthcare": ["healthcare", "Healthcare", "HEALTHCARE", "healthcare "],
    "retail": ["retail", "Retail", "RETAIL "],
    "manufacturing": ["manufacturing", "Manufacturing", "MFG", "manufacturing "],
    "energy": ["energy", "Energy", "ENERGY"],
}
industry = np.array([rng.choice(variants[c]) for c in industry_true])
regions = rng.choice(["NAMER", "EMEA", "APAC", "LATAM"], size=N_ACCOUNTS,
                     p=[0.50, 0.25, 0.17, 0.08])
employees = np.clip(rng.lognormal(mean=np.log(6000), sigma=1.2, size=N_ACCOUNTS).astype(int),
                    250, 150000)
tenure_years = np.clip(rng.normal(4.0, 2.3, N_ACCOUNTS), 0.3, 12).round(1)
segment = np.where(employees >= 10000, "Enterprise",
                   np.where(employees >= 1000, "Mid-Market", "SMB"))

start_dates = SCORING_DATE - pd.to_timedelta((tenure_years * 365.25).astype(int), unit="D")
date_strs = []
for d in start_dates:
    r = rng.random()
    if r < 0.88:
        date_strs.append(d.strftime("%Y-%m-%d"))
    elif r < 0.96:
        date_strs.append(d.strftime("%m/%d/%Y"))
    elif r < 0.98:
        date_strs.append("N/A")
    else:
        date_strs.append("TBD")

days_to_renewal = rng.integers(0, 365, N_ACCOUNTS)
renewal_dates = SCORING_DATE + pd.to_timedelta(days_to_renewal, unit="D")

account_ids = [f"ACC-{i:05d}" for i in range(1, N_ACCOUNTS + 1)]
accounts = pd.DataFrame({
    "account_id": account_ids,
    "industry": industry,
    "region": regions,
    "employee_count": employees,
    "segment": segment,
    "tenure_years": tenure_years,
    "contract_start_date": date_strs,
    "renewal_date": renewal_dates.strftime("%Y-%m-%d"),
    "days_to_renewal": days_to_renewal,
})

# ---------------------------------------------------------------- subscriptions (order items)
affinity = {"PRD-06": 0.30, "PRD-02": 0.20, "PRD-03": 0.18, "PRD-04": 0.14,
            "PRD-07": 0.12, "PRD-08": 0.10, "PRD-16": 0.10, "PRD-05": 0.08}
_zero_inflate = rng.random(N_ACCOUNTS) < 0.30
_lam = 0.7 + 0.22 * tenure_years + 0.25 * np.log10(employees)
n_other = np.where(_zero_inflate, 0, np.clip(rng.poisson(_lam), 0, 8))

sub_rows, order_seq = [], 1
for i, acc in enumerate(account_ids):
    arr_target = np.clip(rng.lognormal(mean=np.log(380_000), sigma=0.9),
                         35_000, 7_500_000)
    sub_rows.append((f"ORD-{order_seq:06d}", acc, TARGET_PID,
                     round(float(arr_target), -3), "active")); order_seq += 1
    k = int(n_other[i])
    if k:
        pids = list(affinity.keys())
        probs = np.array([affinity[p] for p in pids]); probs /= probs.sum()
        for pid in rng.choice(pids, size=min(k, len(pids)), replace=False, p=probs):
            arr = np.clip(rng.lognormal(mean=np.log(160_000), sigma=0.9),
                          15_000, 2_500_000)
            sub_rows.append((f"ORD-{order_seq:06d}", acc, pid,
                             round(float(arr), -3), "active")); order_seq += 1

subs = pd.DataFrame(sub_rows, columns=["order_item_id", "account_id",
                                       "product_id", "arr_usd", "status"])
# dirty: ~1.5% duplicate order rows + product_id case inconsistency
dup_idx = rng.choice(len(subs), size=int(0.015 * len(subs)), replace=False)
subs = pd.concat([subs, subs.iloc[dup_idx]], ignore_index=True)
case_mask = rng.random(len(subs)) < 0.05
subs.loc[case_mask, "product_id"] = subs.loc[case_mask, "product_id"].str.lower()
subs = subs.sample(frac=1.0, random_state=SEED).reset_index(drop=True)

is_target = subs["product_id"].str.upper() == TARGET_PID
arr_target_map = (subs[is_target].drop_duplicates("account_id")
                  .set_index("account_id")["arr_usd"])
arr_target = accounts["account_id"].map(arr_target_map).values
other_products_owned = (subs[~is_target].drop_duplicates(["account_id", "product_id"])
                        .groupby("account_id").size())
other_products_owned = (accounts["account_id"].map(other_products_owned)
                        .fillna(0).astype(int).values)

# ---------------------------------------------------------------- telemetry (hero product)
n_tel = N_ACCOUNTS
licensed_users = np.clip((employees * rng.uniform(0.02, 0.30, n_tel)).astype(int),
                         10, 50000)
active_user_ratio = np.clip(rng.beta(2.0, 3.0, n_tel), 0.02, 1.0).round(3)
usage_decay_90d = np.clip(rng.normal(1.0, 0.25, n_tel), 0.2, 2.0).round(3)
feature_depth = np.clip(rng.binomial(12, np.clip(active_user_ratio * 0.85 + 0.08, 0, 1),
                                    n_tel), 0, 12)
api_calls_weekly = rng.lognormal(mean=np.log(35000), sigma=1.3, size=n_tel).astype(int)
champion_logins_30d = rng.poisson(np.clip(6 * active_user_ratio + 1, 0.5, 12),
                                  n_tel).astype(float)
telemetry = pd.DataFrame({
    "account_id": account_ids, "product_id": TARGET_PID,
    "licensed_users": licensed_users, "active_user_ratio": active_user_ratio,
    "usage_decay_90d": usage_decay_90d, "feature_depth": feature_depth,
    "api_calls_weekly": api_calls_weekly, "champion_logins_30d": champion_logins_30d,
})

# ---------------------------------------------------------------- support
tickets_opened_12m = rng.poisson(np.clip(13 - 0.7 * tenure_years, 3, 20), N_ACCOUNTS)
ticket_resolution_rate = np.clip(rng.beta(7, 2.2, N_ACCOUNTS), 0.25, 1.0).round(3)
p1_tickets_12m = rng.poisson(np.clip(1.5 - 1.1 * ticket_resolution_rate, 0.05, 3),
                             N_ACCOUNTS)
escalations_12m = rng.poisson(np.clip(3.0 - 2.0 * ticket_resolution_rate, 0.1, 4),
                              N_ACCOUNTS)
support = pd.DataFrame({
    "account_id": account_ids, "tickets_opened_12m": tickets_opened_12m,
    "ticket_resolution_rate": ticket_resolution_rate,
    "p1_tickets_12m": p1_tickets_12m, "escalations_12m": escalations_12m,
})

# ---------------------------------------------------------------- engagement (marketing + sales + relationship)
webinars_watched = rng.poisson(4.0, N_ACCOUNTS).astype(float)
content_downloads = rng.poisson(8.0, N_ACCOUNTS).astype(float)
sales_calls_12m = rng.poisson(13, N_ACCOUNTS)
qbr_attended_12m = rng.poisson(1.7, N_ACCOUNTS)
downgraded_12m = (rng.random(N_ACCOUNTS)
                  < np.clip(0.05 + 0.09 * (other_products_owned == 0), 0, 0.4)).astype(int)
expansion_revenue_pct = np.clip(
    rng.normal(7 + 3 * (other_products_owned > 3) - 11 * downgraded_12m, 17, N_ACCOUNTS),
    -45, 80).round(1)
engagement = pd.DataFrame({
    "account_id": account_ids, "webinars_watched": webinars_watched,
    "content_downloads": content_downloads, "sales_calls_12m": sales_calls_12m,
    "qbr_attended_12m": qbr_attended_12m, "downgraded_12m": downgraded_12m,
    "expansion_revenue_pct": expansion_revenue_pct,
})

# MCAR missingness on a couple of non-survey fields
for frame, col, frac in [(engagement, "webinars_watched", 0.04),
                         (engagement, "content_downloads", 0.03),
                         (telemetry, "champion_logins_30d", 0.03)]:
    frame.loc[rng.random(len(frame)) < frac, col] = np.nan

# ---------------------------------------------------------------- latent satisfaction (drives BOTH surveys and churn)
# sat: 0-10 latent satisfaction; low sat -> silent nonresponse AND churn
sat = np.clip(rng.normal(6.8, 1.8, N_ACCOUNTS)
              - 1.6 * (usage_decay_90d < 0.70)
              - 1.2 * (ticket_resolution_rate < 0.65)
              + 0.8 * (other_products_owned >= 3), 0, 10).round(2)

# ---------------------------------------------------------------- surveys (the angle table)
roles = ["Security Engineer", "SOC Analyst", "CISO", "IT Manager", "DevOps Engineer"]
role_probs = [0.34, 0.26, 0.10, 0.18, 0.12]
grid_cols = ["csat_onboarding", "csat_support", "csat_value",
             "csat_documentation", "csat_renewal_intent"]

first = ["alex", "priya", "jordan", "maria", "chen", "sam", "fatima", "liam",
         "sofia", "raj", "emma", "diego", "ana", "kenji", "nora", "omar"]
last = ["patel", "garcia", "kim", "nguyen", "smith", "khan", "rossi", "muller",
        "tanaka", "silva", "ahmed", "dubey", "chen", "park", "ali", "kumar"]
open_pos = ["Great product, very happy with the support team.",
            "The platform just works. Onboarding was smooth.",
            "Solid value for money, our SOC relies on it daily.",
            "Excellent threat coverage and responsive support."]
open_neu = ["It's fine. Does what we need most of the time.",
            "Average experience, some rough edges in the UI.",
            "Works okay but reporting could be better."]
open_neg = ["Too many false positives, tuning took months.",
            "Support is slow and the product feels unfinished.",
            "Considering alternatives at renewal."]
canned_copypasta = ["Outstanding solution with world-class customer success!!!",
                    "Five stars, would definitely recommend to other CISOs."]

survey_rows, survey_seq = [], 1
resp_email_pool = {}
for i, acc in enumerate(account_ids):
    n_invites = rng.integers(1, 4)  # 1-3 invitations per account
    for _ in range(n_invites):
        # NONRESPONSE BIAS: at-risk (low sat) accounts go silent.
        # Steep satisfaction gradient -> respondents skew satisfied.
        p_resp = np.clip(0.02 + 0.075 * sat[i], 0.02, 0.75)
        if rng.random() > p_resp:
            continue
        role = rng.choice(roles, p=role_probs)
        # unique respondent email per response (survey_seq suffix); only the
        # injected duplicate-fraud below reuses an address
        email = (f"{rng.choice(first)}.{rng.choice(last)}"
                 f".{survey_seq:06d}@example.com")
        resp_email_pool.setdefault(acc, []).append(email)
        nps_score = int(np.clip(round(rng.normal(2.2 + 0.85 * sat[i], 1.6)), 0, 10))
        # COURTESY BIAS (not fraud — the filter must NOT catch this): ~12% of
        # respondents inflate NPS out of politeness while grid answers and
        # behavior tell the truer story.
        if rng.random() < 0.12:
            nps_score = min(10, nps_score + 2)
        grid = np.clip(np.round(rng.normal(1.2 + 0.42 * sat[i], 0.9, 5)), 1, 5).astype(int)
        if sat[i] >= 7:
            otext = rng.choice(open_pos)
        elif sat[i] >= 4:
            otext = rng.choice(open_neu)
        else:
            otext = rng.choice(open_neg)
        # duration: honest respondents take 2-8 min; lognormal
        duration = float(np.clip(rng.lognormal(mean=np.log(240), sigma=0.6), 40, 1800))
        submitted = SCORING_DATE - pd.to_timedelta(int(rng.integers(0, 90)), unit="D")
        survey_rows.append([f"SRV-{survey_seq:06d}", acc, email, role, "NPS",
                            nps_score, *grid, otext, duration,
                            submitted.strftime("%Y-%m-%d")])
        survey_seq += 1

surveys = pd.DataFrame(survey_rows, columns=[
    "survey_id", "account_id", "respondent_email", "respondent_role",
    "survey_type", "nps_score", *grid_cols, "open_text",
    "duration_seconds", "submitted_date"])

# ---- fraud injection ----
n = len(surveys)
# 1) straight-liners: 3% -> all grid answers identical
sl_idx = rng.choice(n, size=int(0.03 * n), replace=False)
for j in sl_idx:
    v = rng.choice([1, 5, 5, 3])  # extremes dominate
    surveys.loc[j, grid_cols] = v
    surveys.loc[j, "duration_seconds"] = float(rng.uniform(35, 90))
# 2) speeders: 4% -> implausibly fast
sp_idx = rng.choice(n, size=int(0.04 * n), replace=False)
surveys.loc[sp_idx, "duration_seconds"] = rng.uniform(12, 55, len(sp_idx)).round(1)
# 3) duplicate submissions: 1.5% -> same respondent submits twice
dup_pick = rng.choice(n, size=int(0.015 * n), replace=False)
dup_rows = surveys.iloc[dup_pick].copy()
dup_rows["survey_id"] = [f"SRV-{survey_seq + k:06d}" for k in range(len(dup_rows))]
dup_rows["submitted_date"] = (
    pd.to_datetime(dup_rows["submitted_date"]) + pd.to_timedelta(rng.integers(1, 3, len(dup_rows)), unit="D")
).dt.strftime("%Y-%m-%d")
survey_seq += len(dup_rows)
# 4) copy-paste open text: 2% -> canned text shared across accounts.
# Fraud signature: the farm submits in tight BURSTS (bot batch), so re-stamp
# these rows into 3-day burst windows per canned text.
cp_idx = rng.choice(surveys.index.difference(dup_pick), size=int(0.02 * n), replace=False)
cp_texts = rng.choice(canned_copypasta, len(cp_idx))
surveys.loc[cp_idx, "open_text"] = cp_texts
for k, canned in enumerate(canned_copypasta):
    kk = cp_idx[cp_texts == canned]
    burst_start = SCORING_DATE - pd.to_timedelta(int(rng.integers(45, 80)), unit="D")
    surveys.loc[kk, "submitted_date"] = (
        burst_start + pd.to_timedelta(rng.integers(0, 3, len(kk)), unit="D")
    ).strftime("%Y-%m-%d")

surveys = pd.concat([surveys, dup_rows], ignore_index=True)
surveys = surveys.sample(frac=1.0, random_state=SEED).reset_index(drop=True)

# ---------------------------------------------------------------- labels (latent churn + CLV)
tel = telemetry.set_index("account_id")
aur = telemetry["active_user_ratio"].values
decay = telemetry["usage_decay_90d"].values
champ = np.where(telemetry["champion_logins_30d"].isna(), 4.0,
                 telemetry["champion_logins_30d"].values)
rr = ticket_resolution_rate
logit = (
    BASE_LOGIT
    - 1.50 * (aur > 0.45) - 0.60 * aur
    - 0.85 * (decay < 0.70)
    - 1.10 * (rr > 0.80) - 0.50 * rr
    - 0.40 * (p1_tickets_12m == 0)
    + 1.00 * (other_products_owned == 0) - 0.10 * np.minimum(other_products_owned, 8)
    - 0.12 * tenure_years
    + 0.60 * (expansion_revenue_pct < 0) + 0.50 * downgraded_12m
    + 0.45 * (days_to_renewal < 90)
    - 0.19 * sat  # latent satisfaction protects against churn
    - 0.35 * (champ >= 8) - 0.30 * (qbr_attended_12m >= 2)
    + 1.30 * ((aur < 0.35) & (other_products_owned <= 1))
    + 1.00 * ((rr < 0.65) & (tenure_years < 2.0))
    + 0.70 * (tenure_years > 8)
    + rng.normal(0, 0.50, N_ACCOUNTS)
)
p_churn = 1 / (1 + np.exp(-logit))
churned = (rng.random(N_ACCOUNTS) < p_churn).astype(int)

clv_12m = np.clip(
    arr_target * (1 - p_churn)
    + arr_target * np.clip(expansion_revenue_pct, -50, 80) / 100 * 0.5
    + rng.normal(0, arr_target * 0.05), 0, None).round(0)
labels = pd.DataFrame({"account_id": account_ids, "churned": churned,
                       "clv_12m": clv_12m, "p_churn_latent": np.round(p_churn, 4)})

# ---------------------------------------------------------------- write
accounts.to_csv(RAW / "accounts.csv", index=False)
products.to_csv(RAW / "products.csv", index=False)
subs.to_csv(RAW / "subscriptions.csv", index=False)
telemetry.to_csv(RAW / "telemetry.csv", index=False)
support.to_csv(RAW / "support.csv", index=False)
engagement.to_csv(RAW / "engagement.csv", index=False)
surveys.to_csv(RAW / "surveys.csv", index=False)
labels.to_csv(RAW / "labels.csv", index=False)

if __name__ == "__main__":
    for name, f in [("accounts", accounts), ("products", products),
                    ("subscriptions", subs), ("telemetry", telemetry),
                    ("support", support), ("engagement", engagement),
                    ("surveys", surveys), ("labels", labels)]:
        print(f"raw/{name}.csv: {f.shape[0]} rows x {f.shape[1]} cols")
    print(f"Churn rate: {churned.mean():.3f} | Mean CLV: ${clv_12m.mean():,.0f} | "
          f"Survey response coverage: {surveys['account_id'].nunique()}/{N_ACCOUNTS} accounts")
