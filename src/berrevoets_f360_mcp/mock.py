"""
Mock responses for testing without Fusion 360 running.

Returns plausible data for all implemented commands.
"""


def mock_response(command_type: str, params: dict) -> dict:
    """Return a mock response for the given command."""
    handler = _HANDLERS.get(command_type)
    if handler:
        return {"status": "success", "result": handler(params), "mode": "mock"}
    return {
        "status": "error",
        "message": f"Unknown command in mock mode: {command_type}",
        "mode": "mock",
    }


def _ping(_p: dict) -> dict:
    return {"pong": True}


def _get_scene_info(_p: dict) -> dict:
    return {
        "design_name": "MockDesign",
        "design_type": "DirectDesignType",
        "bodies": [
            {
                "name": "Body1",
                "volume": 125.0,
                "area": 150.0,
                "material": "Steel",
                "is_visible": True,
            }
        ],
        "sketches": [
            {"name": "Sketch1", "profile_count": 1, "is_visible": True}
        ],
        "bodies_count": 1,
        "sketches_count": 1,
        "features_count": 1,
        "timeline_count": 1,
        "camera": {
            "eye": [10.0, 10.0, 10.0],
            "target": [0.0, 0.0, 0.0],
            "up": [0.0, 1.0, 0.0],
        },
    }


def _get_object_info(p: dict) -> dict:
    name = p.get("name", "Body1")
    return {
        "found": True,
        "type": "body",
        "name": name,
        "volume": 125.0,
        "area": 150.0,
        "material": "Steel",
        "is_visible": True,
        "faces_count": 6,
        "edges_count": 12,
        "vertices_count": 8,
        "bounding_box": {
            "min": [0.0, 0.0, 0.0],
            "max": [5.0, 5.0, 5.0],
        },
    }


def _list_components(_p: dict) -> dict:
    return {
        "components": [{"name": "Root", "is_root": True}],
        "count": 1,
    }


def _export_stl(p: dict) -> dict:
    return {
        "exported": True,
        "body": p.get("body_name", "Body1"),
        "file_path": p.get("file_path", "/mock/Body1.stl"),
    }


def _export_step(p: dict) -> dict:
    return {
        "exported": True,
        "file_path": p.get("file_path", "/mock/design.step"),
    }


def _export_f3d(p: dict) -> dict:
    return {
        "exported": True,
        "file_path": p.get("file_path", "/mock/design.f3d"),
    }


def _import_step(p: dict) -> dict:
    return {
        "imported": True,
        "file_path": p.get("file_path", "/mock/import.step"),
        "component_name": "ImportedComponent",
    }


def _import_f3d(p: dict) -> dict:
    return {
        "imported": True,
        "file_path": p.get("file_path", "/mock/import.f3d"),
    }


def _measure_distance(p: dict) -> dict:
    return {
        "distance": 5.0,
        "point_one": [0.0, 0.0, 0.0],
        "point_two": [5.0, 0.0, 0.0],
    }


def _measure_angle(_p: dict) -> dict:
    return {"angle_degrees": 90.0}


def _get_physical_properties(p: dict) -> dict:
    return {
        "mass": 0.981,
        "volume": 125.0,
        "area": 150.0,
        "density": 0.00785,
        "center_of_mass": [2.5, 2.5, 2.5],
    }


def _get_parameters(_p: dict) -> dict:
    return {
        "parameters": [
            {
                "name": "width",
                "value": 5.0,
                "expression": "5.0",
                "unit": "cm",
                "comment": "Box width",
            }
        ],
        "count": 1,
    }


def _create_parameter(p: dict) -> dict:
    return {
        "created": True,
        "name": p.get("name", "param1"),
        "value": p.get("value", 1.0),
        "unit": p.get("unit", "cm"),
    }


def _set_parameter(p: dict) -> dict:
    return {
        "updated": True,
        "name": p.get("name", "param1"),
        "value": p.get("value", 1.0),
    }


def _delete_parameter(p: dict) -> dict:
    return {"deleted": True, "name": p.get("name", "param1")}


def _execute_code(p: dict) -> dict:
    return {
        "executed": True,
        "result": None,
        "output": f"[mock] Would execute: {p.get('code', '')[:100]}",
    }


def _undo(_p: dict) -> dict:
    return {"undone": True}


def _delete_all(_p: dict) -> dict:
    return {"deleted": True}


_HANDLERS = {
    "ping": _ping,
    "get_scene_info": _get_scene_info,
    "get_object_info": _get_object_info,
    "list_components": _list_components,
    "export_stl": _export_stl,
    "export_step": _export_step,
    "export_f3d": _export_f3d,
    "import_step": _import_step,
    "import_f3d": _import_f3d,
    "measure_distance": _measure_distance,
    "measure_angle": _measure_angle,
    "get_physical_properties": _get_physical_properties,
    "get_parameters": _get_parameters,
    "create_parameter": _create_parameter,
    "set_parameter": _set_parameter,
    "delete_parameter": _delete_parameter,
    "execute_code": _execute_code,
    "undo": _undo,
    "delete_all": _delete_all,
}
