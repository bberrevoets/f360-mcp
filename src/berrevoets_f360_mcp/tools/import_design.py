"""Import tools — import STEP and F3D files into the active design."""

from typing import Callable

from fastmcp import FastMCP


def register(mcp: FastMCP, send: Callable) -> None:

    @mcp.tool()
    def import_step(file_path: str) -> dict:
        """Import a STEP file into the current design.

        The imported geometry appears as a child component.
        Use get_scene_info or list_components after import to see the result.

        Args:
            file_path: Absolute path to the .step or .stp file.
        """
        return send("import_step", {"file_path": file_path})

    @mcp.tool()
    def import_f3d(file_path: str) -> dict:
        """Import a Fusion 360 archive (.f3d) into the current design.

        Args:
            file_path: Absolute path to the .f3d file.
        """
        return send("import_f3d", {"file_path": file_path})
