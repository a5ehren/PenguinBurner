#!/usr/bin/env python3
"""Verify the runtime payload of a Meson-built PenguinBurner wheel."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import zipfile


REQUIRED_PAYLOADS = {
    "daemon": ("runtime/daemon_bin/penguin-burnerd", b"\x7fELF"),
    "Vulkan layer": (
        "overlay/native_layer/libVkLayer_penguinburner_latency.so",
        b"\x7fELF",
    ),
    "Vulkan manifest": (
        "overlay/native_layer/VkLayer_PENGUINBURNER_latency.json",
        None,
    ),
    "NVAPI shim": ("overlay/nvapi_shim/nvapi64.dll", b"MZ"),
}


def inspect(wheel: Path) -> list[str]:
    errors: list[str] = []
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        entry_points = [
            name for name in names if name.endswith(".dist-info/entry_points.txt")
        ]
        if len(entry_points) != 1:
            errors.append("wheel must contain exactly one entry_points.txt")
        else:
            scripts = archive.read(entry_points[0]).decode("utf-8")
            for name in (
                "penguin-burner",
                "pburn",
                "penguin-burner-cli",
                "pburn-cli",
            ):
                if f"{name} = " not in scripts:
                    errors.append(f"missing console script: {name}")

        for label, (member, magic) in REQUIRED_PAYLOADS.items():
            if member not in names:
                errors.append(f"missing {label}: {member}")
            elif magic is not None and not archive.read(member).startswith(magic):
                errors.append(f"invalid {label} signature: {member}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path)
    args = parser.parse_args()
    errors = inspect(args.wheel)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"verified Meson wheel: {args.wheel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
