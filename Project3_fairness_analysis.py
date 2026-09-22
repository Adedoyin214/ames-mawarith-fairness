"""
=============================================================
Mawārith Analytics — Project 3
Fairness Metrics in Islamic Inheritance Distribution
Gini Coefficient, Theil Index, Variance & Equity Analysis
=============================================================
Dataset     : 20 PCIED cases + 5,000 simulation records
Engine      : mawaarith_engine_v2 (Fiqh al-Mawārith)
Institute   : Elbaseety Institute® | Mawārith Analytics
Source Data : PCIED 2023 — Alhikma University, Ilorin
=============================================================
"""

import json
import math
import statistics as st
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from mawaarith_engine_v2 import MawaarithEngine, PCIED_CASES

# ─────────────────────────────────────────────
# FAIRNESS METRICS
# ─────────────────────────────────────────────

def gini(values):
    """Compute Gini coefficient from a list of amounts (per-person shares)."""
    vals = sorted([v for v in values if v > 0])
    if not vals or len(vals) == 1:
        return 0.0
    n = len(vals)
    cumsum = 0
    for i, v in enumerate(vals):
        cumsum += (2 * (i + 1) - n - 1) * v
    return cumsum / (n * sum(vals))


def theil_t(values):
    """Theil T index — entropy-based inequality measure."""
    vals = [v for v in values if v > 0]
    if not vals:
        return 0.0
    mean_v = sum(vals) / len(vals)
    if mean_v == 0:
        return 0.0
    return sum((v / mean_v) * math.log(v / mean_v) for v in vals) / len(vals)


def atkinson(values, epsilon=0.5):
    """Atkinson inequality index with epsilon=0.5 (moderate inequality aversion)."""
    vals = [v for v in values if v > 0]
    if not vals or len(vals) < 2:
        return 0.0
    mean_v = sum(vals) / len(vals)
    if epsilon == 1:
        geo_mean = math.exp(sum(math.log(v) for v in vals) / len(vals))
        return 1 - geo_mean / mean_v
    ede = (sum(v ** (1 - epsilon) for v in vals) / len(vals)) ** (1 / (1 - epsilon))
    return 1 - ede / mean_v


def coefficient_of_variation(values):
    vals = [v for v in values if v > 0]
    if len(vals) < 2:
        return 0.0
    return st.stdev(vals) / st.mean(vals)


def share_range(values):
    vals = [v for v in values if v > 0]
    if not vals:
        return 0.0
    return max(vals) - min(vals)


def palma_ratio(values):
    """Palma ratio: top 10% share / bottom 40% share."""
    vals = sorted([v for v in values if v > 0])
    if len(vals) < 3:
        return None
    n = len(vals)
    top10_idx = max(1, int(n * 0.9))
    bot40_idx = max(1, int(n * 0.4))
    top10 = sum(vals[top10_idx:])
    bot40 = sum(vals[:bot40_idx])
    if bot40 == 0:
        return None
    return round(top10 / bot40, 4)


def fairness_report(case_name, naira_per_person):
    """Full fairness metrics for a given list of per-person naira amounts."""
    vals = [v for v in naira_per_person if v > 0]
    return {
        "case": case_name,
        "n_heirs": len(vals),
        "total": sum(vals),
        "mean": round(st.mean(vals), 2) if vals else 0,
        "median": round(st.median(vals), 2) if vals else 0,
        "gini": round(gini(vals), 4),
        "theil_t": round(theil_t(vals), 4),
        "atkinson": round(atkinson(vals), 4),
        "cv": round(coefficient_of_variation(vals), 4),
        "range": round(share_range(vals), 2),
        "palma": palma_ratio(vals),
    }


# ─────────────────────────────────────────────
# CIVIL / EQUAL-SHARE BENCHMARK
# ─────────────────────────────────────────────

def civil_equal_share(total_value, n_heirs):
    """Equal share among all heirs — civil law benchmark."""
    if n_heirs == 0:
        return []
    share = total_value / n_heirs
    return [share] * n_heirs


# ─────────────────────────────────────────────
# COMPUTE FOR ALL 20 PCIED CASES
# ─────────────────────────────────────────────

def compute_pcied_fairness():
    engine = MawaarithEngine()
    results = []

    for case in PCIED_CASES:
        r = engine.compute(case)
        total = r.total_estate_value
        n_all_heirs = sum(case.heirs_input.values())

        # Per-person naira amounts from Islamic distribution
        islamic_pp = []
        for row in r.shares_table:
            if row["status"] == "Inherits" and row["share_fraction"] not in ("—", "0"):
                try:
                    from fractions import Fraction
                    pp_share = float(Fraction(row["share_per_person"]))
                    naira_pp = total * pp_share
                    count = row["count"]
                    for _ in range(count):
                        islamic_pp.append(naira_pp)
                except:
                    pass

        # Civil equal share
        civil_pp = civil_equal_share(total, n_all_heirs)

        # Compute metrics
        islamic_metrics = fairness_report(case.deceased_name, islamic_pp)
        civil_metrics   = fairness_report(case.deceased_name + " [Civil]", civil_pp)

        results.append({
            "case_id": len(results) + 1,
            "name": case.deceased_name,
            "location": case.location,
            "total_value": total,
            "n_all_heirs": n_all_heirs,
            "n_inheriting": len(islamic_pp),
            "islamic": islamic_metrics,
            "civil": civil_metrics,
            "awl": r.awl_applied,
            "radd": r.radd_applied,
            "tanzeel": r.tanzeel_applied,
        })

    return results


# ─────────────────────────────────────────────
# COMPUTE FOR SIMULATION RECORDS (5,000)
# ─────────────────────────────────────────────

def compute_sim_fairness(sim_records):
    """Compute Gini and key metrics for each simulation record."""
    out = []
    for r in sim_records:
        total = r["total_value"]
        # Build per-person naira list from simulation
        pp_list = []
        for role, share in r["per_person"].items():
            if share > 0:
                count = r["heirs_input"].get(role.replace(" ", "_").lower(), 1)
                for _ in range(count):
                    pp_list.append(total * share)

        if not pp_list:
            continue

        n_all = sum(r["heirs_input"].values())
        civil_pp = civil_equal_share(total, n_all)

        out.append({
            "sim_id": r["sim_id"],
            "profile": r["profile"],
            "gender": r["gender"],
            "total_value": total,
            "n_heirs": len(pp_list),
            "awl": r["awl"],
            "radd": r["radd"],
            "tanzeel": r["tanzeel"],
            "gini_islamic": round(gini(pp_list), 4),
            "gini_civil":   round(gini(civil_pp), 4),
            "theil_islamic": round(theil_t(pp_list), 4),
            "atkinson_islamic": round(atkinson(pp_list), 4),
            "cv_islamic": round(coefficient_of_variation(pp_list), 4),
        })
    return out


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("  MAWĀRITH ANALYTICS — Project 3: Fairness Metrics")
    print("=" * 65)

    # ── PCIED Cases ──────────────────────────────────────────
    print("\n[1/2] Computing fairness metrics for 20 PCIED cases...")
    pcied = compute_pcied_fairness()

    print(f"\n  {'Case':>2}  {'Gini (Islamic)':>15}  {'Gini (Civil)':>13}  {'Theil T':>8}  {'Atkinson':>9}  {'CV':>7}")
    print(f"  {'-'*62}")
    for p in pcied:
        print(f"  {p['case_id']:>2}  {p['islamic']['gini']:>15.4f}  {p['civil']['gini']:>13.4f}  "
              f"{p['islamic']['theil_t']:>8.4f}  {p['islamic']['atkinson']:>9.4f}  {p['islamic']['cv']:>7.4f}")

    ginis = [p["islamic"]["gini"] for p in pcied]
    print(f"\n  Mean Gini (Islamic)  : {st.mean(ginis):.4f}")
    print(f"  Median Gini (Islamic): {st.median(ginis):.4f}")
    print(f"  Civil equal-share Gini (mean): {st.mean(p['civil']['gini'] for p in pcied):.4f}")

    with open("pcied_fairness.json", "w") as f:
        json.dump(pcied, f)
    print("  → Saved: pcied_fairness.json")

    # ── Simulation Records ───────────────────────────────────
    print("\n[2/2] Computing fairness metrics for 5,000 simulation records...")
    sim_records = json.load(open("simulation_results.json"))
    sim_fair = compute_sim_fairness(sim_records)

    ginis_sim = [r["gini_islamic"] for r in sim_fair]
    ginis_civ = [r["gini_civil"]   for r in sim_fair]

    print(f"\n  Simulation Gini (Islamic) — Mean: {st.mean(ginis_sim):.4f}  Median: {st.median(ginis_sim):.4f}")
    print(f"  Simulation Gini (Civil)   — Mean: {st.mean(ginis_civ):.4f}  Median: {st.median(ginis_civ):.4f}")

    import collections
    by_profile = collections.defaultdict(list)
    for r in sim_fair:
        by_profile[r["profile"]].append(r["gini_islamic"])
    print(f"\n  Mean Gini by Profile:")
    for p, vals in sorted(by_profile.items(), key=lambda x: -st.mean(x[1])):
        print(f"    {p:<45} {st.mean(vals):.4f}")

    with open("sim_fairness.json", "w") as f:
        json.dump(sim_fair, f)
    print("\n  → Saved: sim_fairness.json")
    print("\n" + "=" * 65)
    print("  Project 3 analysis complete.")
    print("=" * 65)
