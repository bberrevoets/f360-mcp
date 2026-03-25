"""Parameter tools — manage user parameters in the active design."""

from typing import Callable

from fastmcp import FastMCP


def register(mcp: FastMCP, send: Callable) -> None:

    @mcp.tool()
    def get_parameters() -> dict:
        """List all user parameters in the active design.

        Returns name, value, expression, unit, and comment for each parameter.
        """
        return send("get_parameters")

    @mcp.tool()
    def create_parameter(
        name: str, value: float, unit: str, comment: str = ""
    ) -> dict:
        """Create a new user parameter.

        Args:
            name: Parameter name (must be unique).
            value: Numeric value.
            unit: Unit string (e.g. "mm", "cm", "in", "deg").
            comment: Optional description.
        """
        return send("create_parameter", {
            "name": name,
            "value": value,
            "unit": unit,
            "comment": comment,
        })

    @mcp.tool()
    def set_parameter(name: str, value: float) -> dict:
        """Update an existing user parameter's value.

        Args:
            name: Parameter name.
            value: New numeric value.
        """
        return send("set_parameter", {"name": name, "value": value})

    @mcp.tool()
    def delete_parameter(name: str) -> dict:
        """Delete a user parameter.

        Args:
            name: Parameter name to delete.
        """
        return send("delete_parameter", {"name": name})
