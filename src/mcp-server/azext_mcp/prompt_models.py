"""Pydantic models for MCP elicit prompts."""

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class TextPrompt(BaseModel):
    """Model for basic text input prompt."""
    value: Annotated[str, Field(
        description="The text value to input"
    )]


class IntegerPrompt(BaseModel):
    """Model for integer input prompt."""
    value: Annotated[int, Field(
        description="The integer value to input"
    )]


class PasswordPrompt(BaseModel):
    """Model for password input prompt."""
    password: Annotated[str, Field(
        description="The password value (will be masked in UI)"
    )]


class YesNoPrompt(BaseModel):
    """Model for yes/no prompt."""
    answer: Annotated[bool, Field(
        description="Yes (true) or No (false)"
    )]


class TrueFalsePrompt(BaseModel):
    """Model for true/false prompt."""
    answer: Annotated[bool, Field(
        description="True or False"
    )]


class ChoicePrompt(BaseModel):
    """Model for choice selection prompt."""
    choice_index: Annotated[int, Field(
        description="The index of the selected choice (1-based)",
        ge=1
    )]
