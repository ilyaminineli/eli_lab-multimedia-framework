"""Texture conversion services independent of any GUI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image

ALLOWED_TEXTURE_EXTENSIONS = (
    ".jpg", ".jpeg", ".tga", ".exr", ".hdr", ".bmp", ".gif", ".tiff", ".tif", ".png"
)


@dataclass(frozen=True, slots=True)
class TextureConversionResult:
    """Outcome of converting one texture."""

    source: Path
    output: Path | None
    success: bool
    error: str | None = None


def is_texture_file(path: str | Path) -> bool:
    return Path(path).suffix.lower() in ALLOWED_TEXTURE_EXTENSIONS


def convert_texture_to_png(
    filepath: str | Path,
    output_dir: str | Path | None = None,
    *,
    replace_original: bool = False,
) -> TextureConversionResult:
    """Convert one supported image to PNG.

    The source is preserved unless ``replace_original`` is explicitly enabled.
    PNG sources are skipped because conversion would be a no-op.
    """
    source = Path(filepath).expanduser().resolve()
    destination_dir = Path(output_dir).expanduser().resolve() if output_dir else source.parent

    if not source.is_file():
        return TextureConversionResult(source, None, False, "Source file does not exist")
    if not is_texture_file(source):
        return TextureConversionResult(source, None, False, "Unsupported texture format")
    if source.suffix.lower() == ".png":
        return TextureConversionResult(source, source, False, "Source is already PNG")

    destination_dir.mkdir(parents=True, exist_ok=True)
    output = destination_dir / f"{source.stem}.png"

    try:
        with Image.open(source) as image:
            image.save(output, "PNG")
        if replace_original:
            source.unlink()
        return TextureConversionResult(source, output, True)
    except (OSError, ValueError) as exc:
        return TextureConversionResult(source, None, False, str(exc))


def convert_textures(
    directory: str | Path,
    *,
    replace_original: bool = False,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[TextureConversionResult]:
    """Convert supported textures in one directory, returning per-file results."""
    root = Path(directory).expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)

    files = sorted(path for path in root.iterdir() if path.is_file() and is_texture_file(path))
    results: list[TextureConversionResult] = []
    total = len(files)
    for index, path in enumerate(files, start=1):
        result = convert_texture_to_png(path, root, replace_original=replace_original)
        results.append(result)
        if progress_callback:
            progress_callback(index, total)
    return results
