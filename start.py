import io
import sys
import threading
import tkinter
import traceback
from typing import Literal

import psd_tools
import tifffile
from PIL import Image, ImageCms, ImageOps, ImageTk, UnidentifiedImageError
from tkinterdnd2 import DND_FILES, TkinterDnD

from fit_img import FitImg


class App(FitImg):
    def __init__(self):
        self.root: tkinter.Tk = TkinterDnD.Tk()
        self.root.configure(bg="black")
        self.root.title("MiuzPreview")
        self.root.attributes('-topmost', True)
        self.root.geometry("300x301")
        self.root.eval('tk::PlaceWindow . center')

        t = ("Перетяните изображение сюда.\n"
             "Поддерживаемые форматы:\n"
             "tiff, psd, psb, png, jpg")
        self.img_lbl = tkinter.Label(master=self.root, bg="black",text=t)
        self.img_lbl.pack(fill="both", expand=1)
        self.img_lbl.drop_target_register(DND_FILES)
        self.img_lbl.dnd_bind('<<Drop>>', lambda e: self.change_img(e=e))

        self.root.bind(sequence="<Command-Key>", func=self.minimize)
        self.root.protocol(name="WM_DELETE_WINDOW", func=self.root.withdraw)
        self.root.createcommand("tk::mac::ReopenApplication", self.root.deiconify)

    def minimize(self, e: tkinter.Event):
        if e.char == "w":
            self.root.wm_withdraw()

    def open_img(self, src: Literal["img path"]):
        if src.endswith((".tif", ".tiff", ".TIF", ".TIFF")):
            try:
                img = tifffile.imread(files=src)[:,:,:3]
                if str(object=img.dtype) != "uint8":
                    img = (img/256).astype(dtype="uint8")
                self.img = Image.fromarray(obj=img.astype("uint8"), mode="RGB")
                return True
            except Exception:
                # print(traceback.format_exc())
                print("tifffle error")

        else:
            try:
                img = Image.open(fp=src)
                self.img = ImageOps.exif_transpose(image=img)

                try:
                    iccProfile = img.info.get('icc_profile')
                    iccBytes = io.BytesIO(iccProfile)
                    icc = ImageCms.ImageCmsProfile(iccBytes)
                    srgb = ImageCms.createProfile('sRGB')

                    self.img = ImageCms.profileToProfile(img, icc, srgb)
                except Exception:
                    # print(traceback.format_exc())
                    print("icc profile err")

                return True
            except Exception:
            # except (UnidentifiedImageError, IsADirectoryError, OverflowError,
                    # OSError):
                print(traceback.format_exc())
                print("pillow error")

            try:
                self.img = psd_tools.PSDImage.open(fp=src).composite()
                return True
            except Exception:
            # except (ValueError, IsADirectoryError):
                # print(traceback.format_exc())
                print("psd tools error")

        self.img = None
        return False

    def create_tk_img(self, e: tkinter.Event = None):
        img_small = self.img.copy()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        img_small = self.fit(img=self.img.copy(), w=w, h=h)

        img_tk = ImageTk.PhotoImage(image=img_small)
        self.img_lbl.configure(image=img_tk, width=0, height=0)
        self.img_lbl.image_names = img_tk

    def change_img(self, e: tkinter.Event):
        self.img_lbl.configure(image="", text="Пожалуйста, подождите")
        self.img_lbl.unbind("<Configure>")

        task = threading.Thread(target=self.open_img,
                                kwargs={"src": e.data.strip("{}")})
        task.start()

        while task.is_alive():
            self.root.update()

        if not self.img:
            self.root.title(string="MiuzPreview")
            self.img_lbl.configure(image="", text="Не могу открыть изображение")
            self.root.update_idletasks()
            return
        
        self.create_tk_img()
        self.root.title(string=e.data.strip("{}").split("/")[-1])
        self.img_lbl.bind("<Configure>", self.resize_win)

    def resize_win(self, e: tkinter.Event = None):
        if hasattr(self, "task"):
            self.root.after_cancel(self.task)
        self.task = self.root.after(500, self.create_tk_img)


class MacMenu(tkinter.Menu):
    def __init__(self, master: tkinter.Tk):
        menubar = tkinter.Menu(master=master)
        self.root = master
        tkinter.Menu.__init__(self, master=menubar)

        if sys.version_info.minor < 10:
            master.createcommand("tkAboutDialog", self.about_dialog)

        master.configure(menu=menubar)

    def about_dialog(self):
        try:
            self.root.tk.call("tk::mac::standardAboutPanel")
        except Exception:
            self.print_err()


if __name__ == "__main__":
    app = App()
    MacMenu(master=app.root)
    app.root.mainloop()