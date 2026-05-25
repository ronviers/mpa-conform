"""Validate the identifiability flag: it must be ORTHOGONAL to the domain gate.

Three cases:
  kww_oracle  -- in-family, real structure. Expect: gate IN, shape params pinned.
  brain       -- the census degenerate-IN (dC pinned at ~1.0). Expect: gate IN BUT
                 identifiability says nothing is pinned -> closes the degenerate-IN hole.
  square_wave -- out-of-family. Expect: gate OUT.

Run: python H:/mpa-conform/scripts/test_identifiability.py
"""
from __future__ import annotations
import sys, json, glob
sys.path.insert(0, "H:/mpa-conform")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import numpy as np
from conformer.compute import five_vector

DATA = "H:/mpa-central/library/data"
CASES = [
    ("kww_oracle (in-family)",  f"{DATA}/kww_oracle/kww_oracle__X0.5__velocity.json"),
    ("brain (degenerate-IN)",   f"{DATA}/brain/brain__committed__velocity.json"),
    ("square_wave (out-family)", f"{DATA}/square_wave/square_wave__P100__velocity.json"),
]


def rows_for(path):
    c = json.load(open(path))
    s = sorted(c["results"]["all_samples"], key=lambda e: e["dt"])
    scale = (c.get("tau_env_analytic") or c.get("tau_env_measured") or {}).get("value") or 1.0
    return [{"tau": e["dt"] / scale, "C": e["C_mean"], "chi": e["chi_mean"],
             "C_sem": e.get("C_sem", 0.0), "chi_sem": e.get("chi_sem", 0.0)} for e in s]


def main():
    for tag, patt in CASES:
        g = glob.glob(patt)
        if not g:
            print(f"{tag}: MISSING"); continue
        fit = five_vector.fit_kww5(rows_for(g[0]), T=1.0, n_boot=24)
        gate = "IN " if fit.in_domain else "OUT"
        print(f"\n{tag}")
        print(f"  domain gate : {gate}  (resid {fit.residual:.4f})")
        ident = fit.identifiability
        if ident is None or not ident.assessable:
            print("  identifiability: not assessable (no grain)"); continue
        for p in five_vector._PARAM_NAMES:
            val = getattr(fit, p)
            mark = "PINNED" if ident.identified[p] else ("RAILED" if ident.railed[p] else "mush")
            print(f"    {p:<10} = {val:8.3f}  spread={ident.spread[p]:7.3f}  -> {mark}")
        pinned = [p for p in ident.identified if ident.identified[p]]
        print(f"  --> pinned: {pinned or 'NOTHING'}")


if __name__ == "__main__":
    main()
