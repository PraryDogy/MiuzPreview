"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['start.py']
DATA_FILES = []
OPTIONS = {"iconfile": "icon.icns",
           "plist": {"CFBundleName": "MiuzPreview",
                     "CFBundleShortVersionString": "1.0.0",
                     "CFBundleVersion": "1.0.0",
                     "CFBundleIdentifier":f"com.evlosh.MiuzPreview",
                     "NSHumanReadableCopyright": (
                         "Created by Evgeny Loshkarev"
                         "\nCopyright © 2023 MIUZ Diamonds."
                         "\nAll rights reserved.")}}
# 'argv_emulation': True


setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)