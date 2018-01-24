#!/usr/bin/python3                                                                                                                                                                              
# -*- coding: utf-8 -*-
                              
#  ====  Automated Import and pip-installation of requirements  ====  #
import subprocess             
                              
def pipinstall(package):      
    subprocess.call(['pip3', 'install', '--user', package])                                                                                                                                           
                              
try: from time import sleep
except ImportError:           
    pipinstall('time')    
    from time import sleep

try: import tkinter as tk
except ImportError:           
    pipinstall('tkinter')    
    import tkinter as tk

try: import threading
except ImportError:           
    pipinstall('threading')    
    import threading


class MyWindow():
    def __init__(self):
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.result = ""

    def on_button_clicked(self, message):
        self.result = message
        self.root.destroy()

    def on_enter_pressed(self, event):
        pass


    def notification(self, message):
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

    def choices_2(self, message, choice1, choice2):
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

    def prepare_widget(self):
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
        if mode == "true_false":
            result = self.true_false(title)
        elif mode == "notification":
            result = self.notification(title)
        elif mode == "choices_2":
            choice1 = kwargs.pop('choice1')
            choice2 = kwargs.pop('choice2')
            result = self.choices_2(title, choice1, choice2)
        self.prepare_widget()
        # didnt work
        #self.root.wm_attributes("-topmost", 1)
        #self.root.focus_force()
        # didnt work
        #self.root.overrideredirect(False)
        #self.root.iconify()
        #self.root.update()
        #self.root.deiconify()
        #self.root.overrideredirect(True)
        self.root.mainloop()
        return self.result

if __name__ == '__main__':
    Win = MyWindow()                                                                                                                                                                            
    print(Win.show_win("true_false", "Hello world"))
