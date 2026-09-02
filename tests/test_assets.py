from pathlib import Path

from PIL import Image

from eli_lab.assets.textures import convert_texture, is_image_file


def test_image_extension_detection() -> None:
    assert is_image_file("texture.PNG")
    assert not is_image_file("scene.blend")


def test_texture_conversion(tmp_path: Path) -> None:
    source = tmp_path / "texture.jpg"
    Image.new("RGB", (4, 4), (255, 0, 0)).save(source)
    result = convert_texture(source)
    assert result.converted
    assert result.destination == tmp_path / "texture.png"
    assert result.destination.is_file()
