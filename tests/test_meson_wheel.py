from __future__ import annotations

import glob
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _wheel() -> Path:
    wheels = sorted(Path(path) for path in glob.glob(str(ROOT / "dist/meson/*.whl")))
    assert len(wheels) == 1, f"expected one Meson wheel, found {wheels}"
    return wheels[0]


def test_meson_wheel_contains_python_entry_points_and_package_data() -> None:
    wheel = _wheel()
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        metadata = next(name for name in names if name.endswith(".dist-info/METADATA"))
        entry_points = next(
            name for name in names if name.endswith(".dist-info/entry_points.txt")
        )

        assert "auto_uv/__init__.py" in names
        assert "ui/__init__.py" in names
        assert "penguin_burner.py" in names
        assert "ui/assets" in "\n".join(names)
        assert not any("__pycache__/" in name for name in names)
        assert not any(name.startswith("overlay/native/") for name in names)
        assert any(
            name.endswith(".data/data/penguin-burner/penguin_burner.sh")
            for name in names
        )
        assert any(
            name.endswith(
                ".data/data/applications/io.github.jpietek.PenguinBurner.desktop"
            )
            for name in names
        )
        assert any(
            name.endswith(".data/data/icons/hicolor/256x256/apps/penguin-burner.png")
            for name in names
        )
        assert any(
            name.endswith(".data/data/icons/hicolor/512x512/apps/penguin-burner.png")
            for name in names
        )
        assert "Name: penguin-burner" in archive.read(metadata).decode()
        scripts = archive.read(entry_points).decode()
        for name in (
            "penguin-burner",
            "pburn",
            "penguin-burner-cli",
            "pburn-cli",
        ):
            assert f"{name} = " in scripts


def test_meson_wheel_contains_native_payloads_at_runtime_paths() -> None:
    wheel = _wheel()
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        daemon = "runtime/daemon_bin/penguin-burnerd"
        layer = "overlay/native_layer/libVkLayer_penguinburner_latency.so"
        manifest = "overlay/native_layer/VkLayer_PENGUINBURNER_latency.json"
        shim = "overlay/nvapi_shim/nvapi64.dll"
        assert daemon in names and archive.read(daemon).startswith(b"\x7fELF")
        assert layer in names and archive.read(layer).startswith(b"\x7fELF")
        assert manifest in names
        assert shim in names and archive.read(shim).startswith(b"MZ")
    assert "-any.whl" not in wheel.name
