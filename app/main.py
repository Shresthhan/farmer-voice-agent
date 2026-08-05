from fastapi import FastAPI, File, UploadFile
from db import init_db, get_session, save_session
from llm_agent import QUESTIONS, chat_turn, generate_end_message
from stt import transcribe_audio
from tts import synthesize_speech
from models import TextMessage
import base64
import json

app = FastAPI()
init_db()


def clean_value(v):
    if v is None:
        return False
    if isinstance(v, str) and v.strip() == "":
        return False
    if isinstance(v, str) and v.strip().lower() in {"none", "null", "[]", "none mentioned"}:
        return False
    return True


def merge_slots(slots: dict, args: dict):
    for k, v in args.items():
        if not clean_value(v):
            continue

        if k in slots and k not in {"abroad_countries", "other_info"}:
            continue

        if k == "abroad_countries":
            if isinstance(v, str):
                try:
                    v = json.loads(v)
                except:
                    v = [v]
            if not isinstance(v, list):
                v = [v]
            current = slots.get("abroad_countries", [])
            merged = current + v
            slots["abroad_countries"] = list(dict.fromkeys(merged))

        elif k == "other_info":
            slots.setdefault("other_info", []).append(v)

        else:
            slots[k] = v

    return slots


def get_next_question(slots: dict, current_index: int):
    for i in range(current_index, len(QUESTIONS)):
        item = QUESTIONS[i]
        if item["field"] not in slots:
            return item, i
    return None, len(QUESTIONS)


def process_turn(session_id: str, user_text: str):
    slots, history, current_topic_index = get_session(session_id)
    current_item = QUESTIONS[current_topic_index] if current_topic_index < len(QUESTIONS) else None

    expected_field = current_item["field"] if current_item else None

    response = chat_turn(
        user_text=user_text,
        expected_field=expected_field,
        current_question=current_item["ask"] if current_item else "",
    )

    tool_calls = response["tool_calls"]
    if tool_calls:
        for call in tool_calls:
            arguments = call["function"]["arguments"]
            if expected_field and expected_field in arguments:
                slots = merge_slots(slots, {expected_field: arguments[expected_field]})

    asked_item, current_topic_index = get_next_question(slots, current_topic_index)
    upcoming_item = QUESTIONS[current_topic_index + 1] if current_topic_index + 1 < len(QUESTIONS) else None

    reply_text = response["reply_text"]
    if asked_item:
        reply_text = f"{reply_text} {asked_item['ask']}"
    else:
        reply_text = f"{reply_text} {generate_end_message()}"

    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": reply_text})

    save_session(session_id, slots, history, current_topic_index)

    return {
        "reply_text": reply_text,
        "collected_data": slots,
        "current_topic_index": current_topic_index,
        "next_question": upcoming_item["ask"] if upcoming_item else None,
        "current_question": asked_item["ask"] if asked_item else None,
    }


@app.get("/")
def health():
    return {"status": "running"}


@app.get("/start/{session_id}")
def start_conversation(session_id: str):
    slots, history, current_topic_index = get_session(session_id)
    if history:
        next_item, _ = get_next_question(slots, current_topic_index)
        if next_item:
            return {"reply_text": f"Namaste! Let’s continue. {next_item['ask']}"}
        return {"reply_text": "Namaste! We have already completed the questions."}

    first_question = QUESTIONS[0]["ask"] if QUESTIONS else "What is your name?"
    return {"reply_text": f"Namaste! I’ll ask you a few quick questions about your farm. {first_question}"}


@app.post("/talk/{session_id}")
async def talk(session_id: str, audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    user_text = transcribe_audio(audio_bytes)
    result = process_turn(session_id, user_text)
    reply_text = result["reply_text"]

    audio_reply = await synthesize_speech(reply_text)
    audio_reply_b64 = base64.b64encode(audio_reply).decode("utf-8")

    return {
        "reply_text": reply_text,
        "audio_reply_b64": audio_reply_b64,
        "user_text": user_text,
        **result,
    }


@app.post("/talk_text/{session_id}")
def talk_text(session_id: str, payload: TextMessage):
    return process_turn(session_id, payload.text)


@app.get("/sessions/{session_id}")
def view_session(session_id: str):
    slots, history, current_topic_index = get_session(session_id)
    next_item, _ = get_next_question(slots, current_topic_index)
    return {
        "collected_data": slots,
        "conversation": history,
        "current_topic_index": current_topic_index,
        "next_question": next_item["ask"] if next_item else None
    }

@app.post("/talk_voice_text/{session_id}")
async def talk_voice_text(session_id: str, audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    user_text = transcribe_audio(audio_bytes)
    result = process_turn(session_id, user_text)

    return {
        "reply_text": result["reply_text"],
        "user_text": user_text,
        **result,
    }