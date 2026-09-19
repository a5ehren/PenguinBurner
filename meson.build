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

message('burnerd source: ' + burnerd_source_dir)
message('Vulkan layer source: ' + native_layer_source_dir)
message('NVAPI shim source: ' + nvapi_shim_source_dir)
