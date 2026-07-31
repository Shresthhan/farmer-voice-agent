from db import init_db
init_db()

from fastapi import FastAPI, UploadFile
from db import get_session, save_session
from llm_agent import chat_turn
from stt import transcribe_audio
from tts import synthesize_speech

app = FastAPI()

# --- Health check endpoint - confirms the app is running ---
@app.get("/")
def health():
    return {"status": "running"}

# --- Main conversation endpoint ---
# Farmer sends: session_id + audio file (their spoken answer)
# App returns: spoken reply (audio) + updated data
@app.post("/talk/{session_id}")
async def talk(session_id: str, audio: UploadFile):
    # 1. Load existing conversation state for this farmer (or empty if new)
    slots, history = get_session(session_id)

    # 2. Convert farmer's speech to text
    audio_bytes = await audio.read()
    user_text = transcribe_audio(audio_bytes)

    # 3. Send to LLM: it replies naturally AND extracts new data via function calling
    response = chat_turn(history, user_text, slots)
    reply_text = response["message"]["content"]

    # 4. If the model called save_farmer_info, update our slots dict
    if response["message"].get("tool_calls"):
        for call in response["message"]["tool_calls"]:
            args = call["function"]["arguments"]
            slots.update({k: v for k, v in args.items() if v is not None})

    # 5. Update conversation history
    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": reply_text})

    # 6. Save updated state to DB (this is what makes pause/resume work)
    save_session(session_id, slots, history)

    # 7. Convert reply text back to speech
    audio_reply = synthesize_speech(reply_text)

    return {
        "reply_text": reply_text,      # what the model said
        "audio_reply": audio_reply,     # spoken version (bytes/base64)
        "collected_data": slots         # current state of extracted farmer info
    }

# --- Dashboard endpoint - lets your team see collected data live ---
@app.get("/sessions/{session_id}")
def view_session(session_id: str):
    slots, history = get_session(session_id)
    return {"collected_data": slots, "conversation": history}