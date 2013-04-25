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

const TEST_SKIP_ECODE = 77;
const TESTS_FAILED_MSGID = '0eee66bf98514369bef9868327a43cf1';
const TESTS_SUCCESS_MSGID = '4d013788dd704743b826436c951e551d';

let cancellable = null;
let dirEnum;
try {
    let path = Gio.File.new_for_path('/usr/share/installed-tests');
    dirEnum = path.enumerate_children('standard::name,standard::type',
				      Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS,
				      cancellable);
} catch (e) {
    if (e.matches(Gio.IOErrorEnum, Gio.IOErrorEnum.NOT_FOUND))
	dirEnum = null;
    else
	throw e;
}
let info;
let loop = GLib.MainLoop.new(null, true);
let ntests = 0;
let nSkippedTests = 0;
let testSuccess = true;
while (dirEnum != null && (info = dirEnum.next_file(cancellable)) != null) {
    let name = info.get_name();
    if (name.indexOf('.testmeta') < 0)
	continue;
    let child = dirEnum.get_child(info);
    let childPath = child.get_path();

    let kdata = GLib.KeyFile.new();
    kdata.load_from_file(childPath, 0);
    let execKey = kdata.get_string('Test', 'Exec');
    if (!execKey)
	throw new Error("Missing Exec key in " + childPath);
    let [success, testArgv] = GLib.shell_parse_argv(execKey);
    print("Running test: " + childPath);

    let pid;
    [success,pid] = GLib.spawn_async(null, testArgv, null,
					 GLib.SpawnFlags.DO_NOT_REAP_CHILD | GLib.SpawnFlags.SEARCH_PATH, null);
    let errmsg = null;
    let skipped = false;
    GLib.child_watch_add(GLib.PRIORITY_DEFAULT, pid, function(pid, estatus) {
	try {
	    GLib.spawn_check_exit_status(estatus);
	} catch (e) {
	    if (e.domain == GLib.spawn_exit_error_quark() &&
		e.code == TEST_SKIP_ECODE) {
		print("Skipping test " + childPath);
		nSkippedTests++;
		skipped = true;
	    } else {
		errmsg = e.message;
		testSuccess = false;
	    }
	} finally {
	    loop.quit();
	}
    }, null);
    loop.run();
    if (!testSuccess) {
	GSystem.log_structured("Test " + childPath + " failed: " + errmsg,
                               ["MESSAGE_ID=" + TESTS_FAILED_MSGID]);
        break;
    }
    if (!skipped)
	ntests += 1;
}

let rval;
if (testSuccess) {
    GSystem.log_structured("Ran " + ntests + " tests successfully, " + nSkippedTests + " skipped",
                           ["MESSAGE_ID=" + TESTS_SUCCESS_MSGID]);
    rval = 0;
} else {
    rval = 1;
}
rval;
