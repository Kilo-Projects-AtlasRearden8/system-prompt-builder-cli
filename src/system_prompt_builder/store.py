"""JSON file storage for prompt templates."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

from .models import PromptTemplate


class TemplateStore:
    """Persists PromptTemplate objects as JSON files in a data directory."""

    def __init__(self, data_dir: str | os.PathLike[str]) -> None:
        self.data_dir = Path(data_dir)
        self.templates_dir = self.data_dir / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, name: str) -> Path:
        return self.templates_dir / f"{self._safe_name(name)}.json"

    @staticmethod
    def _safe_name(name: str) -> str:
        safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name)
        return safe or "untitled"

    def list(self) -> list[str]:
        return sorted(
            path.stem for path in self.templates_dir.glob("*.json") if path.is_file()
        )

    def get(self, name: str) -> PromptTemplate | None:
        path = self.path_for(name)
        if not path.exists():
            return None
        return PromptTemplate.load(str(path))

    def save(self, template: PromptTemplate) -> Path:
        path = self.path_for(template.name)
        template.save(str(path))
        return path

    def delete(self, name: str) -> bool:
        path = self.path_for(name)
        if not path.exists():
            return False
        path.unlink()
        return True

    def default_path(self) -> Path:
        return self.data_dir / "config.json"

    def load_config(self) -> Dict[str, str]:
        path = self.default_path()
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}

    def save_config(self, config: Dict[str, str]) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.default_path(), "w", encoding="utf-8") as handle:
            json.dump(config, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
