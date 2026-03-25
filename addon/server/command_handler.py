"""
Command handler — thin dispatch router.

Aggregates all handler modules and routes commands by name.
Each handler module exports a COMMANDS dict mapping command names
to handler functions.
"""

from . import get_logger
from .handlers import analysis, export, import_design, parameters, scene, utility

log = get_logger("handler")

_ALL_COMMANDS = {}
for _module in [scene, export, import_design, analysis, parameters, utility]:
    _ALL_COMMANDS.update(_module.COMMANDS)


class CommandHandler:
    """Routes incoming commands to the appropriate handler function."""

    def execute_command(self, command: dict) -> dict:
        cmd_type = command.get("type", "")
        params = command.get("params", {})

        handler = _ALL_COMMANDS.get(cmd_type)
        if handler is None:
            raise RuntimeError(f"Unknown command: {cmd_type}")

        log.debug("Executing: %s", cmd_type)
        result = handler(**params)

        return {"status": "success", "result": result}
