from __future__ import annotations

import random
from typing import Any

import ollama


MODEL = "llama3.2"


QUESTIONS = [
    {"field": "name", "ask": "तपाईंको नाम के हो?"},
    {"field": "crop", "ask": "तपाईंले मुख्य रूपमा कुन बाली लगाउनुहुन्छ?"},
    {"field": "location", "ask": "तपाईंको खेत कहाँ छ?"},
    {"field": "children_count", "ask": "तपाईंका कति जना बच्चा छन्?"},
    {"field": "children_in_nepal", "ask": "तीमध्ये कति जना नेपालमै छन्?"},
    {"field": "children_abroad", "ask": "कति जना विदेशमा छन्?"},
    {"field": "abroad_countries", "ask": "उनीहरू कुन देशमा छन्?"},
    {"field": "farm_size", "ask": "तपाईंको खेत कति ठूलो छ?"},
    {"field": "livestock", "ask": "तपाईंले पशुपालन गर्नुहुन्छ?"},
    {"field": "irrigation", "ask": "तपाईंले सिँचाइ कसरी गर्नुहुन्छ?"},
]


# Plain-text extraction. No tool calling — small local models like
# llama3.2 frequently fail to invoke function/tool calls reliably,
# but they are much better at simply answering a direct question.
EXTRACT_PROMPT = """तपाईं किसानको उत्तरबाट एउटा मात्र जानकारी झिक्ने सहायक हुनुहुन्छ।

तपाईंलाई एउटा "field" र किसानको "उत्तर" दिइनेछ।
त्यो field सँग सम्बन्धित मान मात्र फर्काउनुहोस्।

नियमहरू:
- जवाफमा मान मात्र लेख्नुहोस्, अरू केही नलेख्नुहोस्।
- व्याख्या, वाक्य, वा "Value:" जस्ता शब्दहरू नलेख्नुहोस्।
- किसानले उक्त field को बारेमा स्पष्ट रूपमा नभनेको भए ठीक यही शब्द लेख्नुहोस्: NONE
- संख्या भए अंकमा लेख्नुहोस् (जस्तै: 1, 0, 2)।
- "कोही छैन" वा "विदेशमा कोही छैन" जस्ता जवाफको मतलब 0 हो।
- एकाइ (हेक्टर, रोपनी, बिघा) भए नहटाउनुहोस्।
- Romanized Nepali लाई देवनागरीमा लेख्नुहोस्।

उदाहरणहरू:

field: name
उत्तर: मेरो नाम रमन हो।
मान: रमन

field: name
उत्तर: रमन।
मान: रमन

field: crop
उत्तर: म टमाटर लगाउँछु।
मान: टमाटर

field: children_count
उत्तर: एउटा बच्चा छ।
मान: 1

field: children_abroad
उत्तर: विदेशमा कोही छैन।
मान: 0

field: farm_size
उत्तर: एक हेक्टर छ।
मान: १ हेक्टर

field: irrigation
उत्तर: नहरबाट सिँचाइ गर्छु।
मान: नहरबाट सिँचाइ

field: location
उत्तर: आज मौसम राम्रो छ।
मान: NONE
"""


FEEDBACK_PROMPT = """तपाईं किसानसँग फोनमा कुरा गर्ने न्यानो नेपाली सहायक हुनुहुन्छ।

किसानले भर्खरै दिएको उत्तरलाई मात्र छोटो र स्वाभाविक रूपमा स्वीकार गर्नुहोस्।

नियमहरू:
- केवल एउटा छोटो वाक्य लेख्नुहोस्।
- कुनै प्रश्न नसोध्नुहोस्।
- अर्को प्रश्न नलेख्नुहोस्।
- प्रश्नचिह्न (?) प्रयोग नगर्नुहोस्।
- "अर्को प्रश्न", "नम्बर", "survey", "form" जस्ता शब्दहरू प्रयोग नगर्नुहोस्।
- किसानले नभनेको नाम, स्थान, कारण, प्रशंसा वा तथ्य थप्नु हुँदैन।
- उत्तर नेपाली देवनागरीमा मात्र लेख्नुहोस्।
- हिन्दी, अंग्रेजी वा prompt सम्बन्धी कुरा नलेख्नुहोस्।

उदाहरण:
- किसान: मेरो नाम रमन हो।
  प्रतिक्रिया: रमनजी, भेटेर खुशी लाग्यो।

- किसान: टमाटर लगाउँछु।
  प्रतिक्रिया: टमाटर लगाउनुहुँदो रहेछ, बुझें।

- किसान: विदेशमा कोही छैन।
  प्रतिक्रिया: विदेशमा कोही हुनुहुन्न रहेछ।

- किसान: नहरबाट सिँचाइ गर्छु।
  प्रतिक्रिया: नहरबाट सिँचाइ गर्नुहुँदो रहेछ।
"""


END_MESSAGE = "धन्यवाद, तपाईंले सबै जानकारी दिनुभयो। अहिलेका लागि यत्ति काफी छ।"


CLARIFICATION_PHRASES = [
    "माफ गर्नुहोस्, मैले राम्रोसँग बुझिनँ।",
    "माफ गर्नुस्, फेरि भन्नुहोस् न।",
    "मैले नबुझेको हुनसक्छ, फेरि एकपटक भन्नुहोस्।",
    "क्षमा गर्नुहोस्, फेरि दोहोर्‍याइदिनुहोस् न।",
    "बुझ्न सकिनँ, अलि छर्लङ्ग भन्नुहोस् त।",
]


def extract_value(
    user_text: str,
    expected_field: str | None,
) -> str | None:
    """
    Plain-text extraction (no tool calling).
    Returns the extracted value, or None if the model
    says NONE or the field isn't clearly answered.
    """

    if not expected_field:
        return None

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": EXTRACT_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    f"field: {expected_field}\n"
                    f"उत्तर: {user_text}\n"
                    f"मान:"
                ),
            },
        ],
        options={
            "temperature": 0,
        },
    )

    text = response.get("message", {}).get("content", "").strip()

    # Clean up common formatting artifacts.
    text = text.strip("\"'“”'। \n")

    if not text:
        return None

    if text.strip().upper() == "NONE":
        return None

    if "none" in text.lower() and len(text) < 8:
        return None

    return text


def generate_feedback(
    user_text: str,
    current_question: str,
) -> str:
    """
    Generate only a short acknowledgment.
    The model must not generate the next question.
    """

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": FEEDBACK_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    f"हालको प्रश्न: {current_question}\n"
                    f"किसानको उत्तर: {user_text}"
                ),
            },
        ],
        options={
            "temperature": 0.4,
        },
    )

    text = response.get("message", {}).get("content", "").strip()

    if not text:
        return "बुझें।"

    unwanted_phrases = [
        "अर्को प्रश्न",
        "नम्बर",
        "survey",
        "form",
        "क्या आप",
        "यदि नहीं",
        "why should",
        "प्रश्नलाई",
        "?",
    ]

    text_lower = text.lower()

    if any(
        phrase.lower() in text_lower
        for phrase in unwanted_phrases
    ):
        return "बुझें।"

    return text


def build_natural_reply(
    user_text: str,
    current_question: str,
    next_question: str | None,
) -> str:
    if next_question is None:
        return END_MESSAGE

    feedback = generate_feedback(
        user_text=user_text,
        current_question=current_question,
    )

    return f"{feedback} {next_question}"


def build_clarification_reply(
    current_question: str,
) -> str:
    phrase = random.choice(CLARIFICATION_PHRASES)
    return f"{phrase} {current_question}"


def generate_end_message() -> str:
    return END_MESSAGE