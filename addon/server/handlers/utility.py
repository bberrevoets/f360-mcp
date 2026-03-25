"""Utility handlers — ping, execute_code, undo, delete_all.

BUG FIX: delete_all — the original just reversed timeline deletion which
fails with components. Fixed to delete occurrences first, then timeline items.
"""

import ast
import io
import math
from contextlib import redirect_stdout

import adsk.core
import adsk.fusion

from ._helpers import get_app, get_design, get_root


def ping():
    return {"pong": True}


def execute_code(code: str):
    app = get_app()
    design = get_design()
    root = get_root()

    ns = {
        "adsk": adsk,
        "app": app,
        "ui": app.userInterface,
        "design": design,
        "component": root,
        "math": math,
    }

    buf = io.StringIO()

    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise RuntimeError(f"SyntaxError: {exc}")

    last_expr_value = None
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        last_node = tree.body.pop()
        if tree.body:
            with redirect_stdout(buf):
                exec(
                    compile(
                        ast.Module(body=tree.body, type_ignores=[]),
                        "<mcp>",
                        "exec",
                    ),
                    ns,
                )
        expr_code = compile(
            ast.Expression(body=last_node.value), "<mcp>", "eval"
        )
        with redirect_stdout(buf):
            last_expr_value = eval(expr_code, ns)
    else:
        with redirect_stdout(buf):
            exec(compile(tree, "<mcp>", "exec"), ns)

    output = buf.getvalue()
    result = last_expr_value if last_expr_value is not None else output
    if result is not None:
        try:
            import json

            json.dumps(result)
        except (TypeError, ValueError):
            result = str(result)

    return {"executed": True, "result": result, "output": output}


def undo():
    app = get_app()
    cmd_def = app.userInterface.commandDefinitions.itemById("UndoCommand")
    if cmd_def:
        cmd_def.execute()
    return {"undone": True}


def delete_all():
    """Delete all features and bodies.

    FIX: Original only reversed timeline deletion, which fails when
    components are present. Fixed to:
    1. Delete all occurrences (child components) first
    2. Then delete timeline items in reverse order
    """
    design = get_design()
    root = get_root()

    # First remove all component occurrences
    while root.occurrences.count > 0:
        try:
            root.occurrences.item(0).deleteMe()
        except Exception:
            break

    # Then delete timeline items in reverse
    if hasattr(design, "timeline") and design.timeline.count > 0:
        tl = design.timeline
        for i in range(tl.count - 1, -1, -1):
            try:
                tl.item(i).deleteMe()
            except Exception:
                pass

    return {"deleted": True}


COMMANDS = {
    "ping": lambda **_kw: ping(),
    "execute_code": lambda code, **_kw: execute_code(code),
    "undo": lambda **_kw: undo(),
    "delete_all": lambda **_kw: delete_all(),
}
