"""Tool registration — imports all tool modules and registers them with the MCP server."""

from typing import Callable

from fastmcp import FastMCP


def register_all(mcp: FastMCP, send: Callable) -> None:
    """Register all tools with the MCP server."""
    from . import analysis, export, import_design, parameters, scene, utility

    for module in [scene, export, import_design, analysis, parameters, utility]:
        module.register(mcp, send)
