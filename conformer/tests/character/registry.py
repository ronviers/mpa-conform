"""Character test registry.

A character test is a function that produces a SHOT (EXR sequence +
mp4 preview), not an assertion boolean. The verification is the shot
itself, watched in DJV. Mechanical assertions ride alongside as
sanity, recorded into the per-shot manifest so regressions surface.

This is artifact-first testing. Grabs aren't story; shots are.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


@dataclass(frozen=True)
class CharacterTestSpec:
    """Metadata for one character test."""
    test_id: str                # unique within suite, e.g. "ck-glassy_T0.500_spin-flip"
    substrate_class: str        # e.g. "ck-glassy", "surface-code-qec", "neural-population", "banach"
    bundle_path: Path           # input bundle (or synthetic spec for banach)
    description: str            # one line, shown in report
    fn: Callable                # the test function; receives a ShotRunContext
    expected_character: str = ""  # human-readable: what should be visible in the shot


@dataclass
class CharacterTestResult:
    """Output of running one character test."""
    spec: CharacterTestSpec
    passed_mechanical: bool
    failed_assertions: list[str] = field(default_factory=list)
    shot_dir: Optional[Path] = None
    preview_mp4: Optional[Path] = None
    first_frame_png: Optional[Path] = None
    runtime_s: float = 0.0
    error: Optional[str] = None
    data_channel_stats: dict[str, dict[str, float]] = field(default_factory=dict)


REGISTRY: list[CharacterTestSpec] = []


def character_test(
    *,
    substrate_class: str,
    bundle_path: Path | str,
    description: str = "",
    expected_character: str = "",
    test_id: Optional[str] = None,
) -> Callable[[Callable], Callable]:
    """Decorator: register a function as a character test."""
    bundle = Path(bundle_path)

    def deco(fn: Callable) -> Callable:
        tid = test_id or f"{substrate_class}_{bundle.stem.removesuffix('.bundle')}"
        REGISTRY.append(CharacterTestSpec(
            test_id=tid,
            substrate_class=substrate_class,
            bundle_path=bundle,
            description=description,
            expected_character=expected_character,
            fn=fn,
        ))
        return fn

    return deco


def all_tests() -> list[CharacterTestSpec]:
    """Force import of cases/ subpackage so decorators register; return registry."""
    from . import cases  # noqa: F401
    return list(REGISTRY)
