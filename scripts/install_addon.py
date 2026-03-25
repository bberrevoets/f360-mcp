"""Install the F360MCP add-in to Fusion 360's AddIns directory."""

import os
import shutil
import sys

ADDON_NAME = "F360MCP"


def get_addins_dir() -> str:
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        return os.path.join(
            appdata,
            "Autodesk",
            "Autodesk Fusion 360",
            "API",
            "AddIns",
        )
    elif sys.platform == "darwin":
        home = os.path.expanduser("~")
        return os.path.join(
            home,
            "Library",
            "Application Support",
            "Autodesk",
            "Autodesk Fusion 360",
            "API",
            "AddIns",
        )
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    addon_src = os.path.join(project_root, "addon")
    addins_dir = get_addins_dir()
    addon_dst = os.path.join(addins_dir, ADDON_NAME)

    if not os.path.isdir(addon_src):
        print(f"ERROR: Source addon directory not found: {addon_src}")
        sys.exit(1)

    if not os.path.isdir(addins_dir):
        print(f"ERROR: Fusion 360 AddIns directory not found: {addins_dir}")
        print("Make sure Fusion 360 is installed.")
        sys.exit(1)

    if os.path.exists(addon_dst):
        print(f"Removing existing installation: {addon_dst}")
        shutil.rmtree(addon_dst)

    print(f"Installing {ADDON_NAME} to: {addon_dst}")
    shutil.copytree(addon_src, addon_dst)
    print("Done! Enable the add-in in Fusion 360: Utilities > Add-Ins")


if __name__ == "__main__":
    main()
