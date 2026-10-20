"""Single-Line Dynamic Status Reporter for 3G-agent Turn Interactions.

Streamlines terminal feedback while the user is waiting for the agent to respond:
- Updates strictly on ONE line using carriage return (\r).
- No line breaks (\n) are printed between phases or status updates.
- Minimal, clean text (e.g. "Thinking...", "Running tool: code_execution...").
- Clears the status line completely when done so ONLY the agent's response is displayed.
"""

from __future__ import annotations

import sys
import threading
import time
from typing import Callable, Optional


class TurnStatusReporter:
    """Provides a single-line streaming status indicator during an agent turn."""

    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(
        self,
        enabled: bool = True,
        callback: Optional[Callable[[str, str], None]] = None,
        stream=None,
    ) -> None:
        self.enabled = enabled
        self.callback = callback
        self.stream = stream or sys.stdout
        self.is_tty = hasattr(self.stream, "isatty") and self.stream.isatty()

        self._current_phase = "Thinking"
        self._current_text = "Thinking..."
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._last_line_len = 0

    def start(self, initial_phase: str = "Thinking", initial_detail: str = "") -> "TurnStatusReporter":
        """Starts the single-line streaming status indicator."""
        if not self.enabled:
            return self

        with self._lock:
            self._current_phase = initial_phase
            self._current_text = self._format_status(initial_phase, initial_detail)
            self._running = True

        if self.callback:
            try:
                self.callback(initial_phase, initial_detail)
            except Exception:
                pass

        if self.is_tty:
            self._thread = threading.Thread(target=self._animate, daemon=True, name="3g-status-reporter")
            self._thread.start()

        return self

    def update_status(self, phase: str, detail: str = "") -> None:
        """Updates the status text in-place on the single active line."""
        if not self.enabled:
            return

        with self._lock:
            self._current_phase = phase
            self._current_text = self._format_status(phase, detail)

        if self.callback:
            try:
                self.callback(phase, detail)
            except Exception:
                pass

    def _format_status(self, phase: str, detail: str = "") -> str:
        """Formats a concise, minimal status label without extraneous noise."""
        clean_detail = detail.strip() if detail else ""
        if len(clean_detail) > 40:
            clean_detail = clean_detail[:37] + "..."

        if phase == "Thinking":
            if clean_detail and clean_detail not in ("Reasoning through prompt...", "Analyzing prompt..."):
                return f"Thinking ({clean_detail})..."
            return "Thinking..."
        elif phase == "Skill Use":
            return f"Using skill: {clean_detail}..." if clean_detail else "Using skill..."
        elif phase == "Tool Call":
            return f"Running tool: {clean_detail}..." if clean_detail else "Running tool..."
        elif phase == "Tool Result":
            return f"Tool completed: {clean_detail}..." if clean_detail else "Tool completed..."
        elif phase == "Environment":
            return "Preparing sandbox environment..."
        elif phase == "Responding":
            return "Generating response..."
        elif phase == "Complete":
            return ""
        return f"{phase}..." if not clean_detail else f"{phase}: {clean_detail}..."

    def thinking(self, detail: str = "") -> None:
        self.update_status("Thinking", detail)

    def skill_use(self, skill_name: str, stage: str = "") -> None:
        detail = skill_name
        if stage:
            detail += f" ({stage})"
        self.update_status("Skill Use", detail)

    def tool_call(self, tool_name: str, args_summary: str = "") -> None:
        detail = tool_name
        if args_summary:
            detail += f" ({args_summary})"
        self.update_status("Tool Call", detail)

    def tool_result(self, tool_name: str, result_summary: str = "") -> None:
        detail = tool_name
        if result_summary:
            detail += f": {result_summary}"
        self.update_status("Tool Result", detail)

    def environment(self, detail: str = "") -> None:
        self.update_status("Environment", detail)

    def responding(self, detail: str = "") -> None:
        self.update_status("Responding", detail)

    def complete(self, detail: str = "") -> None:
        self.stop(final_message=detail)

    def stop(self, final_message: Optional[str] = None) -> None:
        """Stops the status reporter and cleanly erases the line so only agent output is shown."""
        if not self._running:
            return

        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.4)

        # Clear the single status line completely so the screen is completely clean
        if self.is_tty and self._last_line_len > 0:
            try:
                self.stream.write("\r" + (" " * self._last_line_len) + "\r")
                self.stream.flush()
            except Exception:
                pass
            self._last_line_len = 0

    def _animate(self) -> None:
        frame_idx = 0
        while self._running:
            with self._lock:
                text = self._current_text

            if text:
                frame = self.SPINNER_FRAMES[frame_idx % len(self.SPINNER_FRAMES)]
                line = f"{frame} {text}"
                padding = max(0, self._last_line_len - len(line))
                try:
                    self.stream.write(f"\r{line}{' ' * padding}")
                    self.stream.flush()
                    self._last_line_len = len(line)
                except Exception:
                    pass
                frame_idx += 1
            time.sleep(0.08)

    def __enter__(self) -> "TurnStatusReporter":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()
