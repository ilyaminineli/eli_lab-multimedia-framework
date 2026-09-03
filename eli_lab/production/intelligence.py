"""Production intelligence for assets, materials, textures and dependencies."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".exr", ".webp", ".bmp"}
BLENDER_EXTENSIONS = {".blend", ".blend1"}


@dataclass(frozen=True, slots=True)
class TextureInfo:
    path: Path
    stem: str
    channel: str | None
    resolution_hint: str | None


@dataclass(frozen=True, slots=True)
class TextureSet:
    name: str
    files: tuple[TextureInfo, ...]
    missing_channels: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Dependency:
    source: Path
    target: Path
    kind: str


CHANNEL_PATTERNS = {
    "base_color": (
        "basecolor",
        "base_color",
        "diffuse",
        "albedo",
        "color",
        "colour",
        "_col",
    ),
    "normal": ("normal", "nor_gl", "nor", "nrm"),
    "roughness": ("roughness", "rough", "smoothness", "smooth"),
    "metallic": ("metallic", "metalness", "metal"),
    "height": ("height", "displacement", "disp", "bump"),
    "ao": ("ambientocclusion", "ao"),
    "opacity": ("opacity", "alpha", "mask"),
}


def _channel_for(stem: str) -> str | None:
    lowered = re.sub(r"[^a-z0-9]+", "_", stem.casefold())
    for channel, tokens in CHANNEL_PATTERNS.items():
        if any(token in lowered for token in tokens):
            return channel
    return None


def _resolution_for(stem: str) -> str | None:
    match = re.search(r"(?:^|[_ -])(\d{1,2}k)(?:$|[_ -])", stem.casefold())
    return match.group(1).upper() if match else None


def inspect_texture(path: str | Path) -> TextureInfo:
    source = Path(path)
    return TextureInfo(
        source, source.stem, _channel_for(source.stem), _resolution_for(source.stem)
    )


def group_texture_set(paths: list[str | Path]) -> TextureSet:
    infos = tuple(inspect_texture(path) for path in paths)
    channels = {info.channel for info in infos if info.channel}
    name_source = infos[0].stem if infos else "Texture Set"
    name = (
        re.sub(
            r"(?:[_ -]?)(?:basecolor|base_color|diffuse|albedo|color|colour|normal|roughness|rough|metallic|metalness|height|displacement|disp|bump|ao|opacity|alpha|mask)(?:[_ -]?\d{1,2}k)?$",
            "",
            name_source,
            flags=re.I,
        ).strip(" _-")
        or name_source
    )
    expected = {"base_color", "normal", "roughness"}
    return TextureSet(name, infos, tuple(sorted(expected - channels)))


def discover_texture_sets(root: str | Path) -> list[TextureSet]:
    root_path = Path(root).expanduser().resolve()
    groups: dict[str, list[Path]] = {}
    for path in root_path.rglob("*"):
        if path.is_file() and path.suffix.casefold() in IMAGE_EXTENSIONS:
            info = inspect_texture(path)
            key = (
                re.sub(
                    r"(?:[_ -]?)(?:basecolor|base_color|diffuse|albedo|color|colour|normal|roughness|rough|metallic|metalness|height|displacement|disp|bump|ao|opacity|alpha|mask)(?:[_ -]?\d{1,2}k)?$",
                    "",
                    info.stem,
                    flags=re.I,
                )
                .strip(" _-")
                .casefold()
            )
            groups.setdefault(key or info.stem.casefold(), []).append(path)
    return [group_texture_set(paths) for paths in groups.values()]


def discover_dependencies(root: str | Path) -> list[Dependency]:
    """Infer useful file relationships from relative path conventions."""
    root_path = Path(root).expanduser().resolve()
    dependencies: list[Dependency] = []
    for blend in root_path.rglob("*.blend"):
        for texture in blend.parent.rglob("*"):
            if texture.is_file() and texture.suffix.casefold() in IMAGE_EXTENSIONS:
                dependencies.append(
                    Dependency(
                        blend.relative_to(root_path),
                        texture.relative_to(root_path),
                        "nearby-texture",
                    )
                )
    return dependencies
