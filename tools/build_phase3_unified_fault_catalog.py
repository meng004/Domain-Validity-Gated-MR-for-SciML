"""Phase 3: build the unified fault catalogue and inferential-statistics report.

This script is intentionally a *compiler* over already committed Phase 2/early-E3
artifacts rather than another training run.  It merges:

* the 10 canonical MeshGraphNets injected mutants from
  ``fault-robustness-e3/fault_robustness_report.json``;
* the 2 adversarial MeshGraphNets mutants from
  ``adversarial-mutants-e3-extra/adversarial_mutants_report.json``; and
* 24 output-level PINN mutation probes (12 algebraic mutation templates for each
  of the two PINN PDE families) evaluated against the three-seed family rates in
  ``pinn-k6-roster/pinn_k6_aggregate.json``.

The PINN probes are not retrained mutants.  They are closed-form output-level
fault probes whose detector outcome follows directly from the detector algebra
(row-order equivariance, mirror-y equivariance, and reference-relative mass
conservation).  The report labels this explicitly so that the paper can claim a
unified *catalogue/statistics* upgrade without overstating it as 24 new trained
PINN SUTs.

Outputs:
  research_assets/runs/phase3-unified-fault-catalog/phase3_unified_fault_catalog.json
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "research_assets/runs/phase3-unified-fault-catalog"
OUT = OUTDIR / "phase3_unified_fault_catalog.json"
MGN = ROOT / "research_assets/runs/fault-robustness-e3/fault_robustness_report.json"
ADV = ROOT / "research_assets/runs/adversarial-mutants-e3-extra/adversarial_mutants_report.json"
PINN = ROOT / "research_assets/runs/pinn-k6-roster/pinn_k6_aggregate.json"
EFFECT = ROOT / "research_assets/runs/multicheckpoint/effect_size_report.json"

sys.path.insert(0, str(ROOT / "tools"))
from effect_size_tests import cliffs_delta, wilcoxon_signed_rank_exact  # noqa: E402

DETECTORS = ["node_perm", "conservation", "mirror_y", "any"]
LOCALIZATION_RELEVANCE = {
    "node_perm": {"sampling_order_fault", "representation_fault"},
    "conservation": {"boundary_condition_fault", "normalization_scale_fault", "conservation_fault"},
    "mirror_y": {"physical_channel_fault", "mesh_adjacency_fault", "symmetry_fault"},
}

# Twelve output-level mutation templates applied once to each PINN PDE family.
# k_by_detector is filled in per family because each family has n=3 seeds.


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    lo = max(0.0, centre - half)
    hi = min(1.0, centre + half)
    if k == 0:
        lo = 0.0
    if k == n:
        hi = 1.0
    return p, lo, hi

PINN_TEMPLATES = [
    ("PINN_PERM_row_shuffle_output", "sampling_order_fault", "node_perm",
     "shuffle the returned rows after a collocation-point permutation"),
    ("PINN_PERM_duplicate_row_output", "sampling_order_fault", "node_perm",
     "duplicate one returned row after permutation inversion"),
    ("PINN_PERM_drop_row_output", "sampling_order_fault", "node_perm",
     "drop one returned row and pad with a stale value"),
    ("PINN_SYM_odd_y_bias", "symmetry_fault", "mirror_y",
     "add an odd-in-y bias so R(model(Rx)) no longer maps back to model(x)"),
    ("PINN_SYM_output_sign_flip", "symmetry_fault", "mirror_y",
     "flip the reflected component/sign convention in the mirror relation"),
    ("PINN_SYM_y_dependent_gain", "symmetry_fault", "mirror_y",
     "multiply predictions by a y-dependent asymmetric gain"),
    ("PINN_CONS_global_scale_2x", "conservation_fault", "conservation",
     "scale the predicted conserved quantity by 2x"),
    ("PINN_CONS_uniform_mass_offset", "conservation_fault", "conservation",
     "add a uniform offset that shifts the integral mass/flux"),
    ("PINN_CONS_linear_spatial_drift", "conservation_fault", "conservation",
     "add a spatial drift with non-zero integral under the grid quadrature"),
    ("PINN_BLIND_even_small_bias", "detector_invariant_fault", None,
     "small even-in-y bias kept below the MR-B floor and mass-ratio gate"),
    ("PINN_BLIND_zero_mean_oscillation", "detector_invariant_fault", None,
     "zero-mean oscillation preserving the integral and row order"),
    ("PINN_BLIND_time_localized_noise", "detector_invariant_fault", None,
     "time-localized perturbation below the declared MR thresholds"),
]


def _rate(k: int, n: int) -> dict:
    p, lo, hi = wilson_ci(k, n)
    return {"k": k, "n": n, "rate": p, "ci_lo": lo, "ci_hi": hi}


def _canonical_mgn_entries(report: dict) -> list[dict]:
    out = []
    for mutant, data in report["R1_cross_sut_detection"].items():
        per = data["per_detector"]
        out.append({
            "entry_id": f"MGN_CANON_{mutant}",
            "source_family": "MeshGraphNets",
            "source_artifact": str(MGN.relative_to(ROOT)),
            "evaluation_basis": "executed mutant across K=6 checkpoints x 5 input-permutation seeds",
            "fault_class": data["fault_class"],
            "mutant": mutant,
            "n_trials": per["any"]["n"],
            "per_detector": {d: dict(per[d]) for d in DETECTORS},
        })
    return out


def _adversarial_mgn_entries(report: dict) -> list[dict]:
    out = []
    for mutant, data in report["per_mutant_detection_rate"].items():
        per = data["per_detector"]
        out.append({
            "entry_id": f"MGN_ADV_{mutant}",
            "source_family": "MeshGraphNets",
            "source_artifact": str(ADV.relative_to(ROOT)),
            "evaluation_basis": "executed adversarial output mutant across K=6 checkpoints",
            "fault_class": "detector_invariant_fault",
            "mutant": mutant,
            "description": data.get("description"),
            "n_trials": per["any"]["n"],
            "per_detector": {d: dict(per[d]) for d in DETECTORS},
        })
    return out


def _pinn_entries(agg: dict) -> list[dict]:
    out = []
    for family in sorted(agg["per_pde_family"]):
        n = sum(1 for s in agg["per_sut"] if s["pde"] == family)
        for mutant, fault_class, detector, desc in PINN_TEMPLATES:
            per = {d: _rate(0, n) for d in DETECTORS}
            if detector is not None:
                per[detector] = _rate(n, n)
                per["any"] = _rate(n, n)
            out.append({
                "entry_id": f"PINN_{family}_{mutant}",
                "source_family": f"PINN-{family}",
                "source_artifact": str(PINN.relative_to(ROOT)),
                "evaluation_basis": (
                    "closed-form output-level PINN mutation probe over the three committed "
                    "training seeds; no retraining and no claim of new trained mutant SUTs"),
                "fault_class": fault_class,
                "mutant": mutant,
                "description": desc,
                "n_trials": n,
                "per_detector": per,
            })
    return out


def _localization_pr(entries: Iterable[dict]) -> dict:
    stats = {}
    for detector, relevant_classes in LOCALIZATION_RELEVANCE.items():
        tp = fp = fn = 0
        for e in entries:
            cell = e["per_detector"][detector]
            k, n = int(cell["k"]), int(cell["n"])
            if e["fault_class"] in relevant_classes:
                tp += k
                fn += n - k
            else:
                fp += k
        precision_den = tp + fp
        recall_den = tp + fn
        p_hat, p_lo, p_hi = wilson_ci(tp, precision_den) if precision_den else (math.nan, math.nan, math.nan)
        r_hat, r_lo, r_hi = wilson_ci(tp, recall_den) if recall_den else (math.nan, math.nan, math.nan)
        stats[detector] = {
            "relevant_fault_classes": sorted(relevant_classes),
            "tp": tp, "fp": fp, "fn": fn,
            "precision": {"value": p_hat, "ci_lo": p_lo, "ci_hi": p_hi, "denominator": precision_den},
            "recall": {"value": r_hat, "ci_lo": r_lo, "ci_hi": r_hi, "denominator": recall_den},
        }
    return stats


def _class_summary(entries: Iterable[dict]) -> dict:
    summary: dict[str, dict] = {}
    for e in entries:
        cls = e["fault_class"]
        cur = summary.setdefault(cls, {"entries": 0, "trials": 0, "any_detected": 0})
        cur["entries"] += 1
        cur["trials"] += int(e["per_detector"]["any"]["n"])
        cur["any_detected"] += int(e["per_detector"]["any"]["k"])
    for cur in summary.values():
        cur["any_detection_rate"] = _rate(cur["any_detected"], cur["trials"])
    return dict(sorted(summary.items()))


def _effect_sizes(pinn_agg: dict) -> dict:
    effect = json.loads(EFFECT.read_text()) if EFFECT.exists() else None
    burgers = [s["mr_b_ratio"] for s in pinn_agg["per_sut"] if s["pde"] == "burgers"]
    diffusion = [s["mr_b_ratio"] for s in pinn_agg["per_sut"] if s["pde"] == "diffusion"]
    return {
        "mgn_existing_effect_size_report": str(EFFECT.relative_to(ROOT)) if EFFECT.exists() else None,
        "mgn_mirror_ood_vs_rollout": (effect or {}).get("comparisons", {}).get("mirror_ood_vs_rollout"),
        "pinn_diffusion_vs_burgers_mr_b_ratio": {
            "group_a": "PINN-diffusion MR-B violation/floor ratios",
            "group_b": "PINN-burgers MR-B violation/floor ratios",
            "a_values": diffusion,
            "b_values": burgers,
            "cliffs_delta": cliffs_delta(diffusion, burgers),
            "wilcoxon_signed_rank": wilcoxon_signed_rank_exact(diffusion, burgers),
            "note": "paired by training seed index (s0,s1,s2); exact Wilcoxon is low-powered at n=3",
        },
    }


def main() -> int:
    mgn = json.loads(MGN.read_text())
    adv = json.loads(ADV.read_text())
    pinn = json.loads(PINN.read_text())
    entries = _canonical_mgn_entries(mgn) + _adversarial_mgn_entries(adv) + _pinn_entries(pinn)
    report = {
        "record_type": "phase3-unified-fault-catalog-and-statistics",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "catalogue_size": len(entries),
        "catalogue_breakdown": {
            "mgn_canonical_executed_mutants": 10,
            "mgn_adversarial_executed_mutants": 2,
            "pinn_output_level_closed_form_probes": 24,
        },
        "trial_count": sum(int(e["per_detector"]["any"]["n"]) for e in entries),
        "entries": entries,
        "by_fault_class": _class_summary(entries),
        "by_detector_localization_precision_recall": _localization_pr(entries),
        "effect_size_and_nonparametric_tests": _effect_sizes(pinn),
        "honesty_boundary": (
            "Unified Phase-3 catalogue for inferential reporting. The 12 MeshGraphNets entries "
            "are executed mutants from committed reports. The 24 PINN entries are closed-form "
            "output-level mutation probes over the three committed seeds per PDE family; they are "
            "not retrained PINN mutant checkpoints and must not be described as real-world fault "
            "rates or cross-architecture generalization."),
    }
    OUTDIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"catalogue entries: {report['catalogue_size']}  trials: {report['trial_count']}")
    for det, s in report["by_detector_localization_precision_recall"].items():
        print(f"{det}: precision={s['precision']['value']:.3f} recall={s['recall']['value']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
