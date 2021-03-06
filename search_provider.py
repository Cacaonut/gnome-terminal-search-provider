import os
import subprocess

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
import dbus.service

from gi.repository import GLib

# Shell
shell = "zsh"

sbn = dict(dbus_interface='org.gnome.Shell.SearchProvider2')

class SearchService(dbus.service.Object):
    bus_name = "org.gnome.Terminal.CommandSearchProvider"
    object_path = "/" + bus_name.replace(".", "/")

    def __init__(self):
        self.session_bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(self.bus_name, bus=self.session_bus)
        dbus.service.Object.__init__(self, bus_name, self.object_path)

        stdout = subprocess.check_output(['/bin/bash', '-c', 'compgen -c'])
        self.commands = [line.decode("utf-8") for line in stdout.splitlines()]

    @dbus.service.method(in_signature='sasu', **sbn)
    def ActivateResult(self, id, terms, timestamp):
        command = id
        print(f"Command: {command}")
        os.system(f"gnome-terminal -- {shell} -c 'cd ~; {command}; exec {shell}'")

    @dbus.service.method(in_signature='as', out_signature='as', **sbn)
    def GetInitialResultSet(self, terms):
        search = " ".join(terms)
        results = [command for command in self.commands if search in command]
        results.append(search)
        return results

    @dbus.service.method(in_signature='as', out_signature='aa{sv}', **sbn)
    def GetResultMetas(self, ids):
        return [dict(id=id, name=id, description=shell) for id in ids]

    @dbus.service.method(in_signature='asas', out_signature='as', **sbn)
    def GetSubsearchResultSet(self, previous_results, new_terms):
        search = " ".join(new_terms)
        print(search)
        results = [command for command in self.commands if search in command]
        results = [search] + results
        print(results)
        return results
                
    @dbus.service.method(in_signature='asu', terms='as', timestamp='u', **sbn)
    def LaunchSearch(self, terms, timestamp):
        pass

if __name__ == "__main__":
    SearchService()
    GLib.MainLoop().run()