"""Berrevoets F360 MCP Server — MCP server for Autodesk Fusion 360."""

__version__ = "0.1.0"


def main():
    """CLI entry point."""
    from .server import cli

    cli()
