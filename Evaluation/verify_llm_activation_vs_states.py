"""Compare llm_last_result.json activations vs simulations/*_states.sto."""

from __future__ import annotations

import argparse
import json
import os
import re
from typing import Dict, List, Tuple


def _load_sto_activation_map(sto_path: str) -> Dict[str, float]:
    with open(sto_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    end = None
    for i, line in enumerate(lines):
        if line.strip().lower() == "endheader":
            end = i
            break
    if end is None:
        raise ValueError(f"No endheader in {sto_path}")
    if end + 2 >= len(lines):
        raise ValueError(f"No data rows in {sto_path}")

    col_line = lines[end + 1].strip()
    cols = col_line.split()
    data_line = lines[end + 2].strip()
    vals = re.split(r"\s+", data_line)
    if len(cols) != len(vals):
        # Some STOs may have aligned columns; still try numeric alignment by joining tail.
        # For your app-generated files it's usually exact.
        raise ValueError(
            f"Column/value count mismatch in {sto_path}: cols={len(cols)} vals={len(vals)}"
        )

    out: Dict[str, float] = {}
    for c, v in zip(cols, vals):
        if c.lower() == "time":
            continue
        name = c
        if name.endswith("/activation"):
            name = name[: -len("/activation")]
        out[name] = float(v)
    return out


def _muscle_name_from_llm_key(k: str) -> str:
    # We store muscle names as-is in JSON; optionally normalize /activation suffix.
    return k.strip()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--gesture", required=True, help="e.g. IMRL, TL, T, etc.")
    args = p.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(project_root, "llm_last_result.json")
    sto_path = os.path.join(project_root, "simulations", f"{args.gesture}_states.sto")

    if not os.path.isfile(json_path):
        raise FileNotFoundError(
            f"Missing {json_path}. Run one simulation from the app first."
        )
    if not os.path.isfile(sto_path):
        raise FileNotFoundError(f"Missing generated STO: {sto_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        llm = json.load(f)

    muscle_parameters = llm.get("muscle_parameters") or {}
    if not muscle_parameters:
        raise ValueError("llm_last_result.json has no muscle_parameters")

    llm_activation: Dict[str, float] = {}
    for muscle, params in muscle_parameters.items():
        if not isinstance(params, dict) or "activation" not in params:
            continue
        llm_activation[_muscle_name_from_llm_key(muscle)] = float(params["activation"])

    sto_activation = _load_sto_activation_map(sto_path)

    muscles = sorted(set(llm_activation.keys()) & set(sto_activation.keys()))
    if not muscles:
        raise ValueError(
            "No overlapping muscles between LLM activation keys and STO columns."
        )

    rows: List[Tuple[str, float, float, float]] = []
    max_abs_err = -1.0
    worst = None
    for m in muscles:
        a_llm = llm_activation[m]
        a_sto = sto_activation[m]
        err = abs(a_sto - a_llm)
        rows.append((m, a_llm, a_sto, err))
        if err > max_abs_err:
            max_abs_err = err
            worst = (m, a_llm, a_sto, err)

    print(f"Gesture: {args.gesture}")
    print(f"STO: {sto_path}")
    print(f"LLM activations used: {len(llm_activation)} muscles; matched: {len(muscles)}")
    print(f"Max abs error: {max_abs_err:.8f}")
    if worst:
        m, a_llm, a_sto, err = worst
        print(f"Worst mismatch: {m}: llm={a_llm:.6f}, sto={a_sto:.6f}, err={err:.6f}")

    # Print top 10 mismatches
    rows.sort(key=lambda x: x[3], reverse=True)
    print("\nTop mismatches (up to 10):")
    for m, a_llm, a_sto, err in rows[:10]:
        print(f"- {m}: llm={a_llm:.6f} sto={a_sto:.6f} abs_err={err:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

