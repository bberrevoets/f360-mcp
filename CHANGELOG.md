# Changelog

All notable changes to the Berrevoets F360 MCP Server will be
documented in this file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Attributors

- **Bert Berrevoets** — Project creator and maintainer
- **Claude** — AI pair programmer

## [Unreleased]

### Added

Author: *Claude*

- CLAUDE.md with project guidance for Claude Code
- MCP Resources section in README (status, design, parameters)
- Development prerequisites, setup, linting, and testing
  instructions in README
- `*.code-workspace` to `.gitignore` (machine-specific paths)

## [0.1.0] - 2026-03-26

### Added

Author: *Bert Berrevoets*

- Initial release with file management and design query tools
- FastMCP-based MCP server with stdio transport
- TCP connection to Fusion 360 add-in (localhost:9876)
- Mock mode for testing without Fusion 360 running
- Scene query tools: `get_scene_info`, `get_object_info`,
  `list_components`
- Export tools: `export_stl`, `export_step`, `export_f3d`
- Import tools: `import_step`, `import_f3d`
- Analysis tools: `measure_distance`, `measure_angle`,
  `get_physical_properties`
- Parameter tools: `get_parameters`, `create_parameter`,
  `set_parameter`, `delete_parameter`
- Utility tools: `ping`, `execute_code`, `undo`, `delete_all`
- Fusion 360 add-in with modular handler architecture
- Install/uninstall scripts for the add-in

### Fixed

Author: *Bert Berrevoets*

- `export_step` — no longer passes body to
  `createSTEPExportOptions` (exports full design correctly)
- `measure_distance` — uses correct `result.pointOne` /
  `result.pointTwo` instead of non-existent
  `result.pointOnEntityOne`
- `create_parameter` — uses `params.add()` instead of
  non-existent `params.createInput()`
- `delete_all` — deletes component occurrences before
  timeline items to prevent failures
