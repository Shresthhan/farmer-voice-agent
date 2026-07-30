"""Application entry point."""

from __future__ import annotations

from app.llm_agent import VoiceAgent


def create_app() -> dict[str, str]:
    """Return a small application metadata payload."""
    agent = VoiceAgent()
    return {
        "name": "farmer-voice-agent",
        "status": "ok",
        "agent": agent.name,
    }


def main() -> None:
    print(create_app())


if __name__ == "__main__":
    main()
