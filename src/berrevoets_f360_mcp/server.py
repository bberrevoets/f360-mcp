"""
Berrevoets F360 MCP Server — FastMCP-based server for Fusion 360.

Communicates with the F360MCP add-in via TCP socket (localhost:9876).
Supports --mode socket (real Fusion 360) or --mode mock (testing).
"""

import logging

import click
from fastmcp import FastMCP

from .connection import DEFAULT_HOST, DEFAULT_PORT, get_connection, reset_connection
from .mock import mock_response
from .tools import register_all

log = logging.getLogger("berrevoets_f360_mcp.server")

mcp = FastMCP(
    "Berrevoets F360 MCP",
    description="MCP server for Autodesk Fusion 360 — file management, export, import, and design queries",
)

_mode = "socket"
_port = DEFAULT_PORT


def send(command_type: str, params: dict | None = None) -> dict:
    """Route a command to the add-in (socket) or mock handler."""
    if _mode == "mock":
        result = mock_response(command_type, params or {})
        if result.get("status") == "error":
            raise RuntimeError(result.get("message", "Mock error"))
        return result.get("result", {})

    try:
        conn = get_connection(host=DEFAULT_HOST, port=_port)
        return conn.send_command(command_type, params)
    except Exception:
        reset_connection()
        raise


register_all(mcp, send)


# -- MCP Resources ----------------------------------------------------------

@mcp.resource("fusion360://status")
def resource_status() -> str:
    """Check connection status to Fusion 360."""
    try:
        result = send("ping")
        return f"Connected: {result}"
    except Exception as exc:
        return f"Disconnected: {exc}"


@mcp.resource("fusion360://design")
def resource_design() -> str:
    """Get the current design tree."""
    import json

    result = send("get_scene_info")
    return json.dumps(result, indent=2)


@mcp.resource("fusion360://parameters")
def resource_parameters() -> str:
    """Get user parameters from the active design."""
    import json

    result = send("get_parameters")
    return json.dumps(result, indent=2)


# -- CLI entry point ---------------------------------------------------------

@click.command()
@click.option(
    "--mode",
    type=click.Choice(["socket", "mock"]),
    default="socket",
    help="Connection mode: socket (real Fusion 360) or mock (testing).",
)
@click.option(
    "--port",
    type=int,
    default=DEFAULT_PORT,
    help=f"TCP port for the Fusion 360 add-in (default: {DEFAULT_PORT}).",
)
def cli(mode: str, port: int):
    """Start the Berrevoets F360 MCP server."""
    global _mode, _port
    _mode = mode
    _port = port

    logging.basicConfig(level=logging.INFO)
    log.info("Starting in %s mode (port %d)", mode, port)

    mcp.run(transport="stdio")
