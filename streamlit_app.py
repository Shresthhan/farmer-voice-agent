from __future__ import annotations

import base64
import uuid

import requests
import streamlit as st

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Farmer Voice Agent", layout="centered")
st.title("Farmer Voice Agent")
st.caption("Text or voice demo for the farm interview flow")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "started" not in st.session_state:
    st.session_state.started = False

if "last_voice_fingerprint" not in st.session_state:
    st.session_state.last_voice_fingerprint = None


def call_start():
    response = requests.get(f"{API_BASE}/start/{st.session_state.session_id}")
    response.raise_for_status()
    return response.json()["reply_text"]


def call_talk_text(text: str):
    response = requests.post(
        f"{API_BASE}/talk_text/{st.session_state.session_id}",
        json={"text": text},
    )
    response.raise_for_status()
    return response.json()


def call_talk_audio(audio_bytes: bytes):
    response = requests.post(
        f"{API_BASE}/talk/{st.session_state.session_id}",
        files={"audio": ("voice.wav", audio_bytes, "audio/wav")},
    )
    response.raise_for_status()
    return response.json()


def append_message(role: str, content: str, audio_b64: str | None = None):
    st.session_state.messages.append(
        {"role": role, "content": content, "audio_b64": audio_b64}
    )


if not st.session_state.started:
    start_text = call_start()
    append_message("assistant", start_text)
    st.session_state.started = True

mode = st.radio("Demo mode", ["Text", "Voice"], horizontal=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant" and message.get("audio_b64"):
            st.audio(base64.b64decode(message["audio_b64"]), format="audio/mp3")

if mode == "Text":
    user_text = st.chat_input("Type your message here")
    if user_text:
        append_message("user", user_text)
        with st.chat_message("user"):
            st.write(user_text)

        try:
            result = call_talk_text(user_text)
            reply = result["reply_text"]
            append_message("assistant", reply)
        except Exception as exc:
            reply = f"Error: {exc}"
            append_message("assistant", reply)

        with st.chat_message("assistant"):
            st.write(reply)

else:
    st.write("Record a short answer, then the assistant will reply with voice.")
    audio_input = None
    if hasattr(st, "audio_input"):
        audio_input = st.audio_input("Record your answer")
    else:
        audio_input = st.file_uploader("Upload a WAV file", type=["wav"])

    if audio_input is not None:
        audio_bytes = (
            audio_input.getvalue()
            if hasattr(audio_input, "getvalue")
            else audio_input.read()
        )
        fingerprint = hash(audio_bytes)

        if fingerprint != st.session_state.last_voice_fingerprint:
            st.session_state.last_voice_fingerprint = fingerprint
            with st.spinner("Listening and responding..."):
                try:
                    result = call_talk_audio(audio_bytes)
                    user_text = result.get("user_text", "Voice message")
                    reply = result["reply_text"]
                    audio_b64 = result.get("audio_reply_b64")

                    append_message("user", user_text)
                    append_message("assistant", reply, audio_b64=audio_b64)

                    st.success("Message sent")
                    with st.chat_message("user"):
                        st.write(user_text)
                    with st.chat_message("assistant"):
                        st.write(reply)
                        if audio_b64:
                            st.audio(base64.b64decode(audio_b64), format="audio/mp3")
                except Exception as exc:
                    st.error(f"Voice request failed: {exc}")