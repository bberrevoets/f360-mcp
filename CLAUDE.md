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

```text
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

## Fusion 360 Python API — Lessons Learned

Practical gotchas encountered while using `execute_code` against the
Fusion API. Useful when writing new handler tools or helping users via
`execute_code`.

### Text engraving via `SketchText`

**Don't** iterate `sketch.profiles` after adding a `SketchText` — the
profiles you get back are the **projected boundaries of the sketch's
host face** (outer outline + any holes), NOT the text glyphs. Extruding
those profiles cuts the whole face and removes far too much material.

**Do** pass the `SketchText` object **directly** to
`extrudes.createInput()`:

```python
ti = sk.sketchTexts.createInput2('Berrevoets Systems', 0.35)
ti.setAsMultiLine(p1, p2, hAlign, vAlign, 0)
text = sk.sketchTexts.add(ti)

# Pass the SketchText itself — not sk.profiles
ei = extrudes.createInput(text, adsk.fusion.FeatureOperations.CutFeatureOperation)
ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal(-0.03))  # 0.3mm
extrudes.add(ei)
```

`createInput` accepts `Profile`, `ObjectCollection of Profile`, or
`SketchText` — the last one is the right choice for text engraving.

### Threads have a minimum length

`ThreadFeatures.add()` raises `RuntimeError: 3 : invalid input thread
length` if the threaded cylindrical face is too short. M6×1 internal
needs ≥ 2 mm of cylinder. Plan hole depth / countersink depth so enough
straight cylinder remains.

### Countersink via tapered extrude-cut

Simple approach:

1. Create an offset plane at the top face of the body.
2. Sketch circles with the **top diameter** of the countersink.
3. `extrudeInput.taperAngle = ValueInput.createByString("-45 deg")`
4. `setDistanceExtent(False, -depth)` — negative distance goes into
   the body from the offset plane.

Negative taper + negative distance: profile **shrinks** as the cut goes
into the material, producing a cone wider at the top.

Verified: top_r=5mm, depth=2mm, taper=-45° → 90° included angle
countersink ending at 3mm radius (matches an M6 hole).

Starting the sketch on the pre-drilled hole edge (profile radius =
hole radius) triggers `No target body found to cut or intersect!` —
offset the sketch above the top face instead.

### `ThreadFeatures` API — createThreadInfo signature

Working call for modeled M6×1 internal threads:

```python
thread_info = threads.createThreadInfo(
    True,                    # isInternal
    'ISO Metric profile',    # threadType
    'M6x1',                  # threadDesignation
    '6H')                    # threadClass

ti = threads.createInput(faces_collection, thread_info)
ti.isModeled = True          # True = visible helical geometry
# Omit ti.threadLength to use the full face length (safer than guessing)
threads.add(ti)
```

### Cylindrical face discovery

`face.geometry.objectType` returns `adsk::core::Cylinder::classType()`
(use the full class type, not the simple name) when the face is a
cylinder. Filter by radius AND origin position to distinguish bolt
holes from the center bore.

```python
for face in body.faces:
    g = face.geometry
    if g and g.objectType == adsk.core.Cylinder.classType():
        if abs(g.radius - BOLT_R) < 1e-3:
            ...
```

### Top face detection

To find the "+Z face" of a body with multiple planar faces:

```python
for face in body.faces:
    g = face.geometry
    if g and g.objectType == adsk.core.Plane.classType():
        eval_ = face.evaluator
        ok, normal = eval_.getNormalAtPoint(face.pointOnFace)
        if ok and normal.z > 0.99:
            # top face; pick the largest if multiple
            ...
```

Chamfered/filleted bodies have multiple near-horizontal faces —
always pick the one with the **largest area**.

### Save active document programmatically

```python
hub = app.data.activeHub
project = app.data.activeProject
root_folder = project.rootFolder
app.activeDocument.saveAs("Test Piece", root_folder, "description", "")
```

Returns `True` on success. This does NOT trigger a UI dialog. Use
this to rename/save an `Untitled` doc after building it via API.

### Undo is a feature-level operation, not per-sketch

`app.undo()` and the `undo` MCP tool undo the **last timeline
feature**. They don't remove sketches individually — use
`sketch.deleteMe()` for that. Note that `deleteMe()` shifts remaining
sketch indices, so iterate **backwards** when deleting in a loop:

```python
for i in range(sketches.count - 1, -1, -1):
    if should_delete(sketches.item(i)):
        sketches.item(i).deleteMe()
```

### Do NOT create or close documents via `execute_code`

Bricks the MCP connection. `saveAs` on the active document is fine;
creating a new document or closing the active one via Python triggers
UI state the add-in's event bridge cannot recover from.

### `execute_code` variables don't persist across calls

Each call is a fresh Python scope. Pre-defined variables (`app`,
`ui`, `design`, `component`, `adsk`, `math`) are always available but
anything you assign inside one call is gone by the next. Re-fetch
bodies, sketches, etc. by name every time.
