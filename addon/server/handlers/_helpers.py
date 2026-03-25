"""Shared helper functions for all command handlers."""

import adsk.core
import adsk.fusion


def get_app():
    return adsk.core.Application.get()


def get_design():
    d = get_app().activeProduct
    if d is None:
        raise RuntimeError("No active design")
    return d


def get_root():
    return get_design().rootComponent


def body_by_name(name: str):
    root = get_root()
    for i in range(root.bRepBodies.count):
        b = root.bRepBodies.item(i)
        if b.name == name:
            return b
    raise RuntimeError(f"Body '{name}' not found")


def component_by_name(name: str):
    root = get_root()
    if root.name == name:
        return root
    for occ in root.allOccurrences:
        if occ.component.name == name:
            return occ.component
    raise RuntimeError(f"Component '{name}' not found")


def sketch_by_name(name: str):
    root = get_root()
    for i in range(root.sketches.count):
        s = root.sketches.item(i)
        if s.name == name:
            return s
    raise RuntimeError(f"Sketch '{name}' not found")


def construction_plane(plane: str):
    root = get_root()
    m = {
        "xy": root.xYConstructionPlane,
        "yz": root.yZConstructionPlane,
        "xz": root.xZConstructionPlane,
    }
    p = m.get(plane)
    if p is None:
        raise RuntimeError(f"Unknown plane '{plane}' — use xy, yz, or xz")
    return p


def construction_axis(axis: str):
    root = get_root()
    m = {
        "x": root.xConstructionAxis,
        "y": root.yConstructionAxis,
        "z": root.zConstructionAxis,
    }
    a = m.get(axis)
    if a is None:
        raise RuntimeError(f"Unknown axis '{axis}' — use x, y, or z")
    return a


def bbox_dict(bbox):
    if bbox is None:
        return None
    return {
        "min": [bbox.minPoint.x, bbox.minPoint.y, bbox.minPoint.z],
        "max": [bbox.maxPoint.x, bbox.maxPoint.y, bbox.maxPoint.z],
    }


def camera_info():
    vp = get_app().activeViewport
    cam = vp.camera
    return {
        "eye": [cam.eye.x, cam.eye.y, cam.eye.z],
        "target": [cam.target.x, cam.target.y, cam.target.z],
        "up": [cam.upVector.x, cam.upVector.y, cam.upVector.z],
    }
