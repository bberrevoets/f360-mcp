"""Uninstall the F360MCP add-in from Fusion 360's AddIns directory."""

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
    addins_dir = get_addins_dir()
    addon_dst = os.path.join(addins_dir, ADDON_NAME)

    if not os.path.exists(addon_dst):
        print(f"{ADDON_NAME} is not installed at: {addon_dst}")
        sys.exit(0)

    print(f"Removing {ADDON_NAME} from: {addon_dst}")
    shutil.rmtree(addon_dst)
    print("Done! The add-in has been removed.")


if __name__ == "__main__":
    main()
