"""Text-to-speech helpers."""

from __future__ import annotations

from pathlib import Path


def synthesize_speech(text: str, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.write_text(text, encoding="utf-8")
    return path
