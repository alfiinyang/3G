"""LangChain tools for basic file-system operations.

Tools:
    - create_file:      create a new Markdown (.md) file
    - read_file:        read the contents of a file
    - edit_file:        replace text in an existing file
    - list_directory:   list the entries of a directory
    - search_directory: search a directory by filename pattern and/or content
"""

from __future__ import annotations

import fnmatch
from pathlib import Path
from ast import Dict
from typing import List

from langchain.tools import tool
from pydantic import BaseModel, Field

MAX_READ_CHARS = 100_000
MAX_SEARCH_RESULTS = 200

class SubAgentSummary(BaseModel):
    """
    Pydantic schema representing the structured summary returned by specialized sub-agents.
    
    This schema ensures that communication between coordinates is strictly structured,
    omitting conversational noise or raw file outputs in favor of programmatic tracking.
    
    Attributes:
        filepaths (List[str]): Paths to any code, specifications, or artifacts updated.
        bullet_points (List[str]): High-level overview of critical decisions or progress.
        status (str): Current execution state indicating success, in-progress, or failure.
        commentary (str): Brief contextual notes or next steps strictly constrained in length.
    """
    filepaths: List[str] = Field(description="List of exact filepaths created or modified.")
    bullet_points: List[str] = Field(description="Concise bullet points highlighting key elements of actions and content.")
    status: str = Field(description="Current status of the action (e.g., 'COMPLETE', 'IN_PROGRESS', 'FAILED').")
    commentary: str = Field(description="Additional short summary or next steps (strictly under 50 words).")


def _resolve(path: str) -> Path:
    return Path(path).expanduser().resolve()


@tool(
    "create_file",
    description=(
        "Create a new Markdown (.md) file at `file_path` containing `content`. "
        "Only .md files are allowed. Missing parent directories are created. "
        "Fails if the file exists unless `overwrite` is True."
    ),
)
def create_file(file_path: str, content: str = "", overwrite: bool = False) -> str:
    """Create a Markdown (.md) file with the given content.

    Args:
        file_path: Path of the file to create. Must end with '.md'.
        content: Text content to write into the file.
        overwrite: If True, overwrite the file if it already exists.
    """
    path = _resolve(file_path)
    if path.suffix.lower() != ".md":
        return f"Error: only .md files can be created (got '{path.name}')."
    if path.exists() and not overwrite:
        return f"Error: '{path}' already exists. Set overwrite=True to replace it."
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        return f"Error creating '{path}': {exc}"
    return f"Created '{path}' ({len(content)} characters)."


@tool(
    "read_file",
    description=(
        "Read a text file at `file_path` and return its contents. "
        "Optionally return only lines `start_line` to `end_line` (1-based, inclusive)."
    ),
)
def read_file(file_path: str, start_line: int = 1, end_line: int | None = None) -> str:
    """Read a text file and return its contents, optionally a line range.

    Args:
        file_path: Path of the file to read.
        start_line: First line to return (1-based, inclusive).
        end_line: Last line to return (inclusive). Defaults to end of file.
    """
    path = _resolve(file_path)
    if not path.is_file():
        return f"Error: '{path}' does not exist or is not a file."
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return f"Error reading '{path}': {exc}"

    start = max(start_line, 1) - 1
    end = len(lines) if end_line is None else min(end_line, len(lines))
    text = "\n".join(lines[start:end])
    if len(text) > MAX_READ_CHARS:
        text = text[:MAX_READ_CHARS] + "\n...[truncated]"
    return text


@tool(
    "edit_file",
    description=(
        "Edit an existing text file at `file_path` by replacing the exact text "
        "`old_text` with `new_text` (empty string deletes it). `old_text` must occur "
        "exactly once unless `replace_all` is True."
    ),
)
def edit_file(file_path: str, old_text: str, new_text: str, replace_all: bool = False) -> str:
    """Edit a text file by replacing `old_text` with `new_text`.

    Args:
        file_path: Path of the file to edit.
        old_text: Exact text to find in the file.
        new_text: Text to replace it with (use an empty string to delete).
        replace_all: If True, replace every occurrence; otherwise `old_text`
            must occur exactly once.
    """
    path = _resolve(file_path)
    if not path.is_file():
        return f"Error: '{path}' does not exist or is not a file."
    if not old_text:
        return "Error: old_text must not be empty."
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        return f"Error reading '{path}': {exc}"

    count = content.count(old_text)
    if count == 0:
        return f"Error: old_text not found in '{path}'."
    if count > 1 and not replace_all:
        return (
            f"Error: old_text occurs {count} times in '{path}'. "
            "Provide more context or set replace_all=True."
        )

    updated = content.replace(old_text, new_text) if replace_all else content.replace(old_text, new_text, 1)
    try:
        path.write_text(updated, encoding="utf-8")
    except OSError as exc:
        return f"Error writing '{path}': {exc}"
    return f"Edited '{path}': replaced {count if replace_all else 1} occurrence(s)."


@tool(
    "list_directory",
    description=(
        "List the files (with sizes) and sub-directories in `dir_path` "
        "(defaults to the current directory). Hidden entries are excluded "
        "unless `show_hidden` is True."
    ),
)
def list_directory(dir_path: str = ".", show_hidden: bool = False) -> str:
    """List the files and sub-directories in a directory.

    Args:
        dir_path: Directory to list. Defaults to the current directory.
        show_hidden: If True, include entries starting with '.'.
    """
    path = _resolve(dir_path)
    if not path.is_dir():
        return f"Error: '{path}' does not exist or is not a directory."
    try:
        entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except OSError as exc:
        return f"Error listing '{path}': {exc}"

    lines = []
    for entry in entries:
        if not show_hidden and entry.name.startswith("."):
            continue
        if entry.is_dir():
            lines.append(f"[DIR]  {entry.name}/")
        else:
            try:
                size = entry.stat().st_size
            except OSError:
                size = -1
            lines.append(f"[FILE] {entry.name} ({size} bytes)")
    return f"Contents of '{path}':\n" + ("\n".join(lines) if lines else "(empty)")


@tool(
    "search_directory",
    description=(
        "Recursively search `dir_path` for files whose names match the glob "
        "`name_pattern` (e.g. '*.md'). If `content_query` is given, return the "
        "matching lines as 'path:line: text'. Matching is case-insensitive unless "
        "`case_sensitive` is True."
    ),
)
def search_directory(
    dir_path: str = ".",
    name_pattern: str = "*",
    content_query: str | None = None,
    case_sensitive: bool = False,
) -> str:
    """Recursively search a directory for files by name pattern and/or content.

    Args:
        dir_path: Root directory to search.
        name_pattern: Glob pattern for file names, e.g. '*.md' or 'report*'.
        content_query: Optional text to look for inside files. When given,
            matching lines are returned with their line numbers.
        case_sensitive: Whether name and content matching is case-sensitive.
    """
    root = _resolve(dir_path)
    if not root.is_dir():
        return f"Error: '{root}' does not exist or is not a directory."

    query = content_query if (content_query is None or case_sensitive) else content_query.lower()
    pattern = name_pattern if case_sensitive else name_pattern.lower()
    results: list[str] = []

    for file in root.rglob("*"):
        if len(results) >= MAX_SEARCH_RESULTS:
            results.append(f"...[stopped after {MAX_SEARCH_RESULTS} results]")
            break
        if not file.is_file():
            continue
        name = file.name if case_sensitive else file.name.lower()
        if not fnmatch.fnmatchcase(name, pattern):
            continue
        rel = file.relative_to(root)

        if query is None:
            results.append(str(rel))
            continue

        try:
            with file.open("r", encoding="utf-8", errors="ignore") as fh:
                for lineno, line in enumerate(fh, start=1):
                    haystack = line if case_sensitive else line.lower()
                    if query in haystack:
                        results.append(f"{rel}:{lineno}: {line.strip()}")
                        if len(results) >= MAX_SEARCH_RESULTS:
                            break
        except OSError:
            continue

    if not results:
        return f"No matches found in '{root}'."
    return f"Matches in '{root}':\n" + "\n".join(results)


TOOLS = [create_file, read_file, edit_file, list_directory, search_directory]

def format_input(query: str) -> dict:
  """
  Prepares and formats a raw user input query into the standard message-based 
  state dictionary schema required by the LangGraph orchestrator agent.

  Args:
      query (str): The raw text message or instruction provided by the user.

  Returns:
      dict: A state dictionary containing a 'messages' list with the query wrapped 
            inside a standardized LangChain user message tuple.
  """
  return {"messages": [("user", query)]}
