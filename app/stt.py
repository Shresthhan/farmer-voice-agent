"""Speech-to-text helpers."""

from __future__ import annotations

from pathlib import Path


def transcribe_audio(audio_path: str | Path) -> str:
    path = Path(audio_path)
    return f"transcription placeholder for {path.name}"
