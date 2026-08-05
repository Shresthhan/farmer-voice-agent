from llm_agent import chat_turn
from main import merge_slots
from db import save_session, get_session

slots = {}
history = []
current_topic_index = 0

user1 = "My name is Ram and I grow tomatoes"
r1 = chat_turn(history, user1, slots, "children_count")
print("R1 reply:", r1["reply_text"])
print("R1 tools:", r1["tool_calls"])

if r1["tool_calls"]:
    for call in r1["tool_calls"]:
        slots = merge_slots(slots, call["function"]["arguments"])

history.append({"role": "user", "content": user1})
history.append({"role": "assistant", "content": r1["reply_text"]})
current_topic_index = 1
save_session("test3", slots, history, current_topic_index)

user2 = "I have 2 children, one in Nepal and one in Oman"
r2 = chat_turn(history, user2, slots, "children_abroad")
print("R2 reply:", r2["reply_text"])
print("R2 tools:", r2["tool_calls"])

if r2["tool_calls"]:
    for call in r2["tool_calls"]:
        slots = merge_slots(slots, call["function"]["arguments"])

history.append({"role": "user", "content": user2})
history.append({"role": "assistant", "content": r2["reply_text"]})
current_topic_index = 5
save_session("test3", slots, history, current_topic_index)

print("FINAL SESSION:", get_session("test3"))