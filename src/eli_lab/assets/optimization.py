"""PNG texture optimization services."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

PNGQUANT_QUALITY_PRESETS = {
    "Very Low": "30-50",
    "Low": "50-70",
    "Medium": "60-80",
    "High": "70-90",
}


@dataclass(frozen=True, slots=True)
class TextureOptimizationResult:
    """Outcome of optimizing one PNG texture."""

    source: Path
    success: bool
    skipped: bool = False
    error: str | None = None


def pngquant_available() -> bool:
    """Return whether pngquant is available on PATH."""
    return shutil.which("pngquant") is not None


def _is_quantized(path: Path) -> bool:
    from PIL import Image

    try:
        with Image.open(path) as image:
            return image.mode == "P"
    except (OSError, ValueError):
        return False


def optimize_textures(
    root_folder: str | Path,
    quality_setting: str = "Medium",
    *,
    replace_original: bool = True,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[TextureOptimizationResult]:
    """Optimize PNG files recursively using pngquant.

    By default pngquant replaces the source in place, matching the legacy tool.
    Callers can disable this and write optimized output beside the source with a
    temporary extension when a non-destructive workflow is required.
    """
    root = Path(root_folder).expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)
    if not pngquant_available():
        raise RuntimeError("pngquant is not installed or not available on PATH")

    quality = PNGQUANT_QUALITY_PRESETS.get(quality_setting, PNGQUANT_QUALITY_PRESETS["Medium"])
    files = sorted(path for path in root.rglob("*.png") if path.is_file())
    results: list[TextureOptimizationResult] = []

    for index, source in enumerate(files, start=1):
        if _is_quantized(source):
            result = TextureOptimizationResult(source, True, skipped=True)
        else:
            if replace_original:
                output = source.with_name(f"{source.stem}.optimized.png")
                command = ["pngquant", "--quality", quality, "--skip-if-larger", "--output", str(output), str(source)]
            else:
                output = source.with_name(f"{source.stem}.optimized.png")
                command = ["pngquant", "--quality", quality, "--skip-if-larger", "--output", str(output), str(source)]
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
                if replace_original and output.exists():
                    output.replace(source)
                result = TextureOptimizationResult(source, True)
            except (subprocess.CalledProcessError, OSError) as exc:
                error = getattr(exc, "stderr", None) or str(exc)
                result = TextureOptimizationResult(source, False, error=error.strip())
        results.append(result)
        if progress_callback:
            progress_callback(index, len(files))

    return results
