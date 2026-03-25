"""Scene query tools — read-only inspection of the active Fusion 360 design."""

from typing import Callable

from fastmcp import FastMCP


def register(mcp: FastMCP, send: Callable) -> None:

    @mcp.tool()
    def get_scene_info() -> dict:
        """Get overview of the active Fusion 360 design.

        Returns design name, body list, sketch list, feature/timeline counts,
        and camera position. Only shows root-level bodies (not inside
        child components).
        """
        return send("get_scene_info")

    @mcp.tool()
    def get_object_info(name: str) -> dict:
        """Get detailed info about a body or sketch by name.

        For bodies: volume, area, material, face/edge/vertex counts,
        bounding box. For sketches: profile count, curve count, visibility.
        """
        return send("get_object_info", {"name": name})

    @mcp.tool()
    def list_components() -> dict:
        """List all components in the design.

        Returns a flat list with is_root flag. Does not show hierarchy.
        """
        return send("list_components")
