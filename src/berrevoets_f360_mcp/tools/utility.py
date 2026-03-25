"""Utility tools — ping, execute_code, undo, delete_all."""

from typing import Callable

from fastmcp import FastMCP


def register(mcp: FastMCP, send: Callable) -> None:

    @mcp.tool()
    def ping() -> dict:
        """Check if the Fusion 360 add-in is running and responsive."""
        return send("ping")

    @mcp.tool()
    def execute_code(code: str) -> dict:
        """Execute arbitrary Python code in Fusion 360's context.

        Pre-defined variables available in the code:
        - app: adsk.core.Application
        - ui: app.userInterface
        - design: active design (adsk.fusion.Design)
        - component: root component
        - adsk: the adsk module
        - math: the math module

        Variables do NOT persist between calls — re-fetch objects each time.
        NEVER create or close documents (bricks the MCP connection).

        Args:
            code: Python code to execute. The last expression's value is returned.
        """
        return send("execute_code", {"code": code})

    @mcp.tool()
    def undo() -> dict:
        """Undo the last operation in Fusion 360."""
        return send("undo")

    @mcp.tool()
    def delete_all() -> dict:
        """Delete all features and bodies from the active design.

        Removes all timeline items in reverse order. Use with caution.
        """
        return send("delete_all")
