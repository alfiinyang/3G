"""Real-Time Terminal Status Reporter for 3G-agent Turn Interactions.

Displays dynamic live agent statuses in the terminal while the user is waiting
for the agent to respond during each turn of interaction:
- Thinking: agent reasoning, analyzing instructions, formulating strategy.
- Skill Use: loading, mounting, or executing skill stages (e.g. pedagogy-engineering).
- Tool Call: executing remote sandbox tools, code execution, search, file operations.
- Tool Result: completion of tool calls.
- Environment: provisioning or holding persistent remote container session.
- Responding: generating and streaming response tokens.
"""

from __future__ import annotations

import sys
import threading
import time
from typing import Callable, Optional


class TurnStatusReporter:
    """Provides dynamic, real-time terminal status feedback during an agent turn."""

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

        self._current_phase = "Initializing"
        self._current_detail = ""
        self._start_time = time.time()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._last_logged_phase: Optional[str] = None

    def start(self, initial_phase: str = "Thinking", initial_detail: str = "Analyzing prompt...") -> "TurnStatusReporter":
        """Starts the background status animator."""
        if not self.enabled:
            return self

        self._current_phase = initial_phase
        self._current_detail = initial_detail
        self._start_time = time.time()
        self._running = True

        if self.callback:
            try:
                self.callback(self._current_phase, self._current_detail)
            except Exception:
                pass

        if not self.is_tty:
            # For non-interactive logs, print immediate initial status
            self._print_static_status(self._current_phase, self._current_detail)
            self._last_logged_phase = self._current_phase

        self._thread = threading.Thread(target=self._animate, daemon=True, name="3g-status-reporter")
        self._thread.start()
        return self

    def update_status(self, phase: str, detail: str = "") -> None:
        """Updates the active status phase and detail."""
        if not self.enabled:
            return

        with self._lock:
            old_phase = self._current_phase
            self._current_phase = phase
            self._current_detail = detail

        if self.callback:
            try:
                self.callback(phase, detail)
            except Exception:
                pass

        if not self.is_tty:
            # Print status change on non-TTY streams
            if phase != self._last_logged_phase or detail:
                self._print_static_status(phase, detail)
                self._last_logged_phase = phase
        else:
            # On TTY, if major phase changed, print a permanent checkpoint line
            if old_phase != phase:
                elapsed = time.time() - self._start_time
                icon = self._get_phase_icon(old_phase)
                try:
                    self.stream.write(f"\r\033[K  {icon} [Agent Status: {old_phase}] Active ({elapsed:.1f}s)\n")
                    self.stream.flush()
                except Exception:
                    pass

    def thinking(self, detail: str = "Reasoning through prompt...") -> None:
        """Sets status to Thinking."""
        self.update_status("Thinking", detail)

    def skill_use(self, skill_name: str, stage: str = "") -> None:
        """Sets status to Skill Use."""
        detail = f"Applying skill '{skill_name}'"
        if stage:
            detail += f" ({stage})"
        self.update_status("Skill Use", detail)

    def tool_call(self, tool_name: str, args_summary: str = "") -> None:
        """Sets status to Tool Call."""
        detail = f"Executing '{tool_name}'"
        if args_summary:
            detail += f" ({args_summary})"
        self.update_status("Tool Call", detail)

    def tool_result(self, tool_name: str, result_summary: str = "") -> None:
        """Sets status to Tool Result."""
        detail = f"Completed '{tool_name}'"
        if result_summary:
            detail += f" -> {result_summary}"
        self.update_status("Tool Result", detail)

    def environment(self, detail: str) -> None:
        """Sets status to Environment."""
        self.update_status("Environment", detail)

    def responding(self, detail: str = "Generating response tokens...") -> None:
        """Sets status to Responding."""
        self.update_status("Responding", detail)

    def complete(self, detail: str = "Done") -> None:
        """Stops the reporter with completion status."""
        self.stop(final_message=detail)

    def stop(self, final_message: Optional[str] = None) -> None:
        """Stops the background animator and cleans up the terminal line."""
        if not self._running:
            return

        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        elapsed = time.time() - self._start_time
        if self.is_tty:
            try:
                msg = final_message or "Complete"
                self.stream.write(f"\r\033[K  ✔ [Agent Status: Complete] {msg} ({elapsed:.1f}s)\n")
                self.stream.flush()
            except Exception:
                pass
        elif final_message:
            self._print_static_status("Complete", f"{final_message} ({elapsed:.1f}s)")

    def _print_static_status(self, phase: str, detail: str) -> None:
        icon = self._get_phase_icon(phase)
        text = f"{icon} [Agent Status: {phase}]"
        if detail:
            text += f" {detail}"
        try:
            self.stream.write(f"{text}\n")
            self.stream.flush()
        except Exception:
            pass

    def _get_phase_icon(self, phase: str) -> str:
        mapping = {
            "Thinking": "🤔",
            "Skill Use": "⚡",
            "Tool Call": "🛠️",
            "Tool Result": "✔",
            "Environment": "🌐",
            "Responding": "✍️",
            "Complete": "✔",
            "Error": "❌",
        }
        return mapping.get(phase, "⚙️")

    def _animate(self) -> None:
        frame_idx = 0
        while self._running:
            if self.is_tty:
                with self._lock:
                    phase = self._current_phase
                    detail = self._current_detail

                elapsed = time.time() - self._start_time
                frame = self.SPINNER_FRAMES[frame_idx % len(self.SPINNER_FRAMES)]
                icon = self._get_phase_icon(phase)

                line = f"\r\033[K{frame} {icon} [Agent Status: {phase}] {detail} ({elapsed:.1f}s)"
                try:
                    self.stream.write(line)
                    self.stream.flush()
                except Exception:
                    pass

                frame_idx += 1
            time.sleep(0.08)

    def __enter__(self) -> "TurnStatusReporter":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.stop(final_message="Interrupted or Error encountered")
        else:
            self.stop()
