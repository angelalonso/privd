#!/usr/bin/python3                                                                                                                                                                              
# -*- coding: utf-8 -*-
                              
from time import sleep
import tkinter as tk


class MyWindow():
    """ Class to manage tkinter Window
    """
    def __init__(self):
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.result = ""

    def on_button_clicked(self, message):
        """ Catching a mouse click 
        """
        self.result = message
        self.root.destroy()

    def on_enter_pressed(self, event):
        """ Catching keyboard Enter
            Not yet implemented
        """
        pass


    def notification(self, message):
        """ Widget to show a notification that disappears after timeout (ms)
        """
        timeout = 4000
        msg_width = len(message) * 14
        btn_width = 4
        title = tk.Message(self.frame, 
                text = message, 
                pady = 15, 
                padx = 15, 
                width = msg_width)
        title.pack(side = tk.TOP)
        btn_ok = tk.Button(self.frame, 
                 width = btn_width,
                 text = "Close", 
                 command = lambda: self.on_button_clicked(""))
        btn_ok.pack(side = tk.RIGHT)
        btn_ok.focus_set()
        self.root.after(timeout, lambda: self.root.destroy()) 

    def true_false(self, message):
        """ Widget to choose between true or false
        """
        msg_width = len(message) * 14
        btn_width = 4
        title = tk.Message(self.frame, 
                text = message, 
                pady = 15, 
                padx = 15, 
                width = msg_width)
        title.pack(side = tk.TOP)
        btn_yes = tk.Button(self.frame, 
                 width = btn_width,
                 text = "Yes", 
                 command = lambda: self.on_button_clicked("yes"))
        btn_yes.pack(side = tk.LEFT)
        btn_no = tk.Button(self.frame,
                 width = btn_width,
                 text = "No",
                 fg = "red",
                 command = lambda: self.on_button_clicked("no"))
        btn_no.pack(side = tk.RIGHT)

    def choices_files(self, file1, file2):
        """ Widget to choose which file to keep
        """
        message = "ATTENTION, CONFLICT!"
        message2_part = "The following file's local copy differs from the remote version!"
        message2 = message2_part + "\n\n" + file1['name']
        msg_width = (max(len(file1['name']), len(message2_part)) * 7)
        print(msg_width)
        pad = 4
        title = tk.Message(self.frame, 
                text = message, 
                font = ("",12,"bold"),
                pady = pad, 
                padx = pad, 
                width = msg_width)
        subtitle = tk.Message(self.frame, 
                text = message2, 
                font = ("",11,""),
                pady = pad, 
                padx = pad, 
                width = msg_width)
        desc_timestamp = tk.Message(self.frame, 
                text = "Last changed", 
                font = ("",10,"bold"),
                pady = pad, 
                padx = pad, 
                width = msg_width)
        desc_size = tk.Message(self.frame, 
                text = "Size", 
                font = ("",10,"bold"),
                pady = pad, 
                padx = pad, 
                width = msg_width)
        file1_desc1 = tk.Message(self.frame,
                text = "LOCAL",
                font = ("",12,""),
                pady = pad, 
                padx = pad, 
                width = msg_width)
        file1_desc2 = tk.Message(self.frame,
                text = file1['timestamp'],
                pady = pad, 
                padx = pad, 
                width = msg_width)
        file1_desc3 = tk.Message(self.frame,
                text = file1['size'],
                pady = pad, 
                padx = pad, 
                width = msg_width)
        file2_desc1 = tk.Message(self.frame,
                text = "REMOTE",
                font = ("",12,""),
                pady = pad, 
                padx = pad, 
                width = msg_width)
        file2_desc2 = tk.Message(self.frame,
                text = file2['timestamp'],
                pady = pad, 
                padx = pad, 
                width = msg_width)
        file2_desc3 = tk.Message(self.frame,
                text = file2['size'],
                pady = pad, 
                padx = pad, 
                width = msg_width)

        btn_useremote = tk.Button(self.frame, 
                text = 'Use REMOTE', 
                pady = pad, 
                padx = pad, 
                command = lambda: self.on_button_clicked('use remote'))
        btn_uselocal = tk.Button(self.frame,
                text = 'Use LOCAL',
                pady = pad, 
                padx = pad, 
                command = lambda: self.on_button_clicked('use local'))
        btn_exit = tk.Button(self.frame,
                text = 'EXIT',
                pady = pad, 
                padx = pad, 
                command = lambda: self.on_button_clicked('exit'))

        title.grid(row=0, column=0, columnspan=3)
        subtitle.grid(row=1, column=0, columnspan=3)
        desc_timestamp.grid(row=3, column=0, sticky=tk.E)
        desc_size.grid(row=4, column=0, sticky=tk.E)
        file1_desc1.grid(row=2, column=1)
        file1_desc2.grid(row=3, column=1, sticky=tk.E)
        file1_desc3.grid(row=4, column=1, sticky=tk.E)
        file2_desc1.grid(row=2, column=2)
        file2_desc2.grid(row=3, column=2, sticky=tk.E)
        file2_desc3.grid(row=4, column=2, sticky=tk.E)
        btn_useremote.grid(row=5, column=0, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
        btn_uselocal.grid(row=6, column=0, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
        btn_exit.grid(row=7, column=0, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)


    def choices_2(self, message, choice1, choice2):
        """ Widget to choose from two alternatives
        """
        msg_width = len(message) * 14
        title = tk.Message(self.frame, 
                text = message, 
                pady = 15, 
                padx = 15, 
                width = msg_width)
        title.pack(side = tk.TOP)
        btn_choice1 = tk.Button(self.frame, 
                 text = choice1, 
                 command = lambda: self.on_button_clicked(choice1))
        btn_choice1.pack(side = tk.LEFT)
        btn_choice2 = tk.Button(self.frame,
                 text = choice2,
                 command = lambda: self.on_button_clicked(choice2))
        btn_choice2.pack(side = tk.RIGHT)

    def prepare_win(self):
        """ Configures the window before we show it
        """
        self.root.overrideredirect(1)
        self.root.update_idletasks()
        w = self.root.winfo_width() 
        h = self.root.winfo_height()
        ws = self.root.winfo_screenwidth() # width of the screen
        hs = self.root.winfo_screenheight() # height of the screen
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.root.update()

    def show_win(self, mode, title, **kwargs):
        """ Calls the different configurations and shows the window we have been getting ready
        """
        if mode == "true_false":
            result = self.true_false(title)
        elif mode == "notification":
            result = self.notification(title)
        elif mode == "choices_files":
            file1 = kwargs.pop('file1')
            file2 = kwargs.pop('file2')
            result = self.choices_files(file1, file2)
        elif mode == "choices_2":
            choice1 = kwargs.pop('choice1')
            choice2 = kwargs.pop('choice2')
            result = self.choices_2(title, choice1, choice2)
        self.prepare_win()
        self.root.mainloop()
        return self.result

if __name__ == '__main__':
    Win = MyWindow()                                                                                                                                                                            
    print(Win.show_win("true_false", "Hello world"))
