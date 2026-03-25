"""Export handlers — STL, STEP, F3D export.

BUG FIX: export_step — the original passed a body to createSTEPExportOptions,
but STEP export requires a component (or no second arg to export the whole
design). Fixed to export the full design.
"""

import os

import adsk.fusion

from ._helpers import body_by_name, get_design


def export_stl(body_name: str, file_path: str = None):
    body = body_by_name(body_name)

    if not file_path:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        file_path = os.path.join(desktop, f"{body_name}.stl")

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    export_mgr = get_design().exportManager
    stl_opts = export_mgr.createSTLExportOptions(body, file_path)
    stl_opts.meshRefinement = (
        adsk.fusion.MeshRefinementSettings.MeshRefinementMedium
    )
    export_mgr.execute(stl_opts)

    return {"exported": True, "body": body_name, "file_path": file_path}


def export_step(file_path: str = None):
    """Export the entire design as STEP.

    FIX: Original code passed body as second arg to createSTEPExportOptions,
    which is wrong — the API expects a component or nothing. We export the
    full design by passing only the file path.
    """
    design = get_design()

    if not file_path:
        doc_name = design.parentDocument.name
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        file_path = os.path.join(desktop, f"{doc_name}.step")

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    export_mgr = design.exportManager
    step_opts = export_mgr.createSTEPExportOptions(file_path)
    export_mgr.execute(step_opts)

    return {"exported": True, "file_path": file_path}


def export_f3d(file_path: str = None):
    design = get_design()

    if not file_path:
        doc_name = design.parentDocument.name
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        file_path = os.path.join(desktop, f"{doc_name}.f3d")

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    export_mgr = design.exportManager
    f3d_opts = export_mgr.createFusionArchiveExportOptions(file_path)
    export_mgr.execute(f3d_opts)

    return {"exported": True, "file_path": file_path}


COMMANDS = {
    "export_stl": lambda body_name, file_path=None, **_kw: export_stl(
        body_name, file_path
    ),
    "export_step": lambda file_path=None, **_kw: export_step(file_path),
    "export_f3d": lambda file_path=None, **_kw: export_f3d(file_path),
}
