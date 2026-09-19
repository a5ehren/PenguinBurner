from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def test_meson_declares_locked_daemon_target_and_package_install_path() -> None:
    text = (ROOT / "meson.build").read_text(encoding="utf-8")
    helper = (ROOT / "scripts" / "meson-build-daemon.py").read_text(encoding="utf-8")

    assert re.search(r"custom_target\(\s*'penguin-burnerd'", text)
    assert "cargo" in helper
    assert "build" in helper
    assert "--release" in helper
    assert "--locked" in helper
    assert "Cargo.toml" in helper
    assert "runtime/daemon_bin" in text


def test_meson_declares_64_bit_vulkan_layer_outputs_and_install_path() -> None:
    text = (ROOT / "meson.build").read_text(encoding="utf-8")

    assert re.search(r"custom_target\(\s*'penguinburner-latency-layer'", text)
    assert "libVkLayer_penguinburner_latency.so" in text
    assert "VkLayer_PENGUINBURNER_latency.json" in text
    assert "overlay/native_layer" in text
    assert re.search(r"build_native_layer.*?custom_target", text, re.S)
