from app.main import create_app
from app.llm_agent import VoiceAgent


def test_create_app() -> None:
    app = create_app()
    assert app["name"] == "farmer-voice-agent"
    assert app["status"] == "ok"


def test_voice_agent_responds() -> None:
    agent = VoiceAgent()
    assert agent.respond("hello") == "farmer-voice-agent received: hello"
