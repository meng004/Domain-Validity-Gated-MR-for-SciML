from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow.ipc as ipc


def infer_array(raw: bytes, shape: tuple[int, ...]) -> np.ndarray:
    count = math.prod(shape)
    if len(raw) == count * 4:
        dtype = np.float32
    elif len(raw) == count * 8:
        dtype = np.float64
    else:
        raise ValueError(
            f"cannot infer dtype for shape={shape}: {len(raw)} bytes for {count} elements"
        )
    return np.frombuffer(raw, dtype=dtype).reshape(shape)


def parse_params_from_sim_id(sim_id: str) -> tuple[float, float]:
    stem = sim_id.removesuffix(".h5")
    re_text, aoa_text = stem.split("_", 1)
    return float(re_text), float(aoa_text)


def relative_l2(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(b.ravel()))
    if denom == 0.0:
        denom = 1.0
    return float(np.linalg.norm((a - b).ravel()) / denom)


def symmetry_score_for_axis(x: np.ndarray, y: np.ndarray, axis: int) -> dict[str, float]:
    x_flip = np.flip(x, axis=axis)
    y_flip = np.flip(y, axis=axis)
    center = float(np.nanmedian((y + y_flip) / 2.0))
    x_scale = float(np.nanmax(x) - np.nanmin(x)) or 1.0
    y_scale = float(np.nanmax(y) - np.nanmin(y)) or 1.0
    return {
        "axis": axis,
        "centerline_y": center,
        "x_invariance_max_norm": float(np.nanmax(np.abs(x - x_flip)) / x_scale),
        "y_reflection_max_norm": float(np.nanmax(np.abs((y + y_flip) - 2.0 * center)) / y_scale),
    }


def choose_reflection_axis(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    candidates = [symmetry_score_for_axis(x, y, 0), symmetry_score_for_axis(x, y, 1)]
    return min(
        candidates,
        key=lambda item: item["x_invariance_max_norm"] + item["y_reflection_max_norm"],
    )


def read_first_arrow_row(path: Path) -> dict[str, Any]:
    reader = ipc.open_stream(path)
    batch = next(reader)
    return {
        name: batch.column(i)[0].as_py()
        for i, name in enumerate(batch.schema.names)
    }


def run_preflight(arrow_path: Path) -> dict[str, Any]:
    row = read_first_arrow_row(arrow_path)
    sim_id = row["sim_id"]
    reynolds, aoa = parse_params_from_sim_id(sim_id)

    x = infer_array(row["x"], (row["x_shape_h"], row["x_shape_w"]))
    y = infer_array(row["y"], (row["y_shape_h"], row["y_shape_w"]))
    u = infer_array(row["u"], (row["shape_t"], row["shape_h"], row["shape_w"]))
    v = infer_array(row["v"], (row["shape_t"], row["shape_h"], row["shape_w"]))
    t = infer_array(row["t"], (row["t_shape"],))

    reflection = choose_reflection_axis(x, y)
    axis = int(reflection["axis"])
    coordinate_floor = max(
        reflection["x_invariance_max_norm"],
        reflection["y_reflection_max_norm"],
    )

    if aoa != 0.0:
        verdict = "out-of-relation-domain"
        reason = "Exact mirror-y is rejected because the source case has non-zero angle of attack."
    elif coordinate_floor > 1e-6:
        verdict = "numerical-tolerance-issue"
        reason = "The coordinate reflection floor is not negligible enough for an exact mirror-y verdict."
    else:
        u_reflected = np.flip(u, axis=axis + 1)
        v_reflected = -np.flip(v, axis=axis + 1)
        u_relative_l2 = relative_l2(u_reflected, u)
        v_relative_l2 = relative_l2(v_reflected, v)
        combined_relative_l2 = relative_l2(
            np.stack([u_reflected, v_reflected]),
            np.stack([u, v]),
        )
        verdict = "inconclusive"
        reason = (
            "The zero-AoA real field can be mirrored and scored, but no independent "
            "PIV measurement-floor bound is available in this preflight run; no pass/fail "
            "claim is licensed."
        )
        return {
            "schema_version": "0.1.0",
            "run_id": "realpdebench-foil-mirror-preflight",
            "source_artifact": str(arrow_path),
            "sim_id": sim_id,
            "reynolds": reynolds,
            "angle_of_attack_degrees": aoa,
            "field_shape": {
                "t": int(row["shape_t"]),
                "h": int(row["shape_h"]),
                "w": int(row["shape_w"]),
                "time_samples": int(t.shape[0]),
            },
            "reflection_mapping": reflection,
            "coordinate_floor_max_norm": coordinate_floor,
            "metric": {
                "u_mirror_relative_l2": u_relative_l2,
                "v_sign_reversed_mirror_relative_l2": v_relative_l2,
                "combined_uv_relative_l2": combined_relative_l2,
            },
            "verdict": verdict,
            "reason": reason,
            "claim_limitations": (
                "This preflight run is a production-adjacent public real-flow field "
                "mirror-y scoring witness. It is not a SUT pass/fail result, not a "
                "real-defect detection result, and not production CFD validation."
            ),
        }

    return {
        "schema_version": "0.1.0",
        "run_id": "realpdebench-foil-mirror-preflight",
        "source_artifact": str(arrow_path),
        "sim_id": sim_id,
        "reynolds": reynolds,
        "angle_of_attack_degrees": aoa,
        "field_shape": {
            "t": int(row["shape_t"]),
            "h": int(row["shape_h"]),
            "w": int(row["shape_w"]),
            "time_samples": int(t.shape[0]),
        },
        "reflection_mapping": reflection,
        "coordinate_floor_max_norm": coordinate_floor,
        "metric": None,
        "verdict": verdict,
        "reason": reason,
        "claim_limitations": (
            "This preflight run is a fail-closed RealPDEBench foil admissibility check. "
            "It does not license pass/fail, real-defect, production CFD, or model "
            "reliability claims."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arrow", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    report = run_preflight(args.arrow)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
