# Berrevoets F360 MCP Server

MCP server for Autodesk Fusion 360 — file management, export, import,
and design queries.

## Overview

This is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
server that connects AI assistants (Claude Code, Cursor, etc.) to
Autodesk Fusion 360. It enables AI-driven 3D CAD operations through
a clean, modular tool interface.

### Architecture

```text
AI Assistant (stdio) --> F360 MCP Server (TCP:9876) --> F360 Add-in --> Fusion 360 API
```

Two components:

- **MCP Server** (`berrevoets-f360-mcp`) — Python package using FastMCP,
  communicates with Claude Code via stdio
- **Fusion 360 Add-in** (`addon/`) — Python scripts running inside
  Fusion 360, exposes the API via TCP socket

## Installation

### MCP Server

```bash
uv tool install berrevoets-f360-mcp
```

Or run directly:

```bash
uvx berrevoets-f360-mcp --mode socket
```

### Fusion 360 Add-in

```bash
python scripts/install_addon.py
```

Then enable "F360MCP" in Fusion 360 under Utilities > Add-Ins.

### Claude Code Configuration

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "fusion360": {
      "command": "uvx",
      "args": ["berrevoets-f360-mcp", "--mode", "socket"]
    }
  }
}
```

## Available Tools

### Scene Queries

| Tool | Description |
|------|-------------|
| `get_scene_info` | Design overview (bodies, sketches, counts) |
| `get_object_info` | Detailed body/sketch info + bounding box |
| `list_components` | Flat component list |

### Export

| Tool | Description |
|------|-------------|
| `export_stl` | Export single body as STL |
| `export_step` | Export entire design as STEP |
| `export_f3d` | Export as Fusion 360 archive |

### Import

| Tool | Description |
|------|-------------|
| `import_step` | Import STEP file into current design |
| `import_f3d` | Import Fusion 360 archive |

### Analysis

| Tool | Description |
|------|-------------|
| `measure_distance` | Minimum distance between entities |
| `measure_angle` | Angle between two bodies |
| `get_physical_properties` | Mass, volume, area, density |

### Parameters

| Tool | Description |
|------|-------------|
| `get_parameters` | List user parameters |
| `create_parameter` | Create new parameter |
| `set_parameter` | Update parameter value |
| `delete_parameter` | Delete parameter |

### Utility

| Tool | Description |
|------|-------------|
| `ping` | Health check |
| `execute_code` | Run arbitrary Python in Fusion 360 |
| `undo` | Undo last operation |
| `delete_all` | Clear all features |

## Development

### Testing (mock mode)

```bash
uvx berrevoets-f360-mcp --mode mock
```

### Project structure

```text
src/berrevoets_f360_mcp/    # MCP server (FastMCP + tools)
addon/                       # Fusion 360 add-in (socket bridge)
scripts/                     # Install/uninstall helpers
tests/                       # Mock-mode tests
```

## License

MIT License - Copyright (c) 2026 Bert Berrevoets / Berrevoets Systems
