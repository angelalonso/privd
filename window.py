import tkinter as tk

class MyWindow():
    def __init__(self):
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.result = ""

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
        button = tk.Button(self.frame, 
                 width = btn_width,
                 text = "Yes", 
                 command = lambda: self.on_button_clicked("yes"))
        button.pack(side = tk.LEFT)
        slogan = tk.Button(self.frame,
                 width = btn_width,
                 text = "No",
                 fg = "red",
                 command = lambda: self.on_button_clicked("no"))
        slogan.pack(side = tk.RIGHT)

    def show_win(self, mode, title):
        if mode == "true_false":
            result = self.true_false(title)
        self.root.mainloop()
        return self.result

if __name__ == '__main__':
    Win = MyWindow()                                                                                                                                                                            
    print(Win.show_win("true_false", "Hello world"))
