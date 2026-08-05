import ollama

QUESTIONS = [
    {"field": "name", "ask": "What is your name?"},
    {"field": "crop", "ask": "What crop do you grow most?"},
    {"field": "location", "ask": "Where is your farm located?"},
    {"field": "children_count", "ask": "How many children do you have?"},
    {"field": "children_in_nepal", "ask": "How many of them live in Nepal?"},
    {"field": "children_abroad", "ask": "How many live abroad?"},
    {"field": "abroad_countries", "ask": "Which countries are they in?"},
    {"field": "farm_size", "ask": "How big is your farm?"},
    {"field": "livestock", "ask": "Do you keep livestock?"},
    {"field": "irrigation", "ask": "What kind of irrigation do you use?"}
]

EXTRACT_PROMPT = """You extract only the facts the farmer actually says.
Call save_farmer_info with real values only.
Do not guess.
Do not fill missing fields with 0, [] or any placeholder.
If a value is not mentioned, leave it out.
"""

FOLLOWUP_PROMPT = """You are a warm, friendly assistant talking to a farmer.

Respond like a real person having a natural conversation, not like a form or script.
Keep the reply short, human, relaxed, and varied.

Stay strictly grounded in the farmer’s latest answer only.
Do not assume, infer, or invent any detail you cannot verify from what the user just said.
Do not use known slots or earlier context to add new facts.
Do not mention crops, seasons, quality, location, family, weather, yield, or any other detail unless the user explicitly said it in their latest answer.

Give light positive feedback when it fits naturally.
Acknowledge the answer in a way that sounds warm, supportive, and conversational.
Keep praise modest and believable.
If the answer contains a place, number, crop, animal, or farm detail, you may react to that detail naturally.
If the answer is simple, still respond warmly but briefly.

Examples of the style:
- "Nice to meet you, Ram."
- "Tomatoes, nice."
- "Dhading is lovely."
- "That sounds like a busy household."
- "Australia, got it."
- "One hectare, okay."
- "Cows and hens, nice."
- "Canals for irrigation, that makes sense."

Avoid bland replies like "That sounds good" unless nothing better fits.
Avoid repeating the same phrase too often.
Do not ask a question.
Do not mention the next question.
Do not sound like an AI, chatbot, survey form, or interviewer.
Write only one short sentence.
"""

REPLY_PROMPT = """You are a warm and friendly assistant talking to a farmer.
First react to what the farmer just said in a natural way.
Then ask the next question naturally, based on the question text you are given.
Do not sound like a form.
Do not repeat known questions.
Keep the reply short and human.
"""

START_PROMPT = """You are a warm and friendly assistant.
Start the conversation with a simple greeting.
Do not assume the farmer’s name.
Keep it short, polite, and easy to understand.
Then ask the first question: What is your name?
"""

END_MESSAGE = "Thanks for sharing everything. I’ve got all the information I needed for now."


def save_farmer_info(name: str = None, crop: str = None,
                     location: str = None,
                     children_count: int = None,
                     children_in_nepal: int = None,
                     children_abroad: int = None,
                     abroad_countries: list[str] = None,
                     farm_size: str = None,
                     livestock: str = None,
                     irrigation: str = None,
                     other_info: str = None):
    return {"status": "saved"}


TOOLS = [save_farmer_info]


def extract_info(user_text: str, expected_field: str | None = None):
    field_hint = f"\nCurrent field to extract: {expected_field}. Only extract this field if it is clearly mentioned." if expected_field else ""
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": EXTRACT_PROMPT + field_hint},
            {"role": "user", "content": user_text}
        ],
        tools=TOOLS
    )
    return response["message"].get("tool_calls")


def generate_followup_reply(user_text: str, current_field: str | None, current_question: str):
    field_hint = f"\nCurrent field: {current_field}" if current_field else ""
    messages = [
        {
            "role": "system",
            "content": FOLLOWUP_PROMPT + field_hint + f"\nCurrent question: {current_question}",
        },
        {"role": "user", "content": user_text},
    ]
    response = ollama.chat(model="llama3.2", messages=messages, options={"temperature": 0.6})
    return response["message"]["content"]


def generate_start_message():
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": START_PROMPT}
        ]
    )
    return response["message"]["content"]


def generate_end_message():
    return END_MESSAGE


def chat_turn(
    user_text: str,
    expected_field: str | None,
    current_question: str,
    next_question: str | None = None,
):
    tool_calls = extract_info(user_text, expected_field=expected_field)
    reply_text = generate_followup_reply(
        user_text=user_text,
        current_field=expected_field,
        current_question=current_question,
    )
    return {"reply_text": reply_text, "tool_calls": tool_calls}