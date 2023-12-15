import tkinter
import sys
import traceback
from PIL import ImageTk, Image
from tkinterdnd2 import DND_FILES, TkinterDnD


class Main:
    def __init__(self):
        self.root: tkinter.Tk = TkinterDnD.Tk()
        self.root.configure(bg="black")
        self.root.title("Img Viewer")
        self.root.attributes('-topmost', True)

        self.img_lbl = tkinter.Label(master=self.root, bg="black",
                                     width=100, height=50,
                                     text="Перетяни сюда фото")
        self.img_lbl.pack()
        self.img_lbl.drop_target_register(DND_FILES)
        self.img_lbl.dnd_bind('<<Drop>>', lambda e: self.set_img(e=e))

    def set_img(self, e: tkinter.Event):
        try:
            self.img = Image.open(e.data)
        except FileNotFoundError:
            self.img = Image.open(e.data.replace("{", "").replace("}", ""))
        except AttributeError:
            print("no")
            return
        
        max_win = max(self.root.winfo_width(), self.root.winfo_height())
        img_small = self.img.copy()
        img_small.thumbnail((max_win, max_win))

        img_tk = ImageTk.PhotoImage(image=img_small)
        self.img_lbl.configure(image=img_tk, width=0, height=0)
        self.img_lbl.image_names = img_tk

        self.root.update_idletasks()

        self.img_lbl.unbind("<Configure>")
        self.root.after(1000, lambda:
                        self.img_lbl.bind("<Configure>", self.create_task)
                        )

    def create_task(self, e=None):
        try:
            self.root.after_cancel(self.task)
        except AttributeError:
            pass
        self.task = self.root.after(500, self.resize_img)

    def resize_img(self):
        try:
            max_win = max(self.root.winfo_width(), self.root.winfo_height())
            img_small = self.img.copy()
            img_small.thumbnail((max_win, max_win))

            img_tk = ImageTk.PhotoImage(image=img_small)
            self.img_lbl.configure(image=img_tk, width=0, height=0)
            self.img_lbl.image_names = img_tk
        except AttributeError:
            pass

Main().root.mainloop()