"""External texture optimization backends."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

QUALITY_PRESETS = {
    "very-low": "30-50",
    "low": "50-70",
    "medium": "60-80",
    "high": "70-90",
}


@dataclass(frozen=True, slots=True)
class OptimizationResult:
    source: Path
    optimized: bool
    skipped: bool = False
    error: str | None = None


def is_quantized(path: str | Path) -> bool:
    try:
        with Image.open(path) as image:
            return image.mode == "P"
    except (OSError, ValueError):
        return False


def optimize_png(
    path: str | Path, *, quality: str = "medium", command: str = "pngquant"
) -> OptimizationResult:
    source = Path(path).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != ".png":
        return OptimizationResult(source, optimized=False, skipped=True)
    if is_quantized(source):
        return OptimizationResult(source, optimized=False, skipped=True)
    if quality not in QUALITY_PRESETS:
        raise ValueError(f"unknown quality preset: {quality}")
    if shutil.which(command) is None:
        return OptimizationResult(
            source, optimized=False, error=f"{command} is not available on PATH"
        )

    try:
        result = subprocess.run(
            [
                command,
                "--quality",
                QUALITY_PRESETS[quality],
                "--force",
                "--ext",
                ".png",
                "--skip-if-larger",
                str(source),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return OptimizationResult(source, optimized=False, error=str(exc))

    if result.returncode != 0:
        return OptimizationResult(
            source,
            optimized=False,
            error=result.stderr.strip() or f"pngquant exited with {result.returncode}",
        )
    return OptimizationResult(source, optimized=True)


# Pillow is imported lazily in the module to keep subprocess functionality clear.
from PIL import Image  # noqa: E402
