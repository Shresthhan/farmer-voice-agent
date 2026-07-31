from faster_whisper import WhisperModel
import tempfile

# "base" model is a good speed/accuracy balance for a demo
# loads once when the app starts, not on every request
model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_audio(audio_bytes: bytes) -> str:
    # faster-whisper needs a file path, so we write the bytes to a temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        segments, _ = model.transcribe(tmp.name)
        text = " ".join(segment.text for segment in segments)
    return text.strip()