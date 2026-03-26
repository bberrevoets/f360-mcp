# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project Overview

Berrevoets F360 MCP Server bridges AI assistants to Autodesk Fusion 360 via
the Model Context Protocol. Two components work together:

```text
AI Assistant ──stdio──▶ MCP Server (Python/FastMCP)
                            │
                        TCP:9876
                            ▼
                      Fusion 360 Add-in ──▶ Fusion 360 API
```

The MCP server (`src/berrevoets_f360_mcp/`) runs as a standalone process.
The add-in (`addon/`) runs inside Fusion 360, accepting commands over a TCP
socket and dispatching them to the Fusion 360 API on the main thread via a
`CustomEvent` + `EventBridge` pattern.

## Build and Development Commands

```bash
# Install for development (editable)
uv sync --dev

# Run the MCP server (real Fusion 360)
uvx berrevoets-f360-mcp --mode socket

# Run the MCP server (mock mode, no Fusion 360 needed)
uvx berrevoets-f360-mcp --mode mock

# Run all tests (mock mode only)
pytest tests/

# Run a single test
pytest tests/test_tools.py::test_ping

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Lint markdown (120 char line limit)
markdownlint "**/*.md"

# Install add-in to Fusion 360
python scripts/install_addon.py
```

## Architecture

### MCP Server (`src/berrevoets_f360_mcp/`)

- **`server.py`** — FastMCP entry point with Click CLI. Global `send()` routes
  commands to either the TCP socket or mock backend based on `--mode`.
- **`connection.py`** — `Fusion360Connection` singleton for persistent TCP.
  Auto-reconnects with retry logic (2 retries, 1s delay, 30s timeout).
- **`mock.py`** — Returns plausible test data for all 19 tools. Used by tests
  and `--mode mock`.
- **`tools/`** — Each module (scene, export, import_design, analysis,
  parameters, utility) exports a `register(mcp, send)` function. All tools
  are registered in `tools/__init__.py:register_all()`.

### Fusion 360 Add-in (`addon/`)

- **`F360MCP.py`** — Add-in entry (`run`/`stop`). Logs to `~/f360mcp.log`.
- **`server/socket_server.py`** — TCP server with auto-restart and exponential
  backoff (up to 10 attempts). One daemon thread per client connection.
- **`server/event_bridge.py`** — Thread-safe queue + `CustomEvent` dispatches
  work to Fusion 360's main thread. 200ms backup timer ensures events fire.
  30-second timeout per command.
- **`server/command_handler.py`** — Routes command type strings to handler
  functions. Each handler module in `handlers/` exports a
  `COMMANDS = {name: handler_fn}` dict.
- **`server/handlers/`** — Mirror the tool modules: scene, export,
  import_design, analysis, parameters, utility. Shared helpers in
  `_helpers.py`.

### Wire Protocol

Newline-delimited JSON over TCP (localhost:9876).

```json
Request:  {"type": "command_name", "params": {...}}
Success:  {"status": "success", "result": {...}}
Error:    {"status": "error", "message": "..."}
```

### Adding a New Tool

1. Add handler function in `addon/server/handlers/<category>.py` and register
   it in that module's `COMMANDS` dict.
2. Add mock response in `src/berrevoets_f360_mcp/mock.py`.
3. Add MCP tool definition in `src/berrevoets_f360_mcp/tools/<category>.py`
   using `@mcp.tool()` inside the `register()` function.
4. Add a test in `tests/test_tools.py`.

## Code Conventions

- **Python 3.11+**, line length 100 (Ruff), strict MyPy
- **Ruff rules:** E (pycodestyle), F (pyflakes), I (isort), W (warnings)
- **Markdown:** 120 character line limit (`.markdownlint.json`)
- All Fusion 360 API calls **must** run on the main thread — always go
  through the `EventBridge`, never call `adsk.*` from socket threads
- The add-in uses Fusion 360's bundled Python (3.12); the MCP server uses
  the system Python (3.11+). They are separate runtimes.

## Testing

Tests run in mock mode only — no Fusion 360 required. The test file
(`tests/test_tools.py`) imports `mock_send` directly and validates response
structure for all tools. There are currently 21 test cases.
