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
mingw_cxx = 'x86_64-w64-mingw32-g++'
python = import('python').find_installation()
python_install_dir = python.get_install_dir(pure: false)

python_packages = [
  'auto_uv',
  'cli',
  'common',
  'curve_editors',
  'drivers',
  'integrations',
  'overlay',
  'profiles',
  'runtime',
  'stability',
  'ui',
]
foreach package : python_packages
  package_excludes = ['__pycache__']
  pycache_dirs = run_command(
    'find', package, '-type', 'd', '-name', '__pycache__', '-printf', '%P\\n',
    check: true,
  ).stdout().strip().split('\n')
  foreach pycache_dir : pycache_dirs
    if pycache_dir != ''
      package_excludes += [pycache_dir]
    endif
  endforeach
  if package == 'overlay'
    package_excludes += ['native']
  endif
  install_subdir(
    package,
    install_dir: python_install_dir,
    exclude_directories: package_excludes,
  )
endforeach
python.install_sources('penguin_burner.py', pure: false)
install_data('penguin_burner.sh', install_dir: get_option('datadir') / 'penguin-burner')
install_data(
  'packaging/linux/io.github.jpietek.PenguinBurner.desktop',
  install_dir: get_option('datadir') / 'applications',
)
install_data(
  'packaging/icons/hicolor/256x256/apps/penguin-burner.png',
  install_dir: get_option('datadir') / 'icons/hicolor/256x256/apps',
)
install_data(
  'packaging/icons/hicolor/512x512/apps/penguin-burner.png',
  install_dir: get_option('datadir') / 'icons/hicolor/512x512/apps',
)

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
    install_dir: python.get_install_dir(pure: false, subdir: 'runtime/daemon_bin'),
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
    install_dir: [
      python.get_install_dir(pure: false, subdir: 'overlay/native_layer'),
      python.get_install_dir(pure: false, subdir: 'overlay/native_layer'),
    ],
  )
endif

if get_option('build_native_layer32')
  custom_target(
    'penguinburner-latency-layer-i386',
    output: [
      'libVkLayer_penguinburner_latency_i386.so',
      'VkLayer_PENGUINBURNER_latency.i386.json',
    ],
    command: [
      python,
      project_root / 'scripts' / 'meson-build-cmake-layer.py',
      native_layer_source_dir,
      '@OUTPUT0@',
      '@OUTPUT1@',
      '--m32',
    ],
    build_by_default: true,
    install: true,
    install_dir: [
      python.get_install_dir(pure: false, subdir: 'overlay/native_layer'),
      python.get_install_dir(pure: false, subdir: 'overlay/native_layer'),
    ],
  )
endif

if get_option('build_nvapi_shim')
  custom_target(
    'penguinburner-nvapi-shim',
    output: 'nvapi64.dll',
    command: [
      python,
      project_root / 'scripts' / 'meson-build-nvapi-shim.py',
      nvapi_shim_source_dir,
      '@OUTPUT@',
      mingw_cxx,
    ],
    build_by_default: true,
    install: true,
    install_dir: python.get_install_dir(pure: false, subdir: 'overlay/nvapi_shim'),
  )
endif
