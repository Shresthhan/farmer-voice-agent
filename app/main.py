from __future__ import annotations

import base64
from typing import Any

from fastapi import FastAPI, File, UploadFile

from db import get_session, init_db, save_session
from llm_agent import (
    QUESTIONS,
    build_clarification_reply,
    build_natural_reply,
    extract_value,
    generate_end_message,
)
from models import TextMessage
from stt import transcribe_audio
from tts import synthesize_speech


app = FastAPI()

init_db()


def is_zero_like(value: Any) -> bool:
    if isinstance(value, bool):
        return False

    if isinstance(value, (int, float)):
        return value == 0

    if isinstance(value, str):
        return value.strip().lower() in {
            "0",
            "०",
            "zero",
            "शून्य",
        }

    return False


def get_next_question(
    slots: dict[str, Any],
    start_index: int,
) -> tuple[dict[str, str] | None, int]:
    """
    Return the next unanswered question.

    abroad_countries is skipped when children_abroad is zero.
    """

    for index in range(
        max(0, start_index),
        len(QUESTIONS),
    ):
        item = QUESTIONS[index]
        field = item["field"]

        if (
            field == "abroad_countries"
            and is_zero_like(
                slots.get("children_abroad")
            )
        ):
            continue

        if field not in slots:
            return item, index

    return None, len(QUESTIONS)


def process_turn(
    session_id: str,
    user_text: str,
) -> dict[str, Any]:
    slots, history, current_index = get_session(
        session_id
    )

    current_item, _ = get_next_question(
        slots,
        current_index,
    )

    if current_item is None:
        return {
            "reply_text": generate_end_message(),
            "collected_data": slots,
            "current_topic_index": len(QUESTIONS),
            "current_question": None,
            "next_question": None,
        }

    expected_field = current_item["field"]

    value = extract_value(
        user_text=user_text,
        expected_field=expected_field,
    )

    field_was_saved = False

    if value is not None:
        slots[expected_field] = value
        field_was_saved = True

        if expected_field == "children_abroad" and is_zero_like(value):
            slots["children_abroad"] = "0"
            slots["abroad_countries"] = []

    next_item, next_index = get_next_question(
        slots,
        current_index,
    )

    if not field_was_saved:
        reply_text = build_clarification_reply(
            current_question=current_item["ask"],
        )
    elif next_item is None:
        reply_text = generate_end_message()
    else:
        reply_text = build_natural_reply(
            user_text=user_text,
            current_question=current_item["ask"],
            next_question=next_item["ask"],
        )

    history = list(history or [])

    history.append(
        {
            "role": "user",
            "content": user_text,
        }
    )

    history.append(
        {
            "role": "assistant",
            "content": reply_text,
        }
    )

    save_session(
        session_id=session_id,
        slots=slots,
        history=history,
        current_topic_index=next_index,
    )

    following_item, _ = get_next_question(
        slots,
        next_index,
    )

    return {
        "reply_text": reply_text,
        "collected_data": slots,
        "current_topic_index": next_index,
        "current_question": (
            next_item["ask"]
            if next_item
            else None
        ),
        "next_question": (
            following_item["ask"]
            if following_item
            else None
        ),
    }


@app.get("/")
def health() -> dict[str, str]:
    return {
        "status": "running",
    }


@app.get("/start/{session_id}")
def start_conversation(
    session_id: str,
) -> dict[str, Any]:
    slots, history, current_index = get_session(
        session_id
    )

    item, index = get_next_question(
        slots,
        current_index,
    )

    if item is None:
        return {
            "reply_text": generate_end_message(),
            "current_topic_index": index,
            "next_question": None,
        }

    if history:
        greeting = "नमस्ते, अघि बढौँ।"
    else:
        greeting = (
            "नमस्ते! तपाईंको खेतबारीबारे "
            "थोरै कुरा गरौँ।"
        )

    return {
        "reply_text": f"{greeting} {item['ask']}",
        "current_topic_index": index,
        "next_question": item["ask"],
        "collected_data": slots,
    }


@app.post("/talk_text/{session_id}")
def talk_text(
    session_id: str,
    payload: TextMessage,
) -> dict[str, Any]:
    return process_turn(
        session_id=session_id,
        user_text=payload.text,
    )


@app.post("/talk/{session_id}")
async def talk(
    session_id: str,
    audio: UploadFile = File(...),
) -> dict[str, Any]:
    audio_bytes = await audio.read()

    user_text = transcribe_audio(audio_bytes)

    result = process_turn(
        session_id=session_id,
        user_text=user_text,
    )

    audio_reply = await synthesize_speech(
        result["reply_text"]
    )

    return {
        **result,
        "user_text": user_text,
        "audio_reply_b64": base64.b64encode(
            audio_reply
        ).decode("utf-8"),
    }


@app.post("/talk_voice_text/{session_id}")
async def talk_voice_text(
    session_id: str,
    audio: UploadFile = File(...),
) -> dict[str, Any]:
    audio_bytes = await audio.read()

    user_text = transcribe_audio(audio_bytes)

    result = process_turn(
        session_id=session_id,
        user_text=user_text,
    )

    return {
        **result,
        "user_text": user_text,
    }


@app.get("/sessions/{session_id}")
def view_session(
    session_id: str,
) -> dict[str, Any]:
    slots, history, current_index = get_session(
        session_id
    )

    item, index = get_next_question(
        slots,
        current_index,
    )

    return {
        "collected_data": slots,
        "conversation": history,
        "current_topic_index": index,
        "next_question": (
            item["ask"]
            if item
            else None
        ),
    }