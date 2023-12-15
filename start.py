import tkinter
from PIL import ImageTk, Image, UnidentifiedImageError
from tkinterdnd2 import DND_FILES, TkinterDnD
import psd_tools
import tifffile
import traceback
import threading


class Main:
    def __init__(self):
        self.root: tkinter.Tk = TkinterDnD.Tk()
        self.root.configure(bg="black")
        self.root.title("MiuzPreview")
        self.root.attributes('-topmost', True)
        self.root.geometry("300x300")
        self.root.eval('tk::PlaceWindow . center')

        self.img_lbl = tkinter.Label(master=self.root, bg="black",
                                     text="Перетяните изображение сюда.")
        self.img_lbl.pack(fill="both", expand=1)
        self.img_lbl.drop_target_register(DND_FILES)
        self.img_lbl.dnd_bind('<<Drop>>', lambda e: self.set_img(e=e))

    def open_img(self, e: tkinter.Event):
        p = e.data.strip("{}")

        try:
            self.img = psd_tools.PSDImage.open(fp=p).composite()
            return
        except ValueError:
            print(traceback.format_exc())
            pass

        try:
            self.img = Image.open(fp=p)
            return
        except UnidentifiedImageError:
            print(traceback.format_exc())
            pass

        try:
            img = tifffile.imread(files=p)[:,:,:3]
            if str(object=img.dtype) != "uint8":
                img = (img/256).astype(dtype="uint8")
            self.img = Image.fromarray(obj=img.astype("uint8"), mode="RGB")
            return
        except Exception:
            print(traceback.format_exc())
            self.img = None
            return False


    def set_img(self, e: tkinter.Event):
        self.img_lbl.configure(image="", text="Пожалуйста, подождите")

        task = threading.Thread(target=lambda: self.open_img(e=e))
        task.start()

        while task.is_alive():
            # print(task)
            self.root.update()

        if not self.img:
            self.img_lbl.configure(image="", text="Не могу открыть изображение")
            return
        
        max_win = max(self.root.winfo_width(), self.root.winfo_height())
        img_small = self.img.copy()
        img_small.thumbnail((max_win, max_win))

        img_tk = ImageTk.PhotoImage(image=img_small)
        self.img_lbl.configure(image=img_tk, width=0, height=0)
        self.img_lbl.image_names = img_tk

        self.root.update_idletasks()

        self.img_lbl.unbind("<Configure>")
        self.root.after(1, lambda:
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