from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_QUESTION_CHARS = 500
MAX_HISTORY_MESSAGES = 6


class HistoryMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class AskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(max_length=MAX_QUESTION_CHARS)
    history: list[HistoryMessage] = Field(default_factory=list, max_length=MAX_HISTORY_MESSAGES)

    @field_validator("question")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("question vide")
        return value
