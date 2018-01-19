from time import sleep
import tkinter as tk

class MyWindow():
    def __init__(self):
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.result = ""

    def notification(self, message):
        timeout = 5000
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
        self.root.after(timeout, lambda: self.root.destroy()) 

    def on_button_clicked(self, message):
        self.result = message
        self.root.destroy()

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

    def show_win(self, mode, title):
        if mode == "true_false":
            result = self.true_false(title)
        elif mode == "notification":
            result = self.notification(title)
        self.prepare_widget()
        self.root.mainloop()
        return self.result

if __name__ == '__main__':
    Win = MyWindow()                                                                                                                                                                            
    print(Win.show_win("true_false", "Hello world"))
