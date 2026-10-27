"""Prompt template model: variables, mock data, and rendering."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict


VAR_PATTERN = re.compile(r"\{(\w+)\}")


@dataclass
class PromptTemplate:
    """A system prompt template with named variables and mock data defaults."""

    name: str
    template: str
    variables: Dict[str, str] = field(default_factory=dict)
    mock_data: Dict[str, str] = field(default_factory=dict)
    description: str = ""

    def template_variables(self) -> list[str]:
        """Return variable names referenced in the template, in first-seen order."""
        seen: list[str] = []
        for match in VAR_PATTERN.finditer(self.template):
            name = match.group(1)
            if name not in seen:
                seen.append(name)
        return seen

    def missing_variables(self, provided: Dict[str, str]) -> list[str]:
        """Return template variables not covered by provided values or mock data."""
        merged = {**self.mock_data, **provided}
        return [name for name in self.template_variables() if name not in merged]

    def render(self, variables: Dict[str, str] | None = None) -> str:
        """Render the template with mock data defaults overridden by `variables`."""
        merged = {**self.mock_data, **(variables or {})}
        missing = [name for name in self.template_variables() if name not in merged]
        if missing:
            raise ValueError(
                f"Missing values for variables: {', '.join(missing)}"
            )
        return self.template.format(**merged)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptTemplate":
        return cls(
            name=data["name"],
            template=data["template"],
            variables=data.get("variables", {}),
            mock_data=data.get("mock_data", {}),
            description=data.get("description", ""),
        )

    @classmethod
    def load(cls, path: str) -> "PromptTemplate":
        with open(path, "r", encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, indent=2, ensure_ascii=False)
            handle.write("\n")
