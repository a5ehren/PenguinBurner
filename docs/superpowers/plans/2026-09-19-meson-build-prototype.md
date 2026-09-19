# Meson Build Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a parallel Meson/meson-python build path that produces the same Python package and native wheel payloads without removing the existing setuptools path.

**Architecture:** Meson will be the native build graph for the Rust daemon, Vulkan latency layer, optional 32-bit layer, and MinGW NVAPI shim. `meson-python` will expose that graph through PEP 517 while its Python installation metadata preserves the existing package names, data paths, and entry points. Existing Flatpak and distro recipe files remain unchanged, while their source-install commands are validated against the new backend on this branch; `setup.py` remains available for explicit comparison builds.

**Tech Stack:** Meson, meson-python, Python 3.11+, Cargo/Rust 2021, CMake/Vulkan, MinGW-w64, pytest, Python wheel inspection.

**Spec:** `docs/superpowers/specs/2026-09-19-meson-build-prototype-design.md`

## Global Constraints

- Python remains the primary application language and all existing Python packages and console entry points remain installable.
- `burnerd/` remains a standalone privileged Rust executable, not a Python extension module.
- Wheel payload paths remain stable: `overlay/native_layer/`, `overlay/nvapi_shim/nvapi64.dll`, and `runtime/daemon_bin/penguin-burnerd`.
- The Vulkan layer's optional 32-bit build and the NVAPI shim retain their current best-effort/release-required behavior.
- The daemon's `--locked` Cargo build remains reproducible.
- Flatpak and native distro packaging recipe files remain on their current paths during the prototype; their existing `pip install .` source-install command will use the new backend on this branch.
- No hardware mutation or privileged service installation is part of the prototype.

## Review Focus

- Building on Linux without the optional 32-bit compiler must still produce a usable development build; test Meson option defaults and artifact staging.
- A missing Cargo toolchain must fail an explicitly required release build rather than silently producing a daemon-less wheel; test the required path through a deterministic helper boundary.
- A wheel must not place native artifacts outside the package paths used by runtime discovery; test wheel member names and ELF/PE signatures.
- Python-only installs must preserve every existing console script and package-data path; test metadata and importable package coverage.
- Explicit setuptools comparison builds and existing Flatpak/distro recipe invocations must remain callable while the prototype backend is present; test that `setup.py` and recipe references remain available.

### Task 1: Add Meson project metadata and build options

**Files:**
- Create: `meson.build`
- Create: `meson.options`
- Modify: `pyproject.toml` build-system table only
- Test: `tests/test_meson_build_metadata.py`

**Interfaces:**
- Consumes: existing native source directories and `burnerd/Cargo.toml`.
- Produces: Meson options `build_native_layer`, `build_native_layer32`, `build_nvapi_shim`, and `build_daemon`; a configured project named `penguin-burner`.

- [ ] **Step 1: Write the failing metadata tests.** Add tests that load `meson.build` and `meson.options`, assert the four option names exist, assert the project names the Rust/C++ source directories, and assert `pyproject.toml` names `mesonpy` while retaining the existing project metadata.
- [ ] **Step 2: Run the focused tests to verify failure.** Run `python -m pytest tests/test_meson_build_metadata.py -q`; expect failures because the Meson files and backend entry do not yet exist.
- [ ] **Step 3: Add the minimal Meson project declaration.** Define the project, options, source-directory variables, and a Meson version floor compatible with current `meson-python`. Do not add artifact targets yet.
- [ ] **Step 4: Switch only the backend declaration.** Change `[build-system]` to require `meson-python` and use `mesonpy`; leave project dependencies, package metadata, and the setuptools tables intact for now.
- [ ] **Step 5: Run the focused tests.** Run `python -m pytest tests/test_meson_build_metadata.py -q`; expect PASS.
- [ ] **Step 6: Commit.** `git add meson.build meson.options pyproject.toml tests/test_meson_build_metadata.py && git commit -m "build: add Meson project metadata"`

### Task 2: Integrate the Rust daemon and Vulkan layer targets

**Files:**
- Modify: `meson.build`
- Modify: `meson.options`
- Test: `tests/test_meson_native_targets.py`

**Interfaces:**
- Consumes: Task 1 Meson project and option names.
- Produces: Meson targets that stage `runtime/daemon_bin/penguin-burnerd`, `overlay/native_layer/libVkLayer_penguinburner_latency.so`, and `overlay/native_layer/VkLayer_PENGUINBURNER_latency.json`.

- [ ] **Step 1: Write failing target-definition tests.** Assert the build definition contains the locked release Cargo invocation, the Vulkan source directory, the two required 64-bit layer outputs, and install destinations under the Python package tree.
- [ ] **Step 2: Run the focused tests to verify failure.** Run `python -m pytest tests/test_meson_native_targets.py -q`; expect failures for missing target definitions.
- [ ] **Step 3: Implement the Rust target.** Add a Meson custom target/helper that invokes `cargo build --release --locked --manifest-path burnerd/Cargo.toml` and installs the produced executable as package data under `runtime/daemon_bin/`.
- [ ] **Step 4: Implement the Vulkan target.** Add the 64-bit native layer target using the existing CMake source or an equivalent Meson target, install the shared object and JSON manifest beside the Python `overlay` package, and make it required when `build_native_layer=true`.
- [ ] **Step 5: Run a configure/build smoke test.** Run `meson setup --wipe build-meson -Dbuild_native_layer=false -Dbuild_daemon=false`; expect successful configuration. If toolchains are available, run `meson compile -C build-meson` and inspect the target list.
- [ ] **Step 6: Run focused tests.** Run `python -m pytest tests/test_meson_native_targets.py -q`; expect PASS.
- [ ] **Step 7: Commit.** `git add meson.build meson.options tests/test_meson_native_targets.py && git commit -m "build: add Meson daemon and Vulkan targets"`

### Task 3: Add optional 32-bit and MinGW artifact staging

**Files:**
- Modify: `meson.build`
- Modify: `meson.options`
- Test: `tests/test_meson_optional_artifacts.py`

**Interfaces:**
- Consumes: Task 2 target/staging paths.
- Produces: optional `overlay/native_layer/libVkLayer_penguinburner_latency_i386.so`, its i386 manifest, and `overlay/nvapi_shim/nvapi64.dll`; release options can require them.

- [ ] **Step 1: Write failing option and staging tests.** Assert the optional targets use the existing `_i386` names, `-m32` flags, the existing MinGW compiler/source, and separate required options that turn missing outputs into configure/build failures.
- [ ] **Step 2: Run the focused tests to verify failure.** Run `python -m pytest tests/test_meson_optional_artifacts.py -q`; expect failures.
- [ ] **Step 3: Implement optional targets.** Add the 32-bit layer as a conditional target and the NVAPI shim as a conditional custom target using the existing compiler command and source/definition files. Use Meson feature options or explicit booleans so development defaults remain best-effort while release configuration can require the artifacts.
- [ ] **Step 4: Run the focused tests.** Run `python -m pytest tests/test_meson_optional_artifacts.py -q`; expect PASS. Run a configuration with both options disabled to verify it does not require unavailable cross-toolchains.
- [ ] **Step 5: Commit.** `git add meson.build meson.options tests/test_meson_optional_artifacts.py && git commit -m "build: stage optional native artifacts with Meson"`

### Task 4: Make meson-python install the full Python package and wheel

**Files:**
- Modify: `meson.build`
- Modify: `pyproject.toml`
- Test: `tests/test_meson_wheel.py`
- Create: `scripts/inspect-meson-wheel.py`

**Interfaces:**
- Consumes: Tasks 1–3 staged artifact paths.
- Produces: a PEP 517 wheel whose Python modules, console scripts, package data, desktop files, icons, and native payloads match the existing runtime contract.

- [ ] **Step 1: Write failing wheel inspection tests.** Add a test helper that opens a wheel and asserts the four console scripts, representative Python packages, desktop/icon data, native layer files, NVAPI DLL, daemon ELF, and `py3-none` platform-wheel behavior.
- [ ] **Step 2: Run the focused tests to verify failure.** Run `python -m pytest tests/test_meson_wheel.py -q`; expect no valid Meson wheel or missing payload failures.
- [ ] **Step 3: Declare Python installation in Meson.** Install the existing package directories, `penguin_burner.py`, package assets, `penguin_burner.sh`, desktop file, icons, and entry-point wrappers into the same paths currently defined by setuptools. Ensure native targets install into package-relative directories.
- [ ] **Step 4: Add the inspection script.** Implement `scripts/inspect-meson-wheel.py` using only the standard library; it must report missing members and validate ELF/PE magic bytes without modifying the wheel.
- [ ] **Step 5: Build and inspect the wheel.** Run `python -m build --wheel --outdir dist/meson` with development-friendly optional targets disabled or available. Run `python scripts/inspect-meson-wheel.py dist/meson/*.whl`; expect a successful payload report.
- [ ] **Step 6: Run focused tests.** Run `python -m pytest tests/test_meson_wheel.py -q`; expect PASS.
- [ ] **Step 7: Commit.** `git add meson.build pyproject.toml scripts/inspect-meson-wheel.py tests/test_meson_wheel.py && git commit -m "build: package Python and native outputs with Meson"`

### Task 5: Preserve compatibility workflows and document the prototype

**Files:**
- Modify: `docs/install.md`
- Modify: `README.md`
- Modify: `tests/test_packaging_metadata.py`
- Modify: `tests/test_release_workflow.py` only if backend assumptions require an assertion update
- Test: existing focused packaging tests plus `tests/test_meson_build_metadata.py`

**Interfaces:**
- Consumes: Meson backend and inspection command from Tasks 1–4.
- Produces: documented developer/release commands and explicit proof that legacy Flatpak/distro recipe paths remain unchanged while their source-install command exercises the Meson backend.

- [ ] **Step 1: Write failing documentation/compatibility assertions.** Add assertions for the documented Meson setup/build commands, the unchanged `setup.py` comparison path, and the unchanged Flatpak build references.
- [ ] **Step 2: Run the focused tests to verify failure.** Run `python -m pytest tests/test_packaging_metadata.py tests/test_meson_build_metadata.py -q`; expect documentation/backend assertions to fail.
- [ ] **Step 3: Update user-facing build documentation.** Add a “Meson prototype” section with the virtualenv, `meson setup`, `meson compile`, and `python -m build` commands, plus a clear note that Flatpak/distro recipe files are unchanged but their `pip install .` source install now uses Meson on this branch; `python setup.py bdist_wheel` remains the explicit comparison path.
- [ ] **Step 4: Update packaging tests without deleting old contract coverage.** Change only assertions that assume setuptools is the sole backend; retain tests for existing package paths, entry points, Flatpak commands, and release scripts.
- [ ] **Step 5: Run focused tests.** Run `python -m pytest tests/test_packaging_metadata.py tests/test_meson_build_metadata.py tests/test_meson_native_targets.py tests/test_meson_optional_artifacts.py tests/test_meson_wheel.py -q`; expect PASS.
- [ ] **Step 6: Commit.** `git add README.md docs/install.md tests/test_packaging_metadata.py tests/test_release_workflow.py && git commit -m "docs: describe Meson build prototype"`

### Task 6: Full verification and branch handoff

**Files:**
- Modify: only files required by verification fixes from Tasks 1–5.

- [ ] **Step 1: Run the full test suite.** `python -m pytest tests/ -q`; fix failures caused by the conversion using test-first changes.
- [ ] **Step 2: Run static analysis.** `scripts/check-feature-static-analysis.sh`; resolve new diagnostics in touched files.
- [ ] **Step 3: Rebuild and inspect.** Run the Meson configure/compile flow, build the wheel, run `scripts/inspect-meson-wheel.py`, and record whether hardware/live daemon validation was not run.
- [ ] **Step 4: Review the final diff.** Run `git diff --check`, `git status -sb`, and `git diff main...HEAD --stat`; confirm generated build outputs are ignored and no unrelated files changed.
- [ ] **Step 5: Commit verification fixes if needed.** Use a focused message such as `fix: address Meson prototype verification findings`.
