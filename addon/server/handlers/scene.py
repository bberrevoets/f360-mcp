"""Scene query handlers — read-only inspection of the active design."""

from ._helpers import bbox_dict, camera_info, get_design, get_root


def get_scene_info():
    design = get_design()
    root = get_root()

    bodies = []
    for i in range(root.bRepBodies.count):
        b = root.bRepBodies.item(i)
        bodies.append({
            "name": b.name,
            "volume": b.volume,
            "area": b.area,
            "material": b.material.name if b.material else None,
            "is_visible": b.isVisible,
        })

    sketches = []
    for i in range(root.sketches.count):
        s = root.sketches.item(i)
        sketches.append({
            "name": s.name,
            "profile_count": s.profiles.count,
            "is_visible": s.isVisible,
        })

    return {
        "design_name": design.parentDocument.name,
        "design_type": design.productType,
        "bodies": bodies,
        "sketches": sketches,
        "bodies_count": root.bRepBodies.count,
        "sketches_count": root.sketches.count,
        "features_count": root.features.count,
        "timeline_count": (
            design.timeline.count if hasattr(design, "timeline") else 0
        ),
        "camera": camera_info(),
    }


def get_object_info(name: str):
    root = get_root()

    for i in range(root.bRepBodies.count):
        b = root.bRepBodies.item(i)
        if b.name == name:
            return {
                "found": True,
                "type": "body",
                "name": name,
                "volume": b.volume,
                "area": b.area,
                "material": b.material.name if b.material else None,
                "is_visible": b.isVisible,
                "faces_count": b.faces.count,
                "edges_count": b.edges.count,
                "vertices_count": b.vertices.count,
                "bounding_box": bbox_dict(b.boundingBox),
            }

    for i in range(root.sketches.count):
        s = root.sketches.item(i)
        if s.name == name:
            return {
                "found": True,
                "type": "sketch",
                "name": name,
                "is_visible": s.isVisible,
                "profile_count": s.profiles.count,
                "curve_count": s.sketchCurves.count,
            }

    return {"found": False, "name": name}


def list_components():
    root = get_root()
    components = [{"name": root.name, "is_root": True}]
    for occ in root.allOccurrences:
        components.append({
            "name": occ.component.name,
            "is_root": False,
            "is_visible": occ.isVisible,
        })
    return {"components": components, "count": len(components)}


COMMANDS = {
    "get_scene_info": lambda **_kw: get_scene_info(),
    "get_object_info": lambda name, **_kw: get_object_info(name),
    "list_components": lambda **_kw: list_components(),
}
