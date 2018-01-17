import sys
import gi                                                                                                                                                                                             
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class MyWindow():
    def __init__(self):
        self.win = Gtk.Window()
        self.win.connect("delete-event", Gtk.main_quit)
        self.result = ""

    def confirmation(self, message):
        self.button = Gtk.Button(label=message)
        self.button.connect("clicked", self.on_button_clicked)
        self.win.add(self.button)

    def on_button_clicked(self, widget, message):
        self.win.destroy()
        Gtk.main_quit()
        self.result = message

    def true_false(self, message):
        width = len(message)*14
        self.win.set_title(message)
        self.win.set_default_size(width, 0)
        self.grid_yes_no = Gtk.Grid()
        self.button_yes = Gtk.Button(label="Yes")
        self.button_yes.set_size_request(width/2, 0)
        self.button_no = Gtk.Button(label="No")
        self.button_no.set_size_request(width/2, 0)
        self.button_yes.connect("clicked", self.on_button_clicked, "yes")
        self.button_no.connect("clicked", self.on_button_clicked, "no")
        self.grid_yes_no.attach(self.button_yes, 0, 0, 1, 1)
        self.grid_yes_no.attach(self.button_no, 1, 0, 1, 1)
        self.win.add(self.grid_yes_no)

    def show(self, mode, title):
        self.result = ""
        if mode == "true_false":
            result = self.true_false(title)
        self.win.show_all()
        Gtk.main()
        return self.result
