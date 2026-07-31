import ollama

SYSTEM_PROMPT = """You are a warm, friendly assistant having a natural conversation
with a Nepali farmer. Your goal is to learn: their name, main crops they grow,
number of children, and whether their children live abroad or in Nepal.

Rules:
- Don't ask questions in a fixed order. Follow the natural flow of conversation.
- After the farmer answers something, react warmly and specifically before
  moving on. For example, if they say they grow tomatoes, comment on tomatoes
  briefly before asking your next question.
- Whenever the farmer reveals any of the target information, call the
  save_farmer_info function with just the new information mentioned.
- If some information is already known (see below), don't ask for it again.
- Keep responses short and conversational, like real speech, not a form."""

def save_farmer_info(name: str = None, crop: str = None,
                      children_count: int = None,
                      children_location: str = None):
    """Save any new farmer detail mentioned in the conversation.
    Only fill in the fields that were actually mentioned this turn."""
    return {"status": "saved"}

TOOLS = [save_farmer_info]

def chat_turn(history: list, user_text: str, known_slots: dict):
    known_info = f"\n\nAlready known about this farmer: {known_slots}" if known_slots else ""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + known_info}
    ] + history + [
        {"role": "user", "content": user_text}
    ]

    response = ollama.chat(
        model="llama3.2",
        messages=messages,
        tools=TOOLS
    )
    return response