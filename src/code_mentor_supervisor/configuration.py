import os
from typing import Any, Optional, Dict, Type, TypedDict

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

# TypedDict representation of Configuration for LangGraph compatibility
class ConfigSchema(TypedDict):
    """Schema defining configurable parameters for the agent."""
    model_provider: str = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = 0.0

class Configuration(BaseModel):
    """The configurable fields for the agent."""

    model_provider: str = Field(
        default="openai",
        title="Model Provider",
        description="Provider of the LLM (e.g., anthropic, openai)",
    )
    
    model: str = Field(
        default="gpt-4o-mini",
        title="Model Name",
        description="Name of the LLM to use",
    )
    
    temperature: float = Field(
        default=0,
        title="Temperature",
        description="Temperature setting for the LLM",
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
