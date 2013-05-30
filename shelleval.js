#!/usr/bin/env gjs

const Gio = imports.gi.Gio;
const GLib = imports.gi.GLib;

const sessionBus = Gio.bus_get_sync(Gio.BusType.SESSION, null);

function shellEval(shell, code, cancellable) {
    let res = shell.call_sync("Eval", GLib.Variant.new("(s)", [code]), 0, -1,
			      cancellable).deep_unpack();
    let [success, result] = res;
    if (!success)
	throw new Error("Failed to eval " + code.substr(0, 10));
    return JSON.parse(result);
}

function main() {
    let cancellable = null;
    let shell = Gio.DBusProxy.new_sync(sessionBus, 0, null,
				       "org.gnome.Shell", "/org/gnome/Shell",
				       "org.gnome.Shell", cancellable);

    print(shellEval(shell, ARGV[0], cancellable));
}

main();
