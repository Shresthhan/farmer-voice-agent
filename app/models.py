"""Data models used by the agent."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Message:
    role: str
    content: str
