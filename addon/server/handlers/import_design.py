"""Import handlers — STEP and F3D import into the active design."""

import os

import adsk.core

from ._helpers import get_app, get_design, get_root


def import_step(file_path: str):
    if not os.path.isfile(file_path):
        raise RuntimeError(f"File not found: {file_path}")

    app = get_app()
    design = get_design()
    root = get_root()

    import_mgr = app.importManager
    step_opts = import_mgr.createSTEPImportOptions(file_path)
    import_mgr.importToTarget(step_opts, root)

    # Find the newly added component
    component_name = None
    if root.occurrences.count > 0:
        last_occ = root.occurrences.item(root.occurrences.count - 1)
        component_name = last_occ.component.name

    return {
        "imported": True,
        "file_path": file_path,
        "component_name": component_name,
    }


def import_f3d(file_path: str):
    if not os.path.isfile(file_path):
        raise RuntimeError(f"File not found: {file_path}")

    app = get_app()
    root = get_root()

    import_mgr = app.importManager
    f3d_opts = import_mgr.createFusionArchiveImportOptions(file_path)
    import_mgr.importToTarget(f3d_opts, root)

    component_name = None
    if root.occurrences.count > 0:
        last_occ = root.occurrences.item(root.occurrences.count - 1)
        component_name = last_occ.component.name

    return {
        "imported": True,
        "file_path": file_path,
        "component_name": component_name,
    }


COMMANDS = {
    "import_step": lambda file_path, **_kw: import_step(file_path),
    "import_f3d": lambda file_path, **_kw: import_f3d(file_path),
}
