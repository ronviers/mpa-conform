# Character test suite — mpa-conform

A **character test** verifies that the framework's substrate-agnostic
character (cdv1) is correctly producible and perceivable for a given
substrate measurement. The verification artifact is a **shot** (EXR
sequence + mp4 preview), not an assertion boolean. The shot gets
watched in DJV; a small set of mechanical assertions rides along to
catch regressions.

> Grabs aren't story. A test that produces a single PNG cannot show
> character — character is *how* the substrate moves through canonical
> state space over time. The test framework defaults to shots for that
> reason.

Established 2026-05-17, alongside the shot pipeline at
[`conformer/shot/`](../../shot/) and the standards at
[`conformer/shot/STANDARDS.md`](../../shot/STANDARDS.md).

## Run

```
python -m conformer.tests.character.runner
python -m conformer.tests.character.runner --filter ck-glassy
```

Output lands at `output/tests/character/<timestamp>/`:

```
<timestamp>/
  <test_id>/
    first_frame.png         # thumbnail (ffmpeg extract of frame 0)
  ...
  index.html                # dailies report; opens directly in a browser
  results.json              # machine-readable
```

The shot itself lands at `output/shots/<class>/<bundle_stem>/` (the same
place `python -m conformer.cli shot` writes). Open `preview.mp4` in DJV
for frame-accurate review with channel selection and compare mode.

## The destination

Character tests render shots that the **mpa-auditor viewport** will
eventually display interactively. The auditor is the destination
surface — when it gains tumbling, scrubbing, and natural-cadence
playback, the same EXR sequences these tests produce will play through
its viewport. Until then, DJV is the review surface.

## What each sibling repo contributes

Character tests are the cross-repo integration point. Each repo carries
a load-bearing slice of what shows up in the shot.

| Repo | Contribution to character tests |
|---|---|
| **mpa-conform** | Owns the framework. Owns the shot pipeline. Owns the curator → bundle path that feeds tests. Owns this README. |
| **mpa-auditor** | The destination viewport. Defines the viewport contract the shots target. (Bundle-import migration on its roadmap; until then, character tests render directly via `conformer.shot.builder`.) |
| **mpa-atlas** | Spec stability. cdv1's universal kernel, gFDR signatures, regime classifier, RFC-S — these are the structures the tests verify substrates render *as*. Spec changes here must round-trip through a character test run. |
| **mpa-central** | Library + grinder. The 60 grind cells under `library/data/` are the empirical input. Library refresh + grinder updates must re-pass character tests. |
| **mpa-scale-solver** | Six per-frame EXR data channels (`chit`, `gamma_AB`, `regime_label`, `in_gamut`, `provenance_hash`, `validation_flags`) per [`EXR_CHANNEL_MANIFEST.md`](../../../../mpa-scale-solver/docs/EXR_CHANNEL_MANIFEST.md). Plus the `BanachSubstrate` analytical reference used as overlay. |
| **mpa-solver** | Nine per-frame EXR data channels (`X_c`, `X_r`, `alpha_s`, `P_s`, `N_f`, `beta_mem`, `Q`, `I_pred`, `C_mu`) — deferred until the `fit_invariants` Python port lands; tests render without them until then. |

Each sibling repo's CLAUDE.md has a short pointer to this doc and
names that repo's character-test contract.

## Adding a test

```python
# conformer/tests/character/cases/<class>.py

from pathlib import Path
from conformer.shot.builder import build_shot
from conformer.shot.standards import SHOT_STANDARDS
from ..assertions import check_shot
from ..registry import character_test, CharacterTestResult


@character_test(
    substrate_class="my-class",
    bundle_path=Path("output/seed-corpus/my-class/some_cell.bundle.json"),
    description="One-line description shown in the report.",
    expected_character="Plain-English description of what should be visible in the shot.",
)
def test_something(spec):
    import time as _time
    t0 = _time.perf_counter()
    manifest = build_shot(spec.bundle_path, standards=SHOT_STANDARDS)
    # ... assertions ...
    return CharacterTestResult(
        spec=spec, passed_mechanical=passed, failed_assertions=failures,
        shot_dir=..., preview_mp4=..., runtime_s=_time.perf_counter() - t0,
    )
```

Add the module to `cases/__init__.py` to register it.

## Mechanical assertions (sanity, not certification)

[`assertions.py`](assertions.py) `check_shot()` verifies:

- Frame count matches expectation (when supplied).
- Each sampled frame has the six required scale-solver data channels.
- Each channel value falls within its plausible range
  (`CHANNEL_RANGES` constants).
- `preview.mp4` exists and is non-trivially sized.
- RGBA channels are present in the EXR.

These catch shot-pipeline regressions. They do **not** certify the
shot shows the right character — that's the dailies' job.

## Discipline

- **Render shots, then watch them.** The render pass is the test. The
  watching pass is the verification.
- **Failures are informational, not blocking.** A failed mechanical
  assertion means something changed in the pipeline; it does not mean
  the character is wrong. Open the shot in DJV before deciding what
  the failure means.
- **One move per session.** When extending the suite, add one test or
  one assertion at a time. Watch the dailies. Then plan the next move.
  Per `feedback_single_move_design`.
