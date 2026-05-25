"""pose — the dumb dispatcher (Outline A seam).

NOT an inventor. It does exactly five things:
  1. (re)materialize the substrate's frozen data by running the slug's freeze;
  2. SANITIZE that data into a blind copy (workspace/<slug>.data.csv) — strips all
     provenance comments, keeps only the column header + numeric rows. The raw
     .frozen.csv header leaks the substrate + params (e.g. "class-B laser, r=2.0");
     the blind boundary must cover the DATA artifact, not just entry.md (pass-1
     finding). A structural check refuses to emit if any prose survives.
  3. emit ONLY the blind half of the entry to workspace/<slug>.packet.md, with its
     data_path rewritten to point at the sanitized copy;
  4. SANITIZE the traversal (PIPELINE.md) into a blind copy
     (workspace/<slug>.traversal.md) — strips earned/finding blockquotes and
     [EARNED …] tags, which name substrates and answers; the answerer reads this,
     never raw PIPELINE.md (accretion turned the raw doc into a blinding hole);
  5. refuse to emit if a framework token leaks into the blind half or the data
     header, or a substrate/answer token survives in the traversal (code-side
     tripwires — blinding is enforced, not honor-system).

The sealed half of entry.md is never read out. The answerer-session works from the
emitted packet + the SANITIZED data file + the SANITIZED traversal, never from
entry.md, the raw .frozen.csv, or the raw PIPELINE.md.

Usage:  python H:/mpa-conform/blockin/pose.py [slug]
        (slug optional if there is exactly one question)
"""
from __future__ import annotations
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUESTIONS = ROOT / "questions"
WORKSPACE = ROOT / "workspace"
PIPELINE = ROOT / "PIPELINE.md"

SEALED_MARKER = "## SEALED"
# Framework tokens that must never appear in a blind PACKET. Short ambiguous
# symbols (Q, X) are deliberately omitted to avoid false positives; these are the
# unambiguous leak signatures.
LEAK_TOKENS = [
    "chit", "gamma_RO", "omega_RO", "k_frust", "FDR", "regime", "Jacobian",
    "eigenvalue", "Edwards-Anderson", "answer_path", "sealed_answer", "cage_edge",
    "category:", "five-vector", "five_vector",
]

# The blind TRAVERSAL is the generic recipe — it legitimately carries framework METHOD
# vocabulary (k_frust, FDR, chit, regime: that is what the recipe IS). What it must not
# carry is SUBSTRATE IDENTITY or the ANSWER. So the traversal sanitizer uses a different,
# substrate/answer-specific token set (NOT the method-vocabulary packet list above). If
# any of these survive after stripping earned/finding blocks, pose.py refuses to emit.
TRAVERSAL_LEAK_TOKENS = [
    "laser", "class-B", "class B", "ω_RO", "omega_RO", "ω₀", "omega_0", "γ_RO",
    "gamma_RO", "ζ", "zeta", "overdamped", "underdamped", "ring-down", "ringdown",
    "relaxation oscillation", "damped-oscillator", "damped oscillator",
    "Q-band", "Q-peak", "r=2", "r = 2",
]
# Earned/finding content the traversal sanitizer drops: markdown blockquotes and the
# inline [EARNED …] / [CONTACT …] provenance tags.
_EARNED_TAG = re.compile(r"\s*\[(?:EARNED|CONTACT)\b[^\]]*\]")


def resolve_slug(arg: str | None) -> str:
    if arg:
        return arg
    slugs = [p.name for p in QUESTIONS.iterdir() if p.is_dir()]
    if len(slugs) != 1:
        sys.exit(f"need a slug — questions/ holds {len(slugs)}: {slugs}")
    return slugs[0]


def blind_half(entry_text: str) -> str:
    # Match the divider as a section-HEADER line, not a raw substring: an inline
    # mention of "## SEALED" in prose or a header comment (entry.md's own authoring
    # note carries one) must NOT trip the split, or the blind packet emits empty.
    offset = 0
    for ln in entry_text.splitlines(keepends=True):
        if ln.strip().startswith(SEALED_MARKER):
            return entry_text[:offset].rstrip() + "\n"
        offset += len(ln)
    sys.exit(f"entry has no '{SEALED_MARKER}' header line — refusing to guess the blind/sealed split")


def leak_check(blind: str) -> None:
    low = blind.lower()
    hits = [t for t in LEAK_TOKENS if t.lower() in low]
    if hits:
        sys.exit(f"LEAK TRIPWIRE — framework tokens in the blind half: {hits}. "
                 "Move them below the SEALED divider before posing.")


def freeze(slug_dir: Path, refresh: bool) -> Path:
    data_dir = slug_dir / "data"
    existing = list(data_dir.glob("*.frozen.csv")) if data_dir.exists() else []
    freezers = list(slug_dir.glob("freeze_*.py"))
    if not freezers:
        sys.exit(f"no freeze_*.py in {slug_dir}")
    if existing and not refresh:
        return existing[0]
    subprocess.run([sys.executable, str(freezers[0])], check=True)
    return next((slug_dir / "data").glob("*.frozen.csv"))


def _is_number(tok: str) -> bool:
    try:
        float(tok)
        return True
    except ValueError:
        return False


def sanitize_data(frozen_path: Path, slug: str) -> Path:
    """Strip provenance; emit a blind data copy. Structural guarantee: what remains
    is a column header + numeric rows, nothing that names the substrate."""
    kept = [ln for ln in frozen_path.read_text(encoding="utf-8").splitlines()
            if not ln.strip().startswith("#")]
    if len(kept) < 2:
        sys.exit(f"sanitize: {frozen_path} has no data after stripping comments")
    header, rows = kept[0], kept[1:]
    hits = [t for t in LEAK_TOKENS if t.lower() in header.lower()]
    if hits:
        sys.exit(f"sanitize LEAK — column header carries framework tokens {hits}: {header!r}")
    for ln in rows:
        if ln.strip() and not all(_is_number(x) for x in ln.split(",")):
            sys.exit(f"sanitize LEAK — non-numeric row would leak prose into the blind data: {ln!r}")
    WORKSPACE.mkdir(exist_ok=True)
    out = WORKSPACE / f"{slug}.data.csv"
    out.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return out


def sanitize_traversal(slug: str) -> Path:
    """Emit a blind copy of the traversal (PIPELINE.md) for the answerer. The canonical
    PIPELINE.md accretes earned contours that name substrates and findings (the
    silhouette precipitating); a blind answerer must not read those. Strip every
    blockquote line and every [EARNED …]/[CONTACT …] tag — the convention is that all
    earned/status/finding content lives in exactly those two forms — then fail-closed if
    any substrate/answer token survives in the remaining generic recipe."""
    if not PIPELINE.exists():
        sys.exit(f"no PIPELINE.md at {PIPELINE} — cannot emit a blind traversal")
    kept = []
    for ln in PIPELINE.read_text(encoding="utf-8").splitlines():
        if ln.lstrip().startswith(">"):      # earned/status/finding blockquote → drop
            continue
        kept.append(_EARNED_TAG.sub("", ln))  # strip inline provenance tags
    text = "\n".join(kept).rstrip() + "\n"
    low = text.lower()
    hits = [t for t in TRAVERSAL_LEAK_TOKENS if t.lower() in low]
    if hits:
        sys.exit(f"traversal sanitize LEAK — substrate/answer tokens survived: {hits}. "
                 "Move the offending passage into a > blockquote or an [EARNED] tag, or "
                 "rephrase the generic step substrate-neutrally, before posing.")
    WORKSPACE.mkdir(exist_ok=True)
    out = WORKSPACE / f"{slug}.traversal.md"
    out.write_text(text, encoding="utf-8")
    return out


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    refresh = "--refresh" in sys.argv
    slug = resolve_slug(args[0] if args else None)
    slug_dir = QUESTIONS / slug
    entry = slug_dir / "entry.md"
    if not entry.exists():
        sys.exit(f"no entry.md in {slug_dir}")

    raw_data = freeze(slug_dir, refresh)
    blind_data = sanitize_data(raw_data, slug)
    blind = blind_half(entry.read_text(encoding="utf-8"))
    # repoint the packet's data_path at the sanitized copy so a blind answerer that
    # follows the packet never opens the provenance-bearing raw file.
    blind = blind.replace(f"data/{raw_data.name}", str(blind_data))
    leak_check(blind)
    blind_traversal = sanitize_traversal(slug)

    WORKSPACE.mkdir(exist_ok=True)
    packet = WORKSPACE / f"{slug}.packet.md"
    packet.write_text(blind, encoding="utf-8")

    print(f"posed: {slug}")
    print(f"  blind packet    -> {packet}")
    print(f"  blind data      -> {blind_data}  (provenance stripped from {raw_data.name})")
    print(f"  blind traversal -> {blind_traversal}  (earned contours stripped from PIPELINE.md)")
    print(f"  (sealed half of entry.md withheld; packet + data + traversal tripwires passed)")


if __name__ == "__main__":
    main()
