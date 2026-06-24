"""
Skill Base - Abstract base class, context, result, and registry for the skills system.

Follows the same ABC pattern as LLMClient in services/llm_client.py.
"""
import logging
import importlib
import pkgutil
from typing import List, Optional, Dict, Any, Literal
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass
class SkillContext:
    """Context passed to a skill during execution."""
    query: str
    patient_id: int
    db_session: Optional[Session] = None
    llm_client: Optional[Any] = None  # LLMClient instance
    case_context: Optional[str] = None


@dataclass
class SkillResult:
    """Result returned by a skill after execution."""
    content: str
    references: List[Any] = field(default_factory=list)  # List[ChatReference]
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class Skill(ABC):
    """Abstract base class for all skills.

    Follows the same ABC pattern as LLMClient.
    Subclasses must define: name, description, skill_type, icon, input_schema
    and implement: execute(context) -> SkillResult
    """
    name: str = ""
    description: str = ""
    skill_type: Literal["prompt_injection", "tool_call"] = "prompt_injection"
    icon: str = "experiment"
    input_schema: Dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def execute(self, context: SkillContext) -> SkillResult:
        pass


class SkillRegistry:
    """Registry for skill discovery and lookup."""

    def __init__(self):
        self._skills: Dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        """Register a skill instance."""
        self._skills[skill.name] = skill
        logger.info(f"Registered skill: {skill.name} ({skill.skill_type})")

    def get(self, name: str) -> Optional[Skill]:
        """Look up a skill by name."""
        return self._skills.get(name)

    def list(self) -> List[Skill]:
        """Return all registered skills."""
        return list(self._skills.values())

    def list_by_type(self, skill_type: str) -> List[Skill]:
        """Filter skills by type."""
        return [s for s in self._skills.values() if s.skill_type == skill_type]


def create_skill_registry() -> SkillRegistry:
    """Factory function: create a SkillRegistry with auto-discovered skills.

    Scans backend/services/skills/ directory for Skill subclasses
    and registers them automatically.
    """
    registry = SkillRegistry()

    try:
        import services.skills as skills_package
        for importer, modname, ispkg in pkgutil.iter_modules(skills_package.__path__):
            try:
                module = importlib.import_module(f"services.skills.{modname}")
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, Skill)
                        and attr is not Skill
                        and hasattr(attr, 'name')
                        and attr.name
                    ):
                        try:
                            instance = attr()
                            registry.register(instance)
                        except Exception as e:
                            logger.warning(f"Failed to instantiate skill {attr_name}: {e}")
            except Exception as e:
                logger.warning(f"Failed to import skills module {modname}: {e}")
    except Exception as e:
        logger.warning(f"Skills auto-discovery failed: {e}")

    return registry
