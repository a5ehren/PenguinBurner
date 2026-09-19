from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_meson_declares_project_and_native_source_directories() -> None:
    text = (ROOT / "meson.build").read_text(encoding="utf-8")

    assert re.search(r"project\(\s*'penguin-burner'", text)
    assert "burnerd" in text
    assert "'overlay' / 'native' / 'latency_layer'" in text
    assert "'overlay' / 'native' / 'nvapi_shim'" in text


def test_meson_declares_native_build_options() -> None:
    text = (ROOT / "meson.options").read_text(encoding="utf-8")

    for option in (
        "build_native_layer",
        "build_native_layer32",
        "build_nvapi_shim",
        "build_daemon",
    ):
        assert re.search(rf"option\(\s*'{option}'", text)


def test_python_build_backend_uses_meson_python_without_dropping_metadata() -> None:
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    build_system = metadata["build-system"]

    assert build_system["build-backend"] == "mesonpy"
    assert any(requirement.startswith("meson-python") for requirement in build_system["requires"])
    assert metadata["project"]["name"] == "penguin-burner"
    assert metadata["project"]["requires-python"] == ">=3.11"
    assert metadata["project"]["scripts"]["penguin-burner"] == "ui.main:main"
