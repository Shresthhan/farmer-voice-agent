"""Language model agent helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class VoiceAgent:
    """Lightweight placeholder for the conversational agent."""

    name: str = "farmer-voice-agent"

    def respond(self, prompt: str) -> str:
        return f"{self.name} received: {prompt}"
