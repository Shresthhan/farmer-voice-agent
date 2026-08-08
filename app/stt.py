from __future__ import annotations

import tempfile

from faster_whisper import WhisperModel

# "medium" gives noticeably better Nepali accuracy than
# "small"/"base", at the cost of slower CPU inference.
model = WhisperModel(
    "medium",
    device="cpu",
    compute_type="int8",
)

NEPALI_PRIMER = "नमस्ते, मेरो नाम राम हो। म किसान हुँ।"


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribe recorded audio to Nepali text.
    faster-whisper needs a file path, so we write the bytes
    to a temporary file first.
    """

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=True,
    ) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()

        segments, info = model.transcribe(
            tmp.name,
            language="ne",
            task="transcribe",
            initial_prompt=NEPALI_PRIMER,
            vad_filter=True,
            vad_parameters={
                "min_silence_duration_ms": 300,
            },
            beam_size=5,
            best_of=5,
            temperature=0.0,
            condition_on_previous_text=False,
            no_speech_threshold=0.6,
        )

        text = " ".join(segment.text for segment in segments)

    return text.strip()