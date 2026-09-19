#!/usr/bin/env python3
"""Build and stage a Vulkan latency layer for a Meson custom target."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) not in (4, 5):
        raise SystemExit(
            "usage: meson-build-cmake-layer.py SOURCE_DIR OUTPUT_LIB OUTPUT_MANIFEST [--m32]"
        )

    source_dir = Path(sys.argv[1]).resolve()
    output_lib = Path(sys.argv[2]).resolve()
    output_manifest = Path(sys.argv[3]).resolve()
    is_32_bit = len(sys.argv) == 5 and sys.argv[4] == "--m32"
    build_dir = output_lib.parent / (".cmake-layer-i386" if is_32_bit else ".cmake-layer")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    configure = [
        "cmake",
        "-S",
        str(source_dir),
        "-B",
        str(build_dir),
        "-DCMAKE_BUILD_TYPE=Release",
    ]
    if is_32_bit:
        configure.extend(
            [
                "-DCMAKE_C_FLAGS=-m32",
                "-DCMAKE_CXX_FLAGS=-m32",
                "-DPB_LAYER_NAME_SUFFIX=_i386",
            ]
        )
    subprocess.run(configure, check=True)
    subprocess.run(["cmake", "--build", str(build_dir), "--config", "Release"], check=True)

    suffix = "_i386" if is_32_bit else ""
    built_lib = build_dir / f"libVkLayer_penguinburner_latency{suffix}.so"
    built_manifest = build_dir / "install" / "VkLayer_PENGUINBURNER_latency.json"
    if not built_lib.is_file() or not built_manifest.is_file():
        raise SystemExit(
            f"CMake did not produce expected layer outputs in {build_dir}"
        )
    output_lib.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(built_lib, output_lib)
    shutil.copy2(built_manifest, output_manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
