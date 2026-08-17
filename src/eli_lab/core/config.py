"""Framework configuration models."""

from dataclasses import dataclass
from pathlib import Path

from .paths import BLENDER_TEMPLATES_ROOT


@dataclass(frozen=True)
class FrameworkConfig:
    """Runtime configuration shared by framework tools."""

    blender_templates_root: Path = BLENDER_TEMPLATES_ROOT
    pngquant_command: str = "pngquant"


DEFAULT_CONFIG = FrameworkConfig()
