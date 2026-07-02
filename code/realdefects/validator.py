"""Validation for Real-MRDefect-10 defect cards.

Enforces, without relaxing the bar:
  - evidence completeness (all required fields present & non-empty);
  - MR-oracle completeness (the four oracle components present) so non-MR
    entries are rejected;
  - crash-only rejection (a value-less crash is not MR-value-detectable);
  - status-transition rules (reproducible needs a repro artifact; verified
    needs affected + fixed version/commit + repro artifact + full oracle);
  - the DL/tensor <=40% domain cap and duplicate-id detection at set level.
"""

import schema


def _blank(v):
    return v is None or (isinstance(v, str) and v.strip() == "")


def validate_card(card):
    """Return a list of error strings for one card ([] means valid)."""
    errs = []
    cid = card.get("id", "<no-id>")

    # 1. evidence completeness: required fields present; non-empty unless the
    #    field is optional-until-verified (e.g. an open defect has no fix yet).
    for f in schema.REQUIRED_FIELDS:
        if f not in card:
            errs.append(f"[{cid}] missing required field: {f}")
        elif _blank(card.get(f)) and f not in schema.OPTIONAL_UNTIL_VERIFIED:
            errs.append(f"[{cid}] missing/empty required field: {f}")

    # 2. status must be one of the three (do not invent extra statuses).
    status = card.get("status")
    if status not in schema.STATUS_VALUES:
        errs.append(
            f"[{cid}] invalid status {status!r}; "
            f"must be one of {schema.STATUS_VALUES}")

    # 3. MR-oracle completeness (already covered by required fields, but state
    #    it explicitly so a non-MR-detectable entry is unambiguously rejected).
    for f in schema.MR_ORACLE_FIELDS:
        if _blank(card.get(f)):
            errs.append(
                f"[{cid}] MR-oracle incomplete: {f} is empty "
                f"(entry is not MR-detectable)")

    # 4. crash-only rejection: a value-less crash has no violating-value oracle.
    haystack = " ".join(
        str(card.get(f, "")).lower()
        for f in ("violating_observation", "why_not_crash_only",
                  "behavioral_symptom")
    )
    hit = [m for m in schema.CRASH_ONLY_MARKERS if m in haystack]
    if hit:
        errs.append(
            f"[{cid}] appears crash-only (markers {hit}); "
            f"not an MR-value-detectable defect")

    # 5. status-transition rules (never lower the candidate/repro/verified bar).
    repro = not _blank(card.get("repro_artifact"))
    if status == "reproducible" and not repro:
        errs.append(
            f"[{cid}] status=reproducible requires a repro_artifact "
            f"(local/script reproduction of the MR violation)")
    if status == "verified":
        missing = []
        if _blank(card.get("affected_version")):
            missing.append("affected_version")
        if _blank(card.get("fixed_version_or_commit")):
            missing.append("fixed_version_or_commit")
        if not repro:
            missing.append("repro_artifact")
        oracle_missing = [f for f in schema.MR_ORACLE_FIELDS
                          if _blank(card.get(f))]
        if missing or oracle_missing:
            errs.append(
                f"[{cid}] status=verified requires full chain; missing "
                f"{missing + oracle_missing}")

    return errs


def validate_cardset(cards):
    """Validate a list of cards: per-card errors + set-level cap/duplicate."""
    errs = []
    for c in cards:
        errs.extend(validate_card(c))

    # duplicate ids
    seen = {}
    for c in cards:
        cid = c.get("id")
        seen[cid] = seen.get(cid, 0) + 1
    for cid, n in seen.items():
        if n > 1:
            errs.append(f"duplicate id: {cid} appears {n} times")

    # DL/tensor domain cap
    total = len(cards)
    if total:
        dl = sum(1 for c in cards
                 if str(c.get("project", "")).lower() in schema.DL_TENSOR_PROJECTS)
        frac = dl / total
        if frac > schema.DL_TENSOR_CAP_FRACTION + 1e-9:
            errs.append(
                f"DL/tensor domain cap exceeded: {dl}/{total} "
                f"= {frac:.0%} > {schema.DL_TENSOR_CAP_FRACTION:.0%}")

    return errs
