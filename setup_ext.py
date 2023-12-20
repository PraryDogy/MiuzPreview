import shutil
import os
import subprocess

class SetupExt:
    def __init__(self, py_ver: str, appname: str):
        lib_src = f"/Library/Frameworks/Python.framework/Versions/{py_ver}/lib"
        folders = "tcl8", "tcl8.6", "tk8.6"

        for i in folders:
            shutil.copytree(
                os.path.join(lib_src, i),
                os.path.join(f"dist/{appname}.app/Contents/lib", i)
                )

        desktop = os.path.expanduser("~/Desktop")

        shutil.move(f"dist/{appname}.app", f"{desktop}/{appname}.app")

        shutil.rmtree("build")
        shutil.rmtree(".eggs")
        shutil.rmtree("dist")

        subprocess.Popen(["open", "-R", f"{desktop}/{appname}.app"])


if __name__ == "__main__":
    shutil.rmtree("build")
    shutil.rmtree(".eggs")
    shutil.rmtree("dist")