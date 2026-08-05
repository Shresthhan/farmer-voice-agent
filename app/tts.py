import os
import tempfile
import edge_tts

VOICE = os.getenv("EDGE_TTS_VOICE", "en-US-JennyNeural")

async def synthesize_speech(text: str) -> bytes:
    communicate = edge_tts.Communicate(text=text, voice=VOICE)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        path = tmp.name

    try:
        await communicate.save(path)
        with open(path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(path):
            os.remove(path)