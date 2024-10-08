# -*- coding: utf-8 -*-

"""
    python setup.py py2app
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime

from setuptools import setup

from tkinter_macos import tkinter_macos_copy

# ****************** DON'T CHANGE IT ******************

def remove_trash():

    trash = ("build", ".eggs", "dist")

    for i in trash:
        try:
            shutil.rmtree(i)
        except Exception as e:
            continue


def move_app_to_desktop(appname: str):

    desktop = os.path.expanduser("~/Desktop")

    dest = os.path.join(desktop, f"{appname}.app")
    src = os.path.join("dist", f"{appname}.app")

    try:
        if os.path.exists(dest):
            shutil.rmtree(dest)
    except Exception as e:
        print(e)

    try:
        shutil.move(src, dest)
    except Exception as e:
        print(e)

    try:
        subprocess.Popen(["open", "-R", dest])
    except Exception as e:
        print(e)

    return dest


def include_files(folder_name: str) -> list[str, list]:
    return (
        folder_name,
        [os.path.join(folder_name, i) for i in os.listdir(folder_name)]
        )





# ****************** YOUR DATA ******************

AUTHOR = "Evgeny Loshkarev"  # "Evgeny Loshkarev"
SHORT_AUTHOR_NAME = "Evlosh" # "Evlosh"
COMPANY = "" # "MIUZ Diamonds" or ""
APP_NAME = "ToJpeger"
APP_VER = "1.1.0" # "1.0.0"
ICON_PATH = "icon.icns" # "icon/icon.icns" or "icon.icns"
MAIN_FILES = ["start.py"] # SINGLE OR MULTIPLE PYTHON FILES


DATA_FILES = [
    "reveal_files.scpt", # SINGLE FILE
    ]





# ****************** DON'T CHANGE IT ******************

YEAR = datetime.now().year # CURRENT YEAR
BUNDLE_ID = f"com.{SHORT_AUTHOR_NAME}.{APP_NAME}" # DON'T CHANGE IT
PY2APP = "py2app" # DON'T CHANGE IT

OPTIONS = {"iconfile": ICON_PATH,
           "plist": {"CFBundleName": APP_NAME,
                     "CFBundleShortVersionString": APP_VER,
                     "CFBundleVersion": APP_VER,
                     "CFBundleIdentifier": BUNDLE_ID,
                     "NSHumanReadableCopyright": (
                         f"Created by {AUTHOR}"
                         f"\nCopyright © {YEAR} {COMPANY}."
                         f"\nAll rights reserved.")}}

sys.argv.append(PY2APP)

try:
    remove_trash()

    setup(
        app=MAIN_FILES,
        name=APP_NAME,
        data_files=DATA_FILES,
        options={PY2APP: OPTIONS},
        setup_requires=[PY2APP],
        )

    dest = move_app_to_desktop(APP_NAME)
    tkinter_macos_copy(app_dest=dest)
    remove_trash()

except Exception as e:
    print(e)
    remove_trash()
