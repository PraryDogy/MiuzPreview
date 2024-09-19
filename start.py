import io
import json
import os
import subprocess
import sys
import threading
import tkinter

import psd_tools
import tifffile
from PIL import Image, ImageCms, ImageOps
from tkinterdnd2 import DND_FILES, TkinterDnD

from fit_img import FitImg

APP_NAME = 'ToJpeger'
CFG_DIR = os.path.join(
    os.path.expanduser('~'), f'Library/Application Support/{APP_NAME}')
JSON_FILE = os.path.join(CFG_DIR, "cfg.json")
DEFAULT_DATA = {
    "reveal": True,
    "resize": True,
    "size": 3000,
    }


def write_json(data: dict):
    with open(JSON_FILE, "w") as file:
        json.dump(data, file, indent=4)


def read_json():
    try:
        with open(JSON_FILE, "r") as file:
            return json.load(file)
    except Exception:
            return None
    

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.configure(bg="black")
        self.title("ToJpeger")
        self.geometry("300x300")
        self.eval('tk::PlaceWindow . center')
        self.resizable(False, False)

        self.bind(sequence="<Command-Key>", func=self.minimize)
        self.protocol(name="WM_DELETE_WINDOW", func=self.withdraw)
        self.createcommand("tk::mac::ReopenApplication", self.deiconify)

        t = ("Перетяните изображения сюда.\n"
             "Поддерживаемые форматы:\n"
             "tiff, psd, psb")

        self.img_lbl = tkinter.Label(master=self, bg="black",text=t)
        self.img_lbl.pack(fill="both", expand=1)
        self.img_lbl.drop_target_register(DND_FILES)
        self.img_lbl.dnd_bind('<<Drop>>', lambda e: self.start_converting(e=e))

        self.stop_btn = tkinter.Label(master=self,  text="Стоп", width=10, height=2, borderwidth=0, bg="black", fg="black")
        self.stop_btn.bind("<ButtonRelease-1>", self.on_stop_click)
        self.stop_btn.pack(pady=10)

        self.jpegs = []
        self.flag = True
        self.data = None
        self.read_data()

    def read_data(self):

        if not os.path.exists(CFG_DIR):
            os.mkdir(CFG_DIR)

        if not os.path.exists(JSON_FILE):
            write_json(DEFAULT_DATA)
            self.data = DEFAULT_DATA
            return

        read_data = read_json()

        if type(read_data) != dict or not read_data or DEFAULT_DATA.keys() != read_json().keys():
            write_json(DEFAULT_DATA)
            self.data = DEFAULT_DATA
            return

        self.data = read_data

    def on_stop_click(self, e):
        self.flag = False

    def minimize(self, e: tkinter.Event):
        if e.char == "w":
            self.wm_withdraw()

    def convert_tiff(self, src: str):
        try:
            img = tifffile.imread(files=src)[:,:,:3]
            if str(object=img.dtype) != "uint8":
                img = (img/256).astype(dtype="uint8")
            img = Image.fromarray(obj=img.astype("uint8"), mode="RGB")

            if img.mode == 'RGBA':
                img = img.convert('RGB')

            if self.data["resize"]:
                img: Image.Image = FitImg.fit(img, self.data["size"], self.data["size"])
            # сохраняем джепег
            save_path = self.new_filename(src)
            img.save(save_path, "JPEG")
            self.jpegs.append(save_path)

        except Exception as e:
            print("tifffle error:", e, src)

    def convert_psd(self, src: str):
        try:
            img = Image.open(fp=src)
            img = ImageOps.exif_transpose(image=img)

            # читаем профиль 
            try:
                iccProfile = img.info.get('icc_profile')
                iccBytes = io.BytesIO(iccProfile)
                icc = ImageCms.ImageCmsProfile(iccBytes)
                srgb = ImageCms.createProfile('sRGB')
                img = ImageCms.profileToProfile(img, icc, srgb)
            except Exception as e:
                print("icc profile err:", e)

            if img.mode == 'RGBA':
                img = img.convert('RGB')

            if self.data["resize"]:
                img: Image.Image = FitImg.fit(img, self.data["size"], self.data["size"])
            save_path = self.new_filename(src)
            img.save(save_path, "JPEG")
            self.jpegs.append(save_path)

        except Exception as e:
            print("pillow error:", e, src)
            # открываем через PSD tools
            try:
                img = psd_tools.PSDImage.open(fp=src).composite()
                save_path = self.new_filename(src)

                if img.mode == 'RGBA':
                    img = img.convert('RGB')

                if self.data["resize"]:
                    img: Image.Image = FitImg.fit(img, self.data["size"], self.data["size"])
                img.save(save_path, "JPEG")
                self.jpegs.append(save_path)
            except Exception as e:
                print("psd tools error:", e, src)
    
    def check_ext(self, img: str):
        img = img.lower()
        if img.endswith((".tif", ".tiff")):
            return "tiff"
        elif img.endswith((".psd", ".psb", ".png")):
            return "psd"
        return "other"
    
    def new_filename(self, src: str, advanced_name: str="_preview"):
        return f"{src.rsplit('.', 1)[0]}{advanced_name}.jpg"

    def convert_images_list(self, img_list: list):
        self.read_data()
        self.img_lbl.unbind('<<Drop>>')
        self.img_lbl.configure(text="Подготовка")
        self.stop_btn.configure(fg="white")
        self.flag = True
        self.jpegs.clear()

        files_to_convert = {
            "tiff": [],
            "psd": [],
            "other": []
            }

        for img in img_list:
            img: str

            if img.endswith(".app"):
                continue

            if os.path.isfile(img):
                files_to_convert[self.check_ext(img)].append(img)

            else:
                for root, dirs, files in os.walk(img):

                    if not self.flag:
                        break

                    for file in files:
                        img_file = os.path.join(root, file)
                        files_to_convert[self.check_ext(img_file)].append(img_file)

        ln = len(files_to_convert["tiff"]) + len(files_to_convert["psd"])
        count = 0

        for tiff_img in files_to_convert["tiff"]:

            if not self.flag:
                break

            count += 1
            self.img_lbl.configure(text=f"Конвертирую {count} из {ln}")
            self.convert_tiff(tiff_img)

        for psd_img in files_to_convert["psd"]:

            if not self.flag:
                break

            count += 1
            self.img_lbl.configure(text=f"Конвертирую {count} из {ln}")
            self.convert_psd(psd_img)

        t = ("Перетяните изображения сюда.\n"
             "Поддерживаемые форматы:\n"
             "tiff, psd, psb, png, jpg")

        self.img_lbl.configure(text=t)
        reveal_script = "reveal_files.scpt"
        
        if self.data["reveal"]:
            command = ["osascript", reveal_script] + self.jpegs
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        self.img_lbl.drop_target_register(DND_FILES)
        self.img_lbl.dnd_bind('<<Drop>>', lambda e: self.start_converting(e=e))
        self.stop_btn.configure(fg="black")

    def start_converting(self, e: tkinter.Event):
        images = self.splitlist(e.data)
        task = threading.Thread(target=self.convert_images_list, args=(images, ))
        task.start()


class MacMenu(tkinter.Menu):
    def __init__(self, master: tkinter.Tk):
        menubar = tkinter.Menu(master=master)
        self.root = master
        tkinter.Menu.__init__(self, master=menubar)

        # Добавляем пункт меню "Настройки"
        self.settings_menu = tkinter.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Настройки", menu=self.settings_menu)
        self.settings_menu.add_command(label="Открыть настройки", command=self.open_settings)

        if sys.version_info.minor < 10:
            master.createcommand("tkAboutDialog", self.about_dialog)

        master.configure(menu=menubar)

    def about_dialog(self):
        try:
            self.root.tk.call("tk::mac::standardAboutPanel")
        except Exception:
            self.print_err()

    def open_settings(self):
        try:
            subprocess.Popen(['open', JSON_FILE])
        except Exception as e:
            print(f"Ошибка при открытии файла настроек: {e}")

    def print_err(self):
        print("Ошибка: не удалось открыть панель О программе")

if __name__ == "__main__":
    app = App()
    MacMenu(master=app)
    app.mainloop()