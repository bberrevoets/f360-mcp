"""
EventBridge — dispatches work from socket threads to Fusion's main thread.

Uses adsk.core.CustomEvent + a thread-safe queue so all Fusion API calls
happen on the main thread. A 200 ms backup timer fires the custom event
periodically in case fireCustomEvent from a daemon thread is unreliable.
"""

import queue
import threading
import time
import traceback

import adsk.core

from . import get_logger

log = get_logger("bridge")

CUSTOM_EVENT_ID = "F360MCP_BridgeEvent"
TIMER_INTERVAL_MS = 200


class WorkItem:
    __slots__ = ("command", "result", "error", "done")

    def __init__(self, command: dict):
        self.command = command
        self.result = None
        self.error = None
        self.done = threading.Event()


class _MainThreadHandler(adsk.core.CustomEventHandler):
    def __init__(self, bridge: "EventBridge"):
        super().__init__()
        self._bridge = bridge

    def notify(self, args):
        self._bridge.drain_queue()


class EventBridge:
    """Bridge between daemon socket threads and Fusion's main thread."""

    def __init__(self, app: adsk.core.Application, command_handler):
        self._app = app
        self._handler = command_handler
        self._queue: queue.Queue = queue.Queue()

        self._event = app.registerCustomEvent(CUSTOM_EVENT_ID)
        self._event_handler = _MainThreadHandler(self)
        self._event.add(self._event_handler)

        self._timer_running = True
        self._timer_thread = threading.Thread(
            target=self._timer_loop, daemon=True
        )
        self._timer_thread.start()

        log.info("EventBridge initialised (custom event: %s)", CUSTOM_EVENT_ID)

    def submit(self, command: dict, timeout: float = 30.0) -> dict:
        """Queue command for main-thread execution; block until done."""
        cmd_type = command.get("type", "?")

        if cmd_type == "ping":
            log.debug("ping (fast path)")
            return {"status": "success", "result": {"pong": True}}

        log.debug("submit cmd=%s", cmd_type)
        item = WorkItem(command)
        self._queue.put(item)

        try:
            self._app.fireCustomEvent(CUSTOM_EVENT_ID)
        except Exception:
            pass

        if not item.done.wait(timeout=timeout):
            log.warning("Command %s timed out after %ss", cmd_type, timeout)
            return {
                "status": "error",
                "message": f"Command timed out after {timeout}s",
            }

        if item.error is not None:
            log.error("Command %s failed: %s", cmd_type, item.error)
            return {"status": "error", "message": item.error}

        log.debug("Command %s completed", cmd_type)
        return item.result

    def drain_queue(self):
        while True:
            try:
                item: WorkItem = self._queue.get_nowait()
            except queue.Empty:
                break

            cmd_type = item.command.get("type", "?")
            try:
                item.result = self._handler.execute_command(item.command)
            except Exception as exc:
                item.error = f"{exc}\n{traceback.format_exc()}"
                log.error("Main-thread exec of %s raised: %s", cmd_type, exc)
            finally:
                item.done.set()

    def _timer_loop(self):
        interval = TIMER_INTERVAL_MS / 1000.0
        while self._timer_running:
            time.sleep(interval)
            if not self._queue.empty():
                try:
                    self._app.fireCustomEvent(CUSTOM_EVENT_ID)
                except Exception:
                    pass

    def reload_handler(self):
        import importlib

        from . import command_handler as ch_mod

        importlib.reload(ch_mod)
        self._handler = ch_mod.CommandHandler()
        log.info("CommandHandler reloaded")

    def stop(self):
        self._timer_running = False
        try:
            self._event.remove(self._event_handler)
        except Exception:
            pass
        try:
            self._app.unregisterCustomEvent(CUSTOM_EVENT_ID)
        except Exception:
            pass
        log.info("EventBridge stopped")
