project(
  'penguin-burner',
  ['c', 'cpp', 'rust'],
  version: '0.8.0',
  meson_version: '>=1.2.0',
)

project_root = meson.project_source_root()
burnerd_source_dir = project_root / 'burnerd'
native_layer_source_dir = project_root / 'overlay' / 'native' / 'latency_layer'
nvapi_shim_source_dir = project_root / 'overlay' / 'native' / 'nvapi_shim'
python = import('python').find_installation()

message('burnerd source: ' + burnerd_source_dir)
message('Vulkan layer source: ' + native_layer_source_dir)
message('NVAPI shim source: ' + nvapi_shim_source_dir)

if get_option('build_daemon')
  custom_target(
    'penguin-burnerd',
    output: 'penguin-burnerd',
    command: [
      python,
      project_root / 'scripts' / 'meson-build-daemon.py',
      burnerd_source_dir,
      '@OUTPUT@',
    ],
    build_by_default: true,
    install: true,
    install_dir: 'runtime/daemon_bin',
  )
endif

if get_option('build_native_layer')
  custom_target(
    'penguinburner-latency-layer',
    output: [
      'libVkLayer_penguinburner_latency.so',
      'VkLayer_PENGUINBURNER_latency.json',
    ],
    command: [
      python,
      project_root / 'scripts' / 'meson-build-cmake-layer.py',
      native_layer_source_dir,
      '@OUTPUT0@',
      '@OUTPUT1@',
    ],
    build_by_default: true,
    install: true,
    install_dir: ['overlay/native_layer', 'overlay/native_layer'],
  )
endif
