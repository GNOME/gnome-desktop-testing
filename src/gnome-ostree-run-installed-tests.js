#!/usr/bin/env gjs

// Copyright (C) 2012,2013 Colin Walters <walters@verbum.org>
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 2 of the License, or (at your option) any later version.
//
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public
// License along with this library; if not, write to the
// Free Software Foundation, Inc., 59 Temple Place - Suite 330,
// Boston, MA 02111-1307, USA.


const GLib = imports.gi.GLib;
const Gio = imports.gi.Gio;
const GSystem = imports.gi.GSystem;

const TESTS_FAILED_MSGID = '0eee66bf98514369bef9868327a43cf1';
const TESTS_SUCCESS_MSGID = '4d013788dd704743b826436c951e551d';

const INSTALLED_TEST_SUFFIX = '-installed-tests';

let cancellable = null;
let e = Gio.File.new_for_path('/usr/bin').enumerate_children('standard::name,standard::type', Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS, cancellable);
let info;
let loop = GLib.MainLoop.new(null, true);
let ntests = 0;
let testSuccess = true;
while ((info = e.next_file(cancellable)) != null) {
    let name = info.get_name();
    let i = name.lastIndexOf(INSTALLED_TEST_SUFFIX);
    if (i == -1 || i != name.length - INSTALLED_TEST_SUFFIX.length)
	continue;
    let child = e.get_child(info);
    ntests += 1;
    print("Running test: " + child.get_path());
    let [success,pid] = GLib.spawn_async (null, [child.get_path()], null,
					  GLib.SpawnFlags.DO_NOT_REAP_CHILD, null);
    let errmsg = null;
    GLib.child_watch_add(GLib.PRIORITY_DEFAULT, pid, function(pid, estatus) {
	try {
	    GLib.spawn_check_exit_status(estatus);
	} catch (e) {
	    errmsg = e.message;
	    testSuccess = false;
	} finally {
	    loop.quit();
	}
    }, null);
    loop.run();
    if (!testSuccess) {
        GSystem.log_structured("Test " + child.get_path() + " failed: " + errmsg,
                               ["MESSAGE_ID=" + TESTS_FAILED_MSGID]);
        break;
    }
}

let rval = 1;
if (testSuccess) {
  GSystem.log_structured("Ran " + ntests + " tests successfully",
                         ["MESSAGE_ID=" + TESTS_SUCCESS_MSGID]);
  rval = 0;
}
rval;

