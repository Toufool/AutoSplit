"""
Capture everything written to the console (``print``, ``warnings``, ``logging``'s last-resort
handler, uncaught tracebacks) without suppressing it, and re-broadcast each completed line as a Qt
signal so the GUI can surface it in the log footer.

The real ``sys.stdout`` / ``sys.stderr`` are *teed*, never replaced: writes still reach the original
streams byte-for-byte (this keeps the ``--auto-controlled`` LiveSplit stdout protocol intact), and a
copy of each line is emitted on top.
"""

from __future__ import annotations

import sys
import threading
from collections import deque
from datetime import datetime
from typing import TextIO, cast, override

from PySide6 import QtCore, QtGui, QtWidgets

LOG_HISTORY_MAX_LINES = 5000
"""A line is more than enough context for a footer, but keep a generous scrollback for the panel."""
TIMESTAMP_FORMAT = "%H:%M:%S.%f"
"""Time-only (no date) timestamp prefixed to each displayed log line. `%f` is microseconds; the last
3 digits are trimmed off at format time to leave milliseconds."""

EXCLUDED_SUBSTRINGS = (
    # The `keyboard` library prints this on Linux when AutoSplit isn't in the `input` group.
    # AutoSplit already surfaces this properly via `error_messages.linux_groups()`.
    "You must be in the 'input' group to access global events",
)
"""Substrings of known-benign dependency messages to hide from the footer/history because they would
mislead users. These are still written to the real console: only the in-app log is filtered"""

LogLine = tuple[str, str, bool]
"""A logged line: ``(timestamp, text, is_stderr)``. ``is_stderr`` marks warnings/errors."""


class LogEmitter(QtCore.QObject):
    """Thread-safe fan-out of logged lines to the GUI, with a bounded scrollback buffer."""

    line_logged = QtCore.Signal(str, str, bool)
    """Emitted once per completed line: ``(timestamp, text, is_stderr)``."""

    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()
        self._history: deque[LogLine] = deque(maxlen=LOG_HISTORY_MAX_LINES)

    def emit_line(self, text: str, *, is_stderr: bool):
        # The console already received this (the tee writes before emitting); only the in-app log
        # filters out blank lines (e.g. a lone "\n" write) and known-benign noise.
        if not text or any(excluded in text for excluded in EXCLUDED_SUBSTRINGS):
            return
        # Stamp at capture time (on the writing thread) so the time reflects when it was logged.
        # Naive local wall-clock time is intentional for a log footer (DTZ005: no tz wanted).
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)[:-3] + ":"  # noqa: DTZ005
        with self._lock:
            self._history.append((timestamp, text, is_stderr))
        # Queued across threads thanks to Qt's auto-connection: safe to call from any thread.
        self.line_logged.emit(timestamp, text, is_stderr)

    def history(self) -> list[LogLine]:
        """Snapshot of the lines logged so far, oldest first."""
        with self._lock:
            return list(self._history)


LOG_EMITTER = LogEmitter()
"""Process-wide singleton. The GUI connects to this; the tee streams write to it."""


class _TeeStream:
    """
    A text stream that forwards to a real stream (if any) and mirrors completed output to the
    emitter. ``real`` may be ``None`` in frozen ``--noconsole`` builds, in which case there is no
    console to write to but the footer still receives the output.

    A single ``write`` is treated as one log entry, even when it spans several lines (e.g. a
    multi-line warning), so it gets a single timestamp and renders as one multi-line block.
    Separate ``write`` calls (e.g. successive ``print`` calls) stay separate entries.
    """

    def __init__(self, real: TextIO | None, emitter: LogEmitter, *, is_stderr: bool):
        self._real = real
        self._emitter = emitter
        self._is_stderr = is_stderr
        self._partial = ""

    def write(self, text: str) -> int:
        if self._real is not None:
            self._real.write(text)
        self._partial += text
        # Emit everything up to the last newline as one entry (keeping internal newlines), and hold
        # any trailing partial line until it's completed by a later write.
        newline_index = self._partial.rfind("\n")
        if newline_index != -1:
            self._emitter.emit_line(self._partial[:newline_index], is_stderr=self._is_stderr)
            self._partial = self._partial[newline_index + 1 :]
        return len(text)

    def flush(self):
        if self._real is not None:
            self._real.flush()

    def __getattr__(self, name: str) -> object:
        # Delegate everything else (encoding, fileno, isatty, errors, ...) to the real stream so the
        # tee is indistinguishable from it. `_real` is always set in __init__, so no recursion.
        real = self.__dict__["_real"]
        if real is None:
            raise AttributeError(name)
        return getattr(real, name)


def install():
    """
    Wrap ``sys.stdout`` and ``sys.stderr`` so console output is mirrored to `LOG_EMITTER`.

    Call once, as early as possible, so startup output is captured.
    """
    sys.stdout = cast("TextIO", _TeeStream(sys.stdout, LOG_EMITTER, is_stderr=False))
    sys.stderr = cast("TextIO", _TeeStream(sys.stderr, LOG_EMITTER, is_stderr=True))


class ClickableLabel(QtWidgets.QLabel):
    """
    A `QLabel` that emits `clicked` when pressed and right-elides its text to fit its current width.
    Used as the log footer; promoted from `QLabel` in ``design.ui``.
    """

    clicked = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._full_text = ""
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

    def set_elided_text(self, text: str):
        self._full_text = text
        self._update_elision()

    def _update_elision(self):
        metrics = self.fontMetrics()
        # Elide to the content rect (excludes padding) so left and right padding are kept.
        width = self.contentsRect().width()
        super().setText(
            metrics.elidedText(self._full_text, QtCore.Qt.TextElideMode.ElideRight, width)
        )

    @override
    def resizeEvent(self, event: QtGui.QResizeEvent):
        # The label re-elides in its own resizeEvent, when its width is already up to date.
        super().resizeEvent(event)
        self._update_elision()

    @override
    def mousePressEvent(self, ev: QtGui.QMouseEvent):
        self.clicked.emit()
        super().mousePressEvent(ev)
