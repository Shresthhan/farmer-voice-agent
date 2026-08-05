import psycopg2
import json
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:farmerdemo@db:5432/farmerdb")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            slots JSONB DEFAULT '{}',
            history JSONB DEFAULT '[]',
            current_topic_index INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def get_session(session_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT slots, history, current_topic_index FROM sessions WHERE id = %s", (session_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return row[0], row[1], row[2]
    return {}, [], 0

def save_session(session_id: str, slots: dict, history: list, current_topic_index: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sessions (id, slots, history, current_topic_index, updated_at)
        VALUES (%s, %s, %s, %s, NOW())
        ON CONFLICT (id) DO UPDATE
        SET slots = %s,
            history = %s,
            current_topic_index = %s,
            updated_at = NOW()
    """, (
        session_id,
        json.dumps(slots),
        json.dumps(history),
        current_topic_index,
        json.dumps(slots),
        json.dumps(history),
        current_topic_index,
    ))
    conn.commit()
    cur.close()
    conn.close()