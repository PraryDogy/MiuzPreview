import shutil
import os
import subprocess

class AdvSetup:
    def __init__(self, py_ver: str, appname: str):
        lib_src = f"/Library/Frameworks/Python.framework/Versions/{py_ver}/lib"
        folders = "tcl8", "tcl8.6", "tk8.6"

        for i in folders:
            shutil.copytree(
                os.path.join(lib_src, i),
                os.path.join(f"dist/{appname}.app/Contents/lib", i)
                )

        folder = os.path.join(os.path.expanduser("~/Desktop"), appname)

        if not os.path.exists(folder):
            os.mkdir(folder)
        else:
            shutil.rmtree(folder)
            os.mkdir(folder)

        subprocess.Popen(
            ["ln", "-s", "/Applications", os.path.join(folder, "Программы")]
                )
        shutil.move(f"dist/{appname}.app", f"{folder}/{appname}.app")

        shutil.rmtree("build")
        shutil.rmtree(".eggs")
        shutil.rmtree("dist")

        subprocess.Popen(["open", "-R", folder])