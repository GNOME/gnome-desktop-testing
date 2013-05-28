# Copyright (C) 2011 Colin Walters <walters@verbum.org>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}
AM_CPPFLAGS = -DDATADIR='"$(datadir)"' -DLIBEXECDIR='"$(libexecdir)"'
AM_CFLAGS = $(WARN_CFLAGS)

NULL = 
BUILT_SOURCES =
MANPAGES =
CLEANFILES =
EXTRA_DIST =
bin_PROGRAMS =
sbin_PROGRAMS =
bin_SCRIPTS =
libexec_PROGRAMS =
noinst_LTLIBRARIES =
noinst_PROGRAMS =
privlibdir = $(pkglibdir)
privlib_LTLIBRARIES =
privlib_DATA =
INSTALL_DATA_HOOKS =

libgsystem_srcpath := src/libgsystem
libgsystem_cflags = $(GIO_UNIX_CFLAGS) $(SYSTEMD_JOURNAL_CFLAGS) -I$(srcdir)/src/libgsystem
libgsystem_libs = $(GIO_UNIX_LIBS) $(SYSTEMD_JOURNAL_LIBS)
include src/libgsystem/Makefile-libgsystem.am
privlib_LTLIBRARIES += libgsystem.la

include Makefile-runner.am

install-data-hook: $(INSTALL_DATA_HOOKS)

release-tag:
	git tag -m "Release $(VERSION)" v$(VERSION)
