"""Analysis tools — measurements and physical properties."""

from typing import Callable

from fastmcp import FastMCP


def register(mcp: FastMCP, send: Callable) -> None:

    @mcp.tool()
    def measure_distance(entity_one: str, entity_two: str) -> dict:
        """Measure the minimum distance between two entities.

        Entities can be body names or point coordinates as "x,y,z".

        Args:
            entity_one: Body name or point coordinates (e.g. "0,0,0").
            entity_two: Body name or point coordinates.

        Returns:
            distance (cm), point_one, point_two — the closest points.
        """
        return send("measure_distance", {
            "entity_one": entity_one,
            "entity_two": entity_two,
        })

    @mcp.tool()
    def measure_angle(entity_one: str, entity_two: str) -> dict:
        """Measure the angle between two bodies (uses their first face).

        Args:
            entity_one: Name of the first body.
            entity_two: Name of the second body.

        Returns:
            angle_degrees — the angle in degrees.
        """
        return send("measure_angle", {
            "entity_one": entity_one,
            "entity_two": entity_two,
        })

    @mcp.tool()
    def get_physical_properties(
        body_name: str, accuracy: str = "medium"
    ) -> dict:
        """Get physical properties of a body.

        Args:
            body_name: Name of the body.
            accuracy: Calculation accuracy — low, medium, high, or very_high.

        Returns:
            mass (kg), volume (cm³), area (cm²), density (kg/cm³),
            center_of_mass [x, y, z] (cm).
        """
        return send("get_physical_properties", {
            "body_name": body_name,
            "accuracy": accuracy,
        })
