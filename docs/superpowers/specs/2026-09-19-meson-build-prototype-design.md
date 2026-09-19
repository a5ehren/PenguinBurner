# Meson Build Prototype Design

## Purpose

Prototype a unified Meson build graph for PenguinBurner without changing the
runtime architecture or removing the existing setuptools path. The branch
should make it possible to compare the new build with the current build and
inspect the resulting wheel payload before deciding whether to migrate fully.

## Constraints

- Python remains the primary application language and all existing Python
  packages and console entry points remain installable.
- `burnerd/` remains a standalone privileged Rust executable, not a Python
  extension module.
- Wheel payload paths remain stable:
  `overlay/native_layer/`, `overlay/nvapi_shim/nvapi64.dll`, and
  `runtime/daemon_bin/penguin-burnerd`.
- The Vulkan layer's optional 32-bit build and the NVAPI shim retain their
  current best-effort/release-required behavior.
- The daemon's `--locked` Cargo build remains reproducible.
- Flatpak and native distro packaging remain on their current paths during the
  prototype; the prototype must not require those formats to switch backend.
- No hardware mutation or privileged service installation is part of the
  prototype.

## Design

Add a top-level `meson.build` and a `meson-python` backend to describe the
native artifacts and Python installation layout. Meson owns configuration,
incremental native builds, staging, and installation into the wheel's
platform-library directory. `meson-python` invokes that build through PEP 517.

The native graph has three targets:

1. `penguin-burnerd`: a release Cargo target using the committed lockfile,
   installed into `runtime/daemon_bin/`.
2. The 64-bit Vulkan latency layer, with its JSON manifest, installed into
   `overlay/native_layer/`.
3. The optional 32-bit Vulkan layer and MinGW NVAPI shim, controlled by Meson
   options that map to the existing release requirements.

Pure Python packages, package data, data files, and console scripts remain
declared in `pyproject.toml` and are installed by `meson-python` without
changing import paths. The existing `setup.py` remains in place during the
prototype so current packaging and Flatpak builds are unaffected.

## Compatibility and failure behavior

The prototype must fail when a required release artifact cannot be built, while
allowing local development to omit optional 32-bit and MinGW artifacts. The
wheel inspection must prove that the new backend contains the same required
payload names and executable/file signatures as the existing release checks.

If Meson cannot express a required operation cleanly, the prototype may use a
small explicit helper script, but build ownership must remain in the Meson
graph rather than hidden in setuptools `build_py` hooks.

## Verification

- Meson configure and compile succeed on Linux when the required toolchains are
  available.
- The generated wheel contains the Python entry points and native payloads at
  the stable paths above.
- Existing packaging metadata tests are updated to test the new backend without
  deleting coverage of the compatibility setuptools path.
- Focused tests, the full pytest suite, static analysis, wheel inspection, and
  `git diff --check` are run before the prototype is reported.

## Explicit non-goals

- Migrating Flatpak, Debian, RPM, or AUR build recipes in this prototype.
- Rewriting the Rust daemon or native C/C++ sources.
- Switching to Maturin or making Rust a Python extension module.
- Adding a new runtime dependency or changing supported platforms.
