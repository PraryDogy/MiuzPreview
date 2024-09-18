import io
import sys
import threading
import tkinter

import psd_tools
import tifffile
from PIL import Image, ImageCms, ImageOps
from tkinterdnd2 import DND_FILES, TkinterDnD

from fit_img import FitImg


class App(FitImg):
    def __init__(self):
        self.root: tkinter.Tk = TkinterDnD.Tk()
        self.root.configure(bg="black")
        self.root.title("ToJpeger")
        # self.root.attributes('-topmost', True)
        self.root.geometry("300x300")
        self.root.eval('tk::PlaceWindow . center')

        t = ("Перетяните изображения сюда.\n"
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

    def convert_img(self, src: str):
        if src.endswith((".tif", ".tiff", ".TIF", ".TIFF")):

            try:
                img = tifffile.imread(files=src)[:,:,:3]
                if str(object=img.dtype) != "uint8":
                    img = (img/256).astype(dtype="uint8")
                self.img = Image.fromarray(obj=img.astype("uint8"), mode="RGB")

                # сохраняем джепег
                save_path = f"{src.rsplit('.', 1)[0]}.jpg"
                self.img.save(save_path, "JPEG")

            except Exception as e:
                print("tifffle error", e)

        elif src.endswith((".psd", ".PSD", ".psb", ".PSB", ".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")):

            # открываем через PIL
            try:
                img = Image.open(fp=src)
                self.img = ImageOps.exif_transpose(image=img)
                # читаем профиль 
                try:
                    iccProfile = img.info.get('icc_profile')
                    iccBytes = io.BytesIO(iccProfile)
                    icc = ImageCms.ImageCmsProfile(iccBytes)
                    srgb = ImageCms.createProfile('sRGB')
                    self.img = ImageCms.profileToProfile(img, icc, srgb)
                    save_path = f"{src.rsplit('.', 1)[0]}.jpg"
                    self.img.save(save_path, "JPEG")
                except Exception as e:
                    print("icc profile err", e)
            except Exception as e:
                print("pillow error", e)
                # открываем через PSD tools
                try:
                    self.img = psd_tools.PSDImage.open(fp=src).composite()
                    save_path = f"{src.rsplit('.', 1)[0]}.jpg"
                    self.img.save(save_path, "JPEG")
                except Exception as e:
                    print("psd tools error", e)

    def convert_images_list(self, img_list: list):
        ln = len(img_list)
        for x, img in enumerate(img_list, start=1):
            self.convert_img(src=img)
            self.img_lbl.configure(text=f"Конвертирую {x} из {ln}")

        t = ("Перетяните изображения сюда.\n"
             "Поддерживаемые форматы:\n"
             "tiff, psd, psb, png, jpg")
        self.img_lbl.configure(text=t)

    def change_img(self, e: tkinter.Event):
        images = self.root.splitlist(e.data)
        task = threading.Thread(target=self.convert_images_list, args=(images, ))
        task.start()


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