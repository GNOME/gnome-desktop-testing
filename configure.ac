AC_PREREQ([2.63])
AC_INIT([gnome-desktop-testing], [2021.1], [walters@verbum.org], [gnome-desktop-testing], [https://wiki.gnome.org/Initiatives/GnomeGoals/InstalledTests/])
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
		-Werror=switch-default -Wswitch-enum -Wsign-compare \
		-Werror=declaration-after-statement"
fi
changequote([,])dnl
AC_SUBST(WARN_CFLAGS)

# Initialize libtool
LT_PREREQ([2.2.4])
LT_INIT([disable-static])

PKG_CHECK_MODULES(BUILDDEP_GDT, [gio-unix-2.0 >= 2.50])
PKG_CHECK_MODULES([SYSTEMD], [libsystemd], [have_systemd=yes], [have_systemd=no])
AS_IF([test "x$have_systemd" = xyes], [AC_DEFINE([HAVE_SYSTEMD], [1], [Define if you have libsystemd])])
BUILDDEP_GDT_CFLAGS="$BUILDDEP_GDT_CFLAGS -DGLIB_VERSION_MIN_REQUIRED=GLIB_VERSION_2_50 -DGLIB_VERSION_MAX_ALLOWED=GLIB_VERSION_2_50"

AC_CONFIG_FILES([
Makefile
])
AC_OUTPUT

echo "
    $PACKAGE $VERSION
"
