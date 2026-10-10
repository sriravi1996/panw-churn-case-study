"""Leakage self-audit (spec 1.4 rule 7). Run: python3 leakage_audit.py
Asserts every forbidden class in PHASE2_SPEC.md 1.5 is excluded from the
feature matrix, then prints PASS. Exit non-zero on any violation."""
import sys
import pandas as pd

sys.path.insert(0, ".")
from prep import load_table, feature_frame, FORBIDDEN, LABEL, ARR


def main():
    df = load_table()
    Xn, Xc = feature_frame(df)
    feats = set(Xn.columns) | set(Xc.columns)

    # 1. every explicitly forbidden column is gone from the feature matrix
    for col, reason in FORBIDDEN:
        assert col not in feats, f"LEAK: forbidden column in features: {col}"

    # 2. class 1 latent ground truth (task-named)
    assert "p_churn_latent" not in feats
    # 3. class 2 post-window dollar outcomes (not on this table; assert anyway)
    for c in ("churned_arr", "pct_arr_churned"):
        assert c not in feats, f"LEAK: {c}"
    # 4. class 3 near-label proxies
    assert "hero_held" not in df.columns, "hero_held unexpectedly present"
    # 5. class 4 family aggregates incl. own outcome (not on this table)
    for c in ("family_churned_any", "family_churn_rate", "parent_is_churned"):
        assert c not in feats, f"LEAK: {c}"
    # 6. class 6 duplicates/constants
    assert "n_order_items" not in feats and "max_item_arr" not in feats
    assert "z_valid_nps" not in feats and "product_id" not in feats
    # 7. class 8 identifiers / PII-adjacent
    assert "account_id" not in feats
    for c in ("company_pseudonym", "contact_email_masked", "account_domain"):
        assert c not in feats, f"LEAK: {c}"
    # 8. dates enter only through as-of-derived features (no date cols as feats)
    date_like = [c for c in feats if "date" in c.lower()]
    assert date_like == [], f"LEAK: date columns as features: {date_like}"
    assert "days_to_renewal" in feats  # legitimate as-of-derived feature
    # 9. auxiliary target is not a feature
    assert "clv_12m" not in feats
    # 10. label itself is not a feature
    assert LABEL not in feats
    # 11. ARR currency present and sane
    assert ARR in feats and (df[ARR] > 0).all()

    n_dropped = len(FORBIDDEN)
    print(f"LEAKAGE AUDIT PASS: {len(feats)} features clean; "
          f"{n_dropped} forbidden columns excluded before modeling.")
    print("Dropped:")
    for col, reason in FORBIDDEN:
        print(f"  - {col}: {reason}")


if __name__ == "__main__":
    main()
