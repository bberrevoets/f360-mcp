"""F360MCP Server Package — CustomEvent bridge architecture."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

LOG_PATH = os.path.join(os.path.expanduser("~"), "f360mcp.log")

_logger = logging.getLogger("f360mcp")
_logger.setLevel(logging.DEBUG)

_fh = RotatingFileHandler(LOG_PATH, maxBytes=2 * 1024 * 1024, backupCount=3)
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(
    logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)
_logger.addHandler(_fh)

_sh = logging.StreamHandler(sys.stdout)
_sh.setLevel(logging.INFO)
_sh.setFormatter(logging.Formatter("[F360MCP] %(message)s"))
_logger.addHandler(_sh)


def get_logger(name: str = None) -> logging.Logger:
    if name:
        return _logger.getChild(name)
    return _logger
