"""
TCP connection to the F360MCP add-in running inside Fusion 360.

The add-in listens on localhost:9876 and speaks newline-delimited JSON.
"""

import json
import logging
import socket
import time
from typing import Any

log = logging.getLogger("berrevoets_f360_mcp.connection")

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9876
_RECV_BUF = 65536
_TIMEOUT = 30.0
_PING_TIMEOUT = 5.0
_MAX_RETRIES = 2
_RETRY_DELAY = 1.0


class Fusion360Connection:
    """Persistent TCP connection to the Fusion 360 add-in socket server."""

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self._sock: socket.socket | None = None

    def connect(self) -> bool:
        if self._sock is not None:
            return True
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(_PING_TIMEOUT)
            s.connect((self.host, self.port))
            self._sock = s
            log.info("Connected to Fusion 360 at %s:%s", self.host, self.port)
            return True
        except Exception as exc:
            log.error("Failed to connect: %s", exc)
            self._sock = None
            return False

    def disconnect(self):
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    def reconnect(self) -> bool:
        self.disconnect()
        return self.connect()

    @property
    def connected(self) -> bool:
        return self._sock is not None

    def ping(self) -> bool:
        try:
            self.send_command("ping")
            return True
        except Exception:
            return False

    def ensure_connected(self) -> bool:
        if self._sock is not None and self.ping():
            return True
        log.warning("Connection lost, attempting reconnect...")
        return self.reconnect()

    def send_command(
        self,
        command_type: str,
        params: dict[str, Any] | None = None,
        retries: int = _MAX_RETRIES,
    ) -> dict:
        """Send a JSON command and block until a JSON response arrives."""
        if not self._sock and not self.connect():
            raise ConnectionError(
                "Not connected to Fusion 360. Make sure the add-in is running."
            )

        payload = json.dumps({"type": command_type, "params": params or {}}) + "\n"

        try:
            self._sock.sendall(payload.encode("utf-8"))
            self._sock.settimeout(_TIMEOUT)
            response = self._recv_json()
        except (socket.timeout, OSError, ConnectionError) as exc:
            log.error("Socket error: %s", exc)
            self.disconnect()
            if retries > 0:
                log.info("Retrying (%d left)...", retries)
                time.sleep(_RETRY_DELAY)
                if self.connect():
                    return self.send_command(command_type, params, retries=retries - 1)
            raise ConnectionError(f"Lost connection to Fusion 360: {exc}") from exc

        if response.get("status") == "error":
            raise RuntimeError(response.get("message", "Unknown error"))

        return response.get("result", {})

    def _recv_json(self) -> dict:
        buf = b""
        while True:
            chunk = self._sock.recv(_RECV_BUF)
            if not chunk:
                raise ConnectionError("Connection closed by Fusion 360")
            buf += chunk

            if b"\n" in buf:
                line, _rest = buf.split(b"\n", 1)
                return json.loads(line)

            try:
                return json.loads(buf)
            except json.JSONDecodeError:
                continue


_connection: Fusion360Connection | None = None


def get_connection(
    *, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT
) -> Fusion360Connection:
    global _connection
    if _connection is not None:
        return _connection
    _connection = Fusion360Connection(host, port)
    _connection.connect()
    return _connection


def reset_connection():
    global _connection
    if _connection:
        _connection.disconnect()
    _connection = None
