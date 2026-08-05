"""Data models used by the agent."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(slots=True)
class Message:
    role: str
    content: str


class TextMessage(BaseModel):
    text: str
