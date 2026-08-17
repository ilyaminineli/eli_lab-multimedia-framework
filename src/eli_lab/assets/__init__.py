"""Asset-processing services for the ELI LAB multimedia framework."""

from .textures import (
    ALLOWED_TEXTURE_EXTENSIONS,
    TextureConversionResult,
    convert_texture_to_png,
    convert_textures,
    is_texture_file,
)
from .optimization import (
    PNGQUANT_QUALITY_PRESETS,
    TextureOptimizationResult,
    optimize_textures,
    pngquant_available,
)

__all__ = [
    "ALLOWED_TEXTURE_EXTENSIONS",
    "PNGQUANT_QUALITY_PRESETS",
    "TextureConversionResult",
    "TextureOptimizationResult",
    "convert_texture_to_png",
    "convert_textures",
    "is_texture_file",
    "optimize_textures",
    "pngquant_available",
    "PNGQUANT_QUALITY_PRESETS",
]
