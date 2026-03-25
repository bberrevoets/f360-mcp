"""Parameter handlers — user parameter CRUD.

BUG FIX: create_parameter — the original used params.createInput() which
doesn't exist on UserParameters. The correct method is params.add() which
takes (name, valueInput, unit, comment) directly.
"""

import adsk.core

from ._helpers import get_design


def get_parameters():
    design = get_design()
    params = []
    for param in design.userParameters:
        params.append({
            "name": param.name,
            "value": param.value,
            "expression": param.expression,
            "unit": param.unit,
            "comment": param.comment,
        })
    return {"parameters": params, "count": len(params)}


def create_parameter(name: str, value: float, unit: str, comment: str = ""):
    """Create a new user parameter.

    FIX: Original code used params.createInput() which doesn't exist.
    The correct API is params.add(name, valueInput, unit, comment).
    """
    design = get_design()
    params = design.userParameters
    value_input = adsk.core.ValueInput.createByReal(value)
    params.add(name, value_input, unit, comment)
    return {"created": True, "name": name, "value": value, "unit": unit}


def set_parameter(name: str, value: float):
    design = get_design()
    param = design.userParameters.itemByName(name)
    if not param:
        raise RuntimeError(f"Parameter '{name}' not found")
    param.value = value
    return {"updated": True, "name": name, "value": value}


def delete_parameter(name: str):
    design = get_design()
    param = design.userParameters.itemByName(name)
    if not param:
        raise RuntimeError(f"Parameter '{name}' not found")
    param.deleteMe()
    return {"deleted": True, "name": name}


COMMANDS = {
    "get_parameters": lambda **_kw: get_parameters(),
    "create_parameter": lambda name, value, unit, comment="", **_kw: create_parameter(
        name, value, unit, comment
    ),
    "set_parameter": lambda name, value, **_kw: set_parameter(name, value),
    "delete_parameter": lambda name, **_kw: delete_parameter(name),
}
