#!/usr/bin/env gjs

const GLib = imports.gi.GLib;
const GObject = imports.gi.GObject;
const Gio = imports.gi.Gio;

const sessionBus = Gio.bus_get_sync(Gio.BusType.SESSION, null);

const CLOSE_APPS = '%{apps}.forEach(function (id) { Shell.AppSystem.get_default().lookup_app(id).request_quit(); });';
const GET_APP_IDS = 'Shell.AppSystem.get_default().get_running().map(function (a) { return a.get_id(); });';

const StartStopApps = new GObject.Class({
    Name: 'StartStopApps',
    
    _init: function(props) {
	this._shell = Gio.DBusProxy.new_sync(sessionBus, 0, null,
					     "org.gnome.Shell", "/org/gnome/Shell",
					     "org.gnome.Shell", null);
    },

    _shellEval: function(code, cancellable) {
	let res = this._shell.call_sync("Eval", GLib.Variant.new("(s)", [code]), 0, -1,
					cancellable).deep_unpack();
	let [success, result] = res;
	if (!success)
	    throw new Error("Failed to eval " + code.substr(0, 20));
	return result ? JSON.parse(result) : null;
    },

    _awaitRunningApp: function(appId, cancellable) {
	let timeoutSecs = 10;
	let i = 0;
	for (let i = 0; i < timeoutSecs; i++) {
	    let runningApps = this._shellEval(GET_APP_IDS, cancellable);
	    for (let i = 0; i < runningApps.length; i++) {
		if (runningApps[i] == appId)
		    return;
	    }
	    GLib.usleep(GLib.USEC_PER_SEC);
	}
	throw new Error("Failed to find running app " + appId + " after " + timeoutSecs + "s");
    },

    _testOneApp: function(app, cancellable) {
	let appId = app.get_id();
	print("testing appid=" + appId);
    	app.launch([], cancellable);
	this._awaitRunningApp(appId, cancellable);
	this._shellEval(CLOSE_APPS.replace('%{apps}', JSON.stringify([appId])), cancellable);
    },
    
    run: function(cancellable) {
	let allApps = Gio.AppInfo.get_all();
	
	let runningApps = this._shellEval(GET_APP_IDS, cancellable);
	print("Closing running apps: " + runningApps);
	this._shellEval(CLOSE_APPS.replace('%{apps}', JSON.stringify(runningApps)), cancellable);
	
	for (let i = 0; i < allApps.length; i++) {
    	    let app = allApps[i];
	    if (app.get_nodisplay())
		continue;
	    // Ok, a gross hack; we should really be using gnome-menus
	    // to look up all apps.  Or maybe fix Gio?
	    if (app.has_key('Categories') &&
		app.get_string('Categories').indexOf('X-GNOME-Settings-Panel') >= 0)
		continue;
	    this._testOneApp(app, cancellable);
	}
    }
});

function main() {
    let cancellable = null;

    let startstopapps = new StartStopApps();
    startstopapps.run(cancellable);
}

main();
