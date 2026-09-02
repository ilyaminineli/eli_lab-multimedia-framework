"""Texture conversion services."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from PIL import Image

IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".tga", ".exr", ".hdr", ".bmp", ".gif", ".tiff", ".tif", ".png"})


@dataclass(frozen=True, slots=True)
class ConversionResult:
    source: Path
    destination: Path | None
    converted: bool
    error: str | None = None


def is_image_file(path: str | Path) -> bool:
    return Path(path).suffix.lower() in IMAGE_EXTENSIONS


def iter_images(directory: str | Path, *, recursive: bool = False) -> Iterator[Path]:
    root = Path(directory).expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)
    paths = root.rglob("*") if recursive else root.glob("*")
    yield from (path for path in sorted(paths) if path.is_file() and is_image_file(path))


def convert_texture(source: str | Path, *, output_dir: str | Path | None = None) -> ConversionResult:
    source_path = Path(source).expanduser().resolve()
    if not source_path.is_file() or not is_image_file(source_path) or source_path.suffix.lower() == ".png":
        return ConversionResult(source_path, None, False)

    destination_dir = Path(output_dir).expanduser().resolve() if output_dir else source_path.parent
    destination = destination_dir / f"{source_path.stem}.png"
    destination_dir.mkdir(parents=True, exist_ok=True)

    try:
        with Image.open(source_path) as image:
            image.save(destination, "PNG")
    except (OSError, ValueError) as exc:
        return ConversionResult(source_path, destination, False, str(exc))

    return ConversionResult(source_path, destination, True)


def convert_directory(directory: str | Path, *, recursive: bool = False, replace_original: bool = False) -> list[ConversionResult]:
    """Convert supported non-PNG images to PNG.

    Source files are preserved by default. Deleting originals is explicit.
    """
    results = []
    for source in iter_images(directory, recursive=recursive):
        result = convert_texture(source)
        results.append(result)
        if replace_original and result.converted and result.destination:
            try:
                source.unlink()
            except OSError as exc:
                results[-1] = ConversionResult(source, result.destination, False, str(exc))
    return results
