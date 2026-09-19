#!/usr/bin/env python3
"""Build and stage the Rust daemon for a Meson custom target."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: meson-build-daemon.py BURNERD_DIR OUTPUT")

    source_dir = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    manifest = source_dir / "Cargo.toml"
    subprocess.run(
        [
            "cargo",
            "build",
            "--release",
            "--locked",
            "--manifest-path",
            str(manifest),
        ],
        check=True,
    )
    built = source_dir / "target" / "release" / "penguin-burnerd"
    if not built.is_file():
        raise SystemExit(f"cargo did not produce {built}")
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(built, output)
    output.chmod(0o755)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
