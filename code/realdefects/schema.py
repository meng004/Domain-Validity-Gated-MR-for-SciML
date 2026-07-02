"""Real-MRDefect-10 defect-card schema.

A defect card records ONE real, MR-detectable behavioral defect with a full
metamorphic oracle (source x, transform T(x), relation R, violating obs) and a
traceable evidence chain (URL, versions, fix point). See the seed-pilot plan
docs/superpowers/plans/2026-07-01-tosem-real-mrdefect-seed-pilot.md.

This module is the single source of truth for field names, status values, and
the DL/tensor project cap population. Validation logic lives in validator.py.
"""

# Fields every card must carry (evidence + MR oracle + SMS-vs-MS hypothesis).
REQUIRED_FIELDS = (
    "id",
    "project",
    "url",
    "affected_version",
    "fixed_version_or_commit",
    "behavioral_symptom",
    "mr_family",
    "source_input_x",
    "transformed_input_Tx",
    "expected_relation_R",
    "violating_observation",
    "why_not_crash_only",
    "reproduction_cost",
    "sms_vs_ms_hypothesis",
    "status",
)

# The four MR-oracle components. If any is empty, the entry is not
# MR-detectable and must be rejected (not a Real-MRDefect card).
MR_ORACLE_FIELDS = (
    "source_input_x",
    "transformed_input_Tx",
    "expected_relation_R",
    "violating_observation",
)

STATUS_VALUES = ("candidate", "reproducible", "verified")

# Fields whose key must be present but may be empty until the card reaches
# 'verified' (a still-open defect has no fix point yet). Non-emptiness for
# these is enforced only by the verified-status transition check.
OPTIONAL_UNTIL_VERIFIED = ("fixed_version_or_commit",)

# DL/tensor projects subject to the <=40% cap (avoid "famous == evidence").
DL_TENSOR_PROJECTS = ("tensorflow", "pytorch", "tvm", "opencv")

# Fraction of a card set that may come from DL/tensor projects.
DL_TENSOR_CAP_FRACTION = 0.40

# Markers that indicate a crash-only / non-behavioral-value defect. If the
# violating observation or the why-not-crash-only justification reduces to one
# of these, the card is not MR-value-detectable.
CRASH_ONLY_MARKERS = (
    "segfault",
    "raises runtimeerror",
    "raises exception",
    "just crashes",
    "core dump",
    "traceback only",
)
