"""In-family census: run every library substrate through invert() + the gate.

One representative cell per substrate folder. Reports the gate verdict (IN/OUT),
the per-channel C S/N, and the dC coverage (camera reading) so we can see WHICH
substrates the KWW-FDT 5-vector can actually fit, and what type they are.

Run: python H:/mpa-conform/scripts/census_in_family.py
"""
from __future__ import annotations
import sys, json, glob, os
from pathlib import Path

sys.path.insert(0, "H:/mpa-conform")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import numpy as np
from conformer.compute import inversion

DATA = Path("H:/mpa-central/library/data")
T = 1.0


def pick_cell(folder: Path):
    cells = sorted(folder.glob("*velocity*.json")) or sorted(folder.glob("*.json"))
    return cells[0] if cells else None


def rows_of(path):
    c = json.load(open(path))
    s = sorted(c["results"]["all_samples"], key=lambda e: e["dt"])
    scale = (c.get("tau_env_analytic") or c.get("tau_env_measured") or {}).get("value") or 1.0
    rows = [{"tau": e["dt"], "C": e["C_mean"], "chi": e["chi_mean"],
             "C_sem": e.get("C_sem", 0.0), "chi_sem": e.get("chi_sem", 0.0)} for e in s]
    gt = (c.get("operating_point") or {}).get("gt")
    return rows, scale, gt


def main():
    folders = sorted([d for d in DATA.iterdir() if d.is_dir()])
    in_family, out_family, errored = [], [], []
    print(f"{'substrate':<18} {'gt':>3} {'gate':>4} {'C S/N':>8} {'dC range':>16}  cell")
    print("-" * 90)
    for folder in folders:
        cell = pick_cell(folder)
        if cell is None:
            continue
        name = folder.name
        try:
            rows, scale, gt = rows_of(cell)
            if len(rows) < 5:
                errored.append((name, "fewer than 5 rows")); continue
            res = inversion.invert(rows, tau_scale=scale, T=T, skip_stage2=True)
            fv = res.five_vector_fit
            dC = 1.0 - np.array([r["C"] for r in rows])
            snrC = fv.channel_snr.get("C", float("nan"))
            gate = "IN " if fv.in_domain else "OUT"
            (in_family if fv.in_domain else out_family).append(name)
            print(f"{name:<18} {str(gt):>3} {gate:>4} {snrC:>8.1f} "
                  f"{f'[{dC.min():.2f},{dC.max():.2f}]':>16}  {os.path.basename(cell)}")
        except Exception as e:
            errored.append((name, f"{type(e).__name__}: {e}"))

    print("\n" + "=" * 60)
    print(f"IN-FAMILY  ({len(in_family)}): {', '.join(in_family) or '(none)'}")
    print(f"OUT        ({len(out_family)}): {', '.join(out_family) or '(none)'}")
    if errored:
        print(f"ERRORED    ({len(errored)}):")
        for n, why in errored:
            print(f"    {n}: {why}")


if __name__ == "__main__":
    main()
