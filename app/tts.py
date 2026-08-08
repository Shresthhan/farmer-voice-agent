from __future__ import annotations

import os
import tempfile

import edge_tts

# Nepali neural voices available in edge-tts.
# Female: ne-NP-HemkalaNeural
# Male:   ne-NP-SagarNeural
VOICE = os.getenv("EDGE_TTS_VOICE", "ne-NP-HemkalaNeural")


async def synthesize_speech(text: str) -> bytes:
    """
    Convert Nepali text to speech and return raw MP3 bytes.
    """

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
    )

    with tempfile.NamedTemporaryFile(
        suffix=".mp3",
        delete=False,
    ) as tmp:
        path = tmp.name

    try:
        await communicate.save(path)

        with open(path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(path):
            os.remove(path)