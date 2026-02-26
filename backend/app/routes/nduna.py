"""
Nduna Chatbot - Multilingual AI Assistant for iHhashi
Supports all 6 South African languages with Groq LLM
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import httpx
import os
from datetime import datetime

router = APIRouter(prefix="/nduna", tags=["nduna"])

# Groq API configuration
GROQ_API_KEYS = [
    "REMOVED_SECRET_1",
    "REMOVED_SECRET_2",
    "REMOVED_SECRET_3",
    "REMOVED_SECRET_4",
    "REMOVED_SECRET_5",
    "REMOVED_SECRET_6",
    "REMOVED_SECRET_7",
]

# Key rotation for rate limiting
current_key_index = 0


def get_next_groq_key():
    """Rotate through Groq API keys for load balancing"""
    global current_key_index
    key = GROQ_API_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(GROQ_API_KEYS)
    return key


# Language configurations
LANGUAGES = {
    "en": {
        "name": "English",
        "greeting": "Hello! I'm Nduna, your iHhashi assistant. How can I help you today?",
        "system_prompt": """You are Nduna, a friendly and helpful AI assistant for iHhashi, a food delivery platform in South Africa. 
You help customers with:
- Placing and tracking orders
- Finding restaurants and food
- Delivery questions
- Account and payment help
- General support

Be friendly, concise, and helpful. Use South African context when appropriate.
Respond in English unless the user speaks another language."""
    },
    "zu": {
        "name": "isiZulu",
        "greeting": "Sawubona! NginguNduna, umsizi wakho we-iHhashi. Ngingakusiza kanjani namuhla?",
        "system_prompt": """You are Nduna, a friendly and helpful AI assistant for iHhashi, a food delivery platform in South Africa.
You help customers with orders, finding restaurants, delivery, and support.
Be friendly, concise, and helpful. Respond in isiZulu (Zulu) language.
Use South African context and cultural references when appropriate."""
    },
    "xh": {
        "name": "isiXhosa",
        "greeting": "Molo! NdinguNduna, umncedi wakho we-iHhashi. Ndingakunceda njani namhlanje?",
        "system_prompt": """You are Nduna, a friendly and helpful AI assistant for iHhashi, a food delivery platform in South Africa.
You help customers with orders, finding restaurants, delivery, and support.
Be friendly, concise, and helpful. Respond in isiXhosa (Xhosa) language.
Use South African context and cultural references when appropriate."""
    },
    "af": {
        "name": "Afrikaans",
        "greeting": "Hallo! Ek is Nduna, jou iHhashi-assistent. Hoe kan ek jou vandag help?",
        "system_prompt": """You are Nduna, a friendly and helpful AI assistant for iHhashi, a food delivery platform in South Africa.
You help customers with orders, finding restaurants, delivery, and support.
Be friendly, concise, and helpful. Respond in Afrikaans language.
Use South African context and cultural references when appropriate."""
    },
    "st": {
        "name": "Sesotho",
        "greeting": "Dumela! Ke Nduna, motho ya thusang ho iHhashi. Nka u thusa joang kajeno?",
        "system_prompt": """You are Nduna, a friendly and helpful AI assistant for iHhashi, a food delivery platform in South Africa.
You help customers with orders, finding restaurants, delivery, and support.
Be friendly, concise, and helpful. Respond in Sesotho (Sotho) language.
Use South African context and cultural references when appropriate."""
    },
    "tn": {
        "name": "Setswana",
        "greeting": "Dumela! Ke Nduna, motho yo o thusang mo iHhashi. Nka go thusa jang gompieno?",
        "system_prompt": """You are Nduna, a friendly and helpful AI assistant for iHhashi, a food delivery platform in South Africa.
You help customers with orders, finding restaurants, delivery, and support.
Be friendly, concise, and helpful. Respond in Setswana (Tswana) language.
Use South African context and cultural references when appropriate."""
    },
    "so": {
        "name": "Sesotho sa Leboa (Northern Sotho)",
        "greeting": "Thobela! Ke Nduna, motho wa thuso wa iHhashi. Nka go thuša bjang lehono?",
        "system_prompt": """You are Nduna, a friendly and helpful AI assistant for iHhashi, a food delivery platform in South Africa.
You help customers with orders, finding restaurants, delivery, and support.
Be friendly, concise, and helpful. Respond in Sesotho sa Leboa (Northern Sotho/Pedi) language.
Use South African context and cultural references when appropriate."""
    }
}


class ChatMessage(BaseModel):
    message: str
    language: str = "en"
    user_id: Optional[str] = None
    context: Optional[dict] = None
    conversation_history: Optional[List[dict]] = []


class ChatResponse(BaseModel):
    response: str
    language: str
    suggestions: Optional[List[str]] = None


class LanguageInfo(BaseModel):
    code: str
    name: str
    greeting: str


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    languages = [
        LanguageInfo(code=code, name=lang["name"], greeting=lang["greeting"])
        for code, lang in LANGUAGES.items()
    ]
    return {"languages": languages}


@router.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """
    Chat with Nduna AI assistant
    
    Supports 7 South African languages:
    - en: English
    - zu: isiZulu
    - xh: isiXhosa
    - af: Afrikaans
    - st: Sesotho
    - tn: Setswana
    - so: Sesotho sa Leboa (Northern Sotho)
    """
    lang_code = chat_message.language.lower()
    if lang_code not in LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {lang_code}")
    
    language_config = LANGUAGES[lang_code]
    
    # Build conversation for Groq
    messages = [
        {"role": "system", "content": language_config["system_prompt"]}
    ]
    
    # Add conversation history
    if chat_message.conversation_history:
        for msg in chat_message.conversation_history[-10:]:  # Last 10 messages
            messages.append(msg)
    
    # Add current message
    messages.append({"role": "user", "content": chat_message.message})
    
    # Add context if provided
    if chat_message.context:
        context_str = f"\n\nCurrent context:\n"
        if chat_message.context.get("order_status"):
            context_str += f"Order status: {chat_message.context['order_status']}\n"
        if chat_message.context.get("location"):
            context_str += f"Location: {chat_message.context['location']}\n"
        if chat_message.context.get("cart_items"):
            context_str += f"Cart items: {len(chat_message.context['cart_items'])} items\n"
        messages[0]["content"] += context_str
    
    # Call Groq API
    api_key = get_next_groq_key()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": messages,
                    "max_tokens": 500,
                    "temperature": 0.7
                }
            )
            
            if response.status_code != 200:
                # Try with next key if rate limited
                if response.status_code == 429:
                    api_key = get_next_groq_key()
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama-3.3-70b-versatile",
                            "messages": messages,
                            "max_tokens": 500,
                            "temperature": 0.7
                        }
                    )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Groq API error"
                    )
            
            data = response.json()
            ai_response = data["choices"][0]["message"]["content"]
            
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Request timeout")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Generate suggestions based on context
    suggestions = generate_suggestions(chat_message.message, chat_message.context)
    
    return ChatResponse(
        response=ai_response,
        language=lang_code,
        suggestions=suggestions
    )


def generate_suggestions(message: str, context: Optional[dict]) -> List[str]:
    """Generate quick reply suggestions based on message and context"""
    suggestions = []
    
    message_lower = message.lower()
    
    if "order" in message_lower:
        suggestions = [
            "Track my order",
            "Cancel order",
            "Contact rider",
            "Order again"
        ]
    elif "restaurant" in message_lower or "food" in message_lower:
        suggestions = [
            "Nearby restaurants",
            "Popular dishes",
            "Special offers",
            "My favorites"
        ]
    elif "deliver" in message_lower:
        suggestions = [
            "Delivery status",
            "Delivery time",
            "Change address",
            "Contact support"
        ]
    elif "pay" in message_lower or "payment" in message_lower:
        suggestions = [
            "Payment methods",
            "Add card",
            "View receipts",
            "Refund status"
        ]
    else:
        suggestions = [
            "Place an order",
            "Track order",
            "Find restaurants",
            "Get help"
        ]
    
    return suggestions[:4]


@router.post("/quick-replies")
async def get_quick_replies(context: dict):
    """Get context-aware quick reply suggestions"""
    suggestions = []
    
    if context.get("screen") == "home":
        suggestions = [
            {"text": "Order food", "action": "search"},
            {"text": "My orders", "action": "orders"},
            {"text": "Nearby deals", "action": "deals"}
        ]
    elif context.get("screen") == "order_tracking":
        suggestions = [
            {"text": "Contact rider", "action": "call_rider"},
            {"text": "Order details", "action": "order_details"},
            {"text": "Help", "action": "support"}
        ]
    elif context.get("screen") == "checkout":
        suggestions = [
            {"text": "Apply promo code", "action": "promo"},
            {"text": "Change delivery time", "action": "schedule"},
            {"text": "Add tip", "action": "tip"}
        ]
    
    return {"suggestions": suggestions}


@router.get("/greeting/{language}")
async def get_greeting(language: str):
    """Get greeting message for a specific language"""
    lang_code = language.lower()
    if lang_code not in LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {lang_code}")
    
    return {
        "language": lang_code,
        "greeting": LANGUAGES[lang_code]["greeting"],
        "language_name": LANGUAGES[lang_code]["name"]
    }
