import gi                                                                                                                                                                                             
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class MyWindow():
    def __init__(self):
        self.win = Gtk.Window()
        self.win.connect("delete-event", Gtk.main_quit)

    def confirmation(self, message):
        self.button = Gtk.Button(label=message)
        self.button.connect("clicked", self.on_button_clicked)
        self.win.add(self.button)

    def on_button_clicked(self, widget):
        print("Hello World") 

    def show(self):
        self.win.show_all()
        Gtk.main()
