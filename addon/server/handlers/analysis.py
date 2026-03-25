"""Analysis handlers — measurements and physical properties.

BUG FIX: measure_distance — the original used result.pointOnEntityOne which
doesn't exist. The correct Fusion API properties are result.pointOne and
result.pointTwo.
"""

import math

import adsk.core
import adsk.fusion

from ._helpers import body_by_name, get_app, get_design, get_root


def measure_distance(entity_one: str, entity_two: str):
    """Measure minimum distance between two entities.

    FIX: Original code used result.pointOnEntityOne / result.pointOnEntityTwo
    which don't exist on MeasureResults. The correct properties are
    result.pointOne and result.pointTwo.
    """
    root = get_root()

    def get_entity(name):
        for i in range(root.bRepBodies.count):
            b = root.bRepBodies.item(i)
            if b.name == name:
                return b
        if "," in name:
            coords = [float(x.strip()) for x in name.split(",")]
            return adsk.core.Point3D.create(*coords)
        raise RuntimeError(f"Entity '{name}' not found")

    e1 = get_entity(entity_one)
    e2 = get_entity(entity_two)

    measure = get_app().measureManager
    result = measure.measureMinimumDistance(e1, e2)

    return {
        "distance": result.value,
        "point_one": [
            result.pointOne.x,
            result.pointOne.y,
            result.pointOne.z,
        ],
        "point_two": [
            result.pointTwo.x,
            result.pointTwo.y,
            result.pointTwo.z,
        ],
    }


def measure_angle(entity_one: str, entity_two: str):
    root = get_root()

    def get_entity(name):
        for i in range(root.bRepBodies.count):
            b = root.bRepBodies.item(i)
            if b.name == name:
                return b.faces.item(0)
        raise RuntimeError(f"Entity '{name}' not found")

    e1 = get_entity(entity_one)
    e2 = get_entity(entity_two)

    measure = get_app().measureManager
    result = measure.measureAngle(e1, e2)

    return {"angle_degrees": math.degrees(result.value)}


def get_physical_properties(body_name: str, accuracy: str = "medium"):
    body = body_by_name(body_name)

    accuracy_map = {
        "low": adsk.fusion.CalculationAccuracy.LowCalculationAccuracy,
        "medium": adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy,
        "high": adsk.fusion.CalculationAccuracy.HighCalculationAccuracy,
        "very_high": adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy,
    }
    acc = accuracy_map.get(accuracy, accuracy_map["medium"])

    props = body.getPhysicalProperties(acc)
    return {
        "mass": props.mass,
        "volume": props.volume,
        "area": props.area,
        "density": props.density,
        "center_of_mass": [
            props.centerOfMass.x,
            props.centerOfMass.y,
            props.centerOfMass.z,
        ],
    }


COMMANDS = {
    "measure_distance": lambda entity_one, entity_two, **_kw: measure_distance(
        entity_one, entity_two
    ),
    "measure_angle": lambda entity_one, entity_two, **_kw: measure_angle(
        entity_one, entity_two
    ),
    "get_physical_properties": lambda body_name, accuracy="medium", **_kw: get_physical_properties(
        body_name, accuracy
    ),
}
