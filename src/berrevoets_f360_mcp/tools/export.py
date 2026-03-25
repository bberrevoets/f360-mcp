"""Export tools — export designs to STL, STEP, or F3D files."""

from typing import Callable

from fastmcp import FastMCP


def register(mcp: FastMCP, send: Callable) -> None:

    @mcp.tool()
    def export_stl(body_name: str, file_path: str = "") -> dict:
        """Export a single body as an STL file.

        Args:
            body_name: Name of the body to export (use get_scene_info to find names).
            file_path: Output file path. Defaults to Desktop/{body_name}.stl.
        """
        params: dict = {"body_name": body_name}
        if file_path:
            params["file_path"] = file_path
        return send("export_stl", params)

    @mcp.tool()
    def export_step(file_path: str = "") -> dict:
        """Export the entire design as a STEP file.

        Exports all components and bodies. Unlike STL, STEP preserves
        exact geometry (BREP), making it ideal for CAD interchange.

        Args:
            file_path: Output file path. Defaults to Desktop/{design_name}.step.
        """
        params: dict = {}
        if file_path:
            params["file_path"] = file_path
        return send("export_step", params)

    @mcp.tool()
    def export_f3d(file_path: str = "") -> dict:
        """Export the entire design as a Fusion 360 archive (.f3d).

        Includes full parametric history, sketches, and timeline.

        Args:
            file_path: Output file path. Defaults to Desktop/{design_name}.f3d.
        """
        params: dict = {}
        if file_path:
            params["file_path"] = file_path
        return send("export_f3d", params)
