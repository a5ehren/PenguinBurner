#!/usr/bin/env python3
"""Build and stage the MinGW NVAPI shim for a Meson custom target."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: meson-build-nvapi-shim.py SOURCE_DIR OUTPUT COMPILER")

    source_dir = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    compiler = sys.argv[3]
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            compiler,
            "-O2",
            "-shared",
            "-std=c++17",
            "-fno-exceptions",
            "-fno-rtti",
            "-static",
            "-static-libgcc",
            "-static-libstdc++",
            "-Wall",
            "-Wextra",
            "-o",
            str(output),
            str(source_dir / "src" / "nvapi_shim.cpp"),
            str(source_dir / "nvapi64.def"),
            "-lkernel32",
        ],
        check=True,
    )
    if not output.is_file():
        raise SystemExit(f"MinGW did not produce {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
