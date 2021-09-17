#!/usr/bin/env python3
# Copyright 2021 Collabora Ltd.
# SPDX-License-Identifier: LGPL-2.0-or-later

import os
import sys

os.symlink(
    'gnome-desktop-testing-runner',
    os.path.join(
        os.environ['MESON_INSTALL_DESTDIR_PREFIX'],
        sys.argv[1],
        'ginsttest-runner',
    )
)
os.symlink(
    'gnome-desktop-testing-runner',
    os.path.join(
        os.environ['MESON_INSTALL_DESTDIR_PREFIX'],
        sys.argv[2],
        'man1',
        'ginsttest-runner.1',
    )
)
