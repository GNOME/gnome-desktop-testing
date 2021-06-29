# Copyright 2021 Collabora Ltd.
# SPDX-License-Identifier: LGPL-2.0-or-later

project(
  'gnome-desktop-testing',
  'c',
  version : '2018.1',
  meson_version : '>=0.49.0',
  default_options : [
    'warning_level=2',
  ],
)

cc = meson.get_compiler('c')

add_project_arguments(
  cc.get_supported_arguments([
    '-Werror=aggregate-return',
    '-Werror=empty-body',
    '-Werror=implicit-function-declaration',
    '-Werror=incompatible-pointer-types',
    '-Werror=init-self',
    '-Werror=int-conversion',
    '-Werror=misleading-indentation',
    '-Werror=missing-declarations',
    '-Werror=missing-include-dirs',
    '-Werror=missing-prototypes',
    '-Werror=overflow',
    '-Werror=parenthesis',
    '-Werror=pointer-arith',
    '-Werror=return-type',
    '-Werror=shadow',
    '-Werror=strict-prototypes',
    '-Werror=switch-default',
    '-Wswitch-enum',

    # deliberately not warning about these
    '-Wno-declaration-after-statement',
    '-Wno-missing-field-initializers',
    '-Wno-unused-parameter',
    '-Wno-error=declaration-after-statement',
    '-Wno-error=missing-field-initializers',
    '-Wno-error=unused-parameter',
  ]),
  language : 'c',
)

if (
  cc.has_argument('-Werror=format=2')
  and cc.has_argument('-Werror=format-security')
  and cc.has_argument('-Werror=format-nonliteral')
)
  add_project_arguments([
    '-Werror=format=2',
    '-Werror=format-security',
    '-Werror=format-nonliteral',
  ], language : 'c')
endif

include_dirs = include_directories('.')

gio_unix_dep = dependency('gio-unix-2.0', version : '>=2.50')
libsystemd_dep = dependency('libsystemd', required : get_option('systemd'))

cdata = configuration_data()
cdata.set_quoted('DATADIR', get_option('prefix') / get_option('datadir'))
cdata.set_quoted('LIBEXECDIR', get_option('prefix') / get_option('libexecdir'))
cdata.set('GLIB_VERSION_MAX_ALLOWED', 'GLIB_VERSION_2_50')
cdata.set('GLIB_VERSION_MIN_REQUIRED', 'GLIB_VERSION_2_50')

if libsystemd_dep.found()
  cdata.set('HAVE_SYSTEMD', 1)
endif

configure_file(
  output : 'config.h',
  configuration : cdata,
)

executable(
  'gnome-desktop-testing-runner',
  ['src/gnome-desktop-testing-runner.c'],
  include_directories : include_dirs,
  install : true,
  dependencies : [gio_unix_dep, libsystemd_dep],
)

install_man(
  ['gnome-desktop-testing-runner.1'],
)

meson.add_install_script(
  'install-hook.py',
  get_option('bindir'),
  get_option('mandir'),
)
