from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_meson_declares_optional_i386_layer_with_existing_contract() -> None:
    text = (ROOT / "meson.build").read_text(encoding="utf-8")
    helper = (ROOT / "scripts" / "meson-build-cmake-layer.py").read_text(
        encoding="utf-8"
    )

    assert re.search(r"if get_option\('build_native_layer32'\)", text)
    assert "libVkLayer_penguinburner_latency_i386.so" in text
    assert "VkLayer_PENGUINBURNER_latency.i386.json" in text
    assert "--m32" in text
    assert "-DCMAKE_C_FLAGS=-m32" in helper
    assert "-DCMAKE_CXX_FLAGS=-m32" in helper
    assert "-DPB_LAYER_NAME_SUFFIX=_i386" in helper


def test_meson_declares_optional_nvapi_shim_with_strict_enable_mode() -> None:
    text = (ROOT / "meson.build").read_text(encoding="utf-8")
    assert re.search(r"if get_option\('build_nvapi_shim'\)", text)
    assert "nvapi64.dll" in text
    assert "x86_64-w64-mingw32-g++" in text
    assert "nvapi_shim" in text


def test_optional_targets_default_to_disabled_development_mode() -> None:
    text = (ROOT / "meson.options").read_text(encoding="utf-8")
    for option in ("build_native_layer32", "build_nvapi_shim"):
        match = re.search(
            rf"option\(\s*'{option}'.*?value:\s*(true|false)", text, re.DOTALL
        )
        assert match and match.group(1) == "false"
