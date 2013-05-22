AC_PREREQ([2.63])
AC_INIT([gnome-desktop-testing], [2013.1], [walters@verbum.org], [gnome-desktop-testing], [https://live.gnome.org/OSTree/GnomeOSTree])
AC_CONFIG_HEADER([config.h])
AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_AUX_DIR([build-aux])

AM_INIT_AUTOMAKE([1.11 -Wno-portability foreign no-define tar-ustar no-dist-gzip dist-xz])
AM_MAINTAINER_MODE([enable])
AM_SILENT_RULES([yes])

AC_PROG_CC
AM_PROG_CC_C_O

changequote(,)dnl
if test "x$GCC" = "xyes"; then
  WARN_CFLAGS="-Wall -Werror=strict-prototypes -Werror=missing-prototypes \
		-Werror=implicit-function-declaration \
		-Werror=pointer-arith -Werror=init-self -Werror=format=2 \
		-Werror=format-security \
		-Werror=missing-include-dirs -Werror=aggregate-return \
		-Werror=declaration-after-statement"
fi
changequote([,])dnl
AC_SUBST(WARN_CFLAGS)

# Initialize libtool
LT_PREREQ([2.2.4])
LT_INIT([disable-static])

GOBJECT_INTROSPECTION_REQUIRE([1.34.0])

PKG_CHECK_MODULES(GIO_UNIX, [gio-unix-2.0 >= 2.34.0])
GIO_UNIX_CFLAGS="$GIO_UNIX_CFLAGS -DGLIB_VERSION_MIN_REQUIRED=GLIB_VERSION_2_36 -DGLIB_VERSION_MAX_ALLOWED=GLIB_VERSION_2_36"

AC_ARG_WITH(systemd-journal,
	    AS_HELP_STRING([--without-systemd-journal], [Use systemd @<:@default=auto@:>@]),
	    [], [with_systemd_journal=auto])
AS_IF([test x$with_systemd_journal != xno], [
  PKG_CHECK_MODULES([SYSTEMD_JOURNAL], [libsystemd-journal >= 200], have_systemd_journal=yes, have_systemd_journal=no)
  ])
AM_CONDITIONAL(ENABLE_SYSTEMD_JOURNAL, test x$have_systemd_journal = xyes)
AS_IF([test x$have_systemd_journal = xyes], [
  AC_DEFINE([ENABLE_SYSTEMD_JOURNAL],[1],[Define if you want to build with systemd journal support])
])

AC_CONFIG_FILES([
Makefile
])
AC_OUTPUT

echo "
    $PACKAGE $VERSION
"
