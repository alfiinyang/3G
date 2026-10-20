"""Skill Discovery, Parsing, and Remote Mounting for 3G-agent.

Requirement:
"it will use a specific skill or group of skills that i will provide in a folder."

This module loads single skill directories or multi-skill directories, parses
YAML frontmatter metadata (name, description), loads subcomponents (stages,
scripts, references), and prepares inline sources for remote Antigravity execution.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("3G-agent.skills")


@dataclass
class SkillFile:
    """Represents an individual file within a skill package."""
    relative_path: str
    absolute_path: Path
    content: str


@dataclass
class Skill:
    """Represents a discovered and parsed Antigravity skill."""
    name: str
    description: str
    root_dir: Path
    skill_md_path: Path
    instruction_content: str
    auxiliary_files: List[SkillFile] = field(default_factory=list)

    def get_signature(self) -> str:
        """Returns a deterministic SHA256 signature of the skill content."""
        hasher = hashlib.sha256()
        hasher.update(self.name.encode("utf-8"))
        hasher.update(self.description.encode("utf-8"))
        hasher.update(self.instruction_content.encode("utf-8"))
        for aux in sorted(self.auxiliary_files, key=lambda x: x.relative_path):
            hasher.update(aux.relative_path.encode("utf-8"))
            hasher.update(aux.content.encode("utf-8"))
        return hasher.hexdigest()[:16]


class SkillLoader:
    """Discovers, parses, and formats skills from a folder for 3G-agent."""

    def __init__(self, skills_dir: Path | str) -> None:
        self.skills_dir = Path(skills_dir)
        self.skills: List[Skill] = []
        self.load_skills()

    def load_skills(self) -> List[Skill]:
        """Scans the specified folder and loads all skills found."""
        self.skills = []
        if not self.skills_dir.exists():
            logger.warning("Skills directory does not exist: %s", self.skills_dir)
            return self.skills

        # Scenario A: The specified folder itself is a skill (contains SKILL.md)
        direct_skill_md = self.skills_dir / "SKILL.md"
        if direct_skill_md.is_file():
            skill = self._parse_skill_directory(self.skills_dir)
            if skill:
                self.skills.append(skill)
                logger.info("Loaded single skill package: '%s'", skill.name)
            return self.skills

        # Scenario B: The specified folder contains one or more subdirectories with SKILL.md
        for child in self.skills_dir.iterdir():
            if child.is_dir():
                sub_skill_md = child / "SKILL.md"
                if sub_skill_md.is_file():
                    skill = self._parse_skill_directory(child)
                    if skill:
                        self.skills.append(skill)
                        logger.info("Loaded skill package: '%s' from %s", skill.name, child.name)

        if not self.skills:
            logger.warning("No valid skills (containing SKILL.md) found in %s", self.skills_dir)

        return self.skills

    def _parse_skill_directory(self, skill_dir: Path) -> Optional[Skill]:
        """Parses a skill directory, extracting metadata and auxiliary stage/script files."""
        skill_md = skill_dir / "SKILL.md"
        try:
            content = skill_md.read_text(encoding="utf-8")
        except Exception as e:
            logger.error("Failed to read %s: %s", skill_md, e)
            return None

        name, description, body = self._extract_frontmatter(content)
        if not name:
            name = skill_dir.name.lower().replace("_", "-")

        auxiliary_files: List[SkillFile] = []
        for file_path in skill_dir.rglob("*"):
            if file_path.is_file() and file_path != skill_md:
                try:
                    rel_path = file_path.relative_to(skill_dir).as_posix()
                    file_text = file_path.read_text(encoding="utf-8", errors="replace")
                    auxiliary_files.append(
                        SkillFile(
                            relative_path=rel_path,
                            absolute_path=file_path,
                            content=file_text,
                        )
                    )
                except Exception as aux_err:
                    logger.debug("Skipping unreadable file %s: %s", file_path, aux_err)

        return Skill(
            name=name,
            description=description,
            root_dir=skill_dir,
            skill_md_path=skill_md,
            instruction_content=body,
            auxiliary_files=auxiliary_files,
        )

    def _extract_frontmatter(self, text: str) -> tuple[str, str, str]:
        """Extracts YAML frontmatter fields (name, description) and body text."""
        name = ""
        description = ""
        body = text

        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
        if match:
            frontmatter_raw, body = match.groups()
            name_match = re.search(r"^name:\s*(.+)$", frontmatter_raw, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip().strip("'\"")

            desc_match = re.search(
                r"^description:\s*(?:>-\s*\n|\s*\n)?((?:[ \t]+[^\n]+\n?)+)",
                frontmatter_raw,
                re.MULTILINE,
            )
            if desc_match:
                lines = [line.strip() for line in desc_match.group(1).splitlines()]
                description = " ".join(lines).strip()
            else:
                desc_simple = re.search(r"^description:\s*(.+)$", frontmatter_raw, re.MULTILINE)
                if desc_simple:
                    description = desc_simple.group(1).strip().strip("'\"")

        return name, description, body

    def build_remote_sources(self) -> List[Dict[str, Any]]:
        """Generates inline sources to mount skills in the remote Antigravity sandbox.
        
        Mounts skills into `.agents/skills/<skill_name>/` in the remote Linux container.
        """
        sources: List[Dict[str, Any]] = []

        for skill in self.skills:
            # Mount the main SKILL.md file
            sources.append({
                "type": "inline",
                "target": f".agents/skills/{skill.name}/SKILL.md",
                "content": skill.instruction_content,
            })

            # Mount auxiliary files (stages, scripts, references)
            for aux in skill.auxiliary_files:
                sources.append({
                    "type": "inline",
                    "target": f".agents/skills/{skill.name}/{aux.relative_path}",
                    "content": aux.content,
                })

        return sources

    def format_skill_catalog(self) -> str:
        """Returns a progressive disclosure catalog listing all skills available to the agent."""
        if not self.skills:
            return "No skills currently configured."

        catalog_lines = ["### Available Skills Catalog:"]
        for skill in self.skills:
            catalog_lines.append(f"- **{skill.name}**: {skill.description}")
            if skill.auxiliary_files:
                catalog_lines.append(f"  Includes {len(skill.auxiliary_files)} reference and stage files.")
        return "\n".join(catalog_lines)

    def get_combined_signature(self) -> str:
        """Computes combined hash signature of all loaded skills."""
        hasher = hashlib.sha256()
        for skill in sorted(self.skills, key=lambda s: s.name):
            hasher.update(skill.get_signature().encode("utf-8"))
        return hasher.hexdigest()[:16]
