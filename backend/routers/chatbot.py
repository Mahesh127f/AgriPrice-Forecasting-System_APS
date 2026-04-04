from fastapi import APIRouter
from pydantic import BaseModel
from data.master import BASE_PRICES, ALL_CROPS, CATEGORY_MAP, MSP_2024_25
from ml.engine import predict_random_forest, generate_historical
import random, re

router = APIRouter()

RESPONSES = {
    "en": {
        "greeting": "Namaste! I'm your AI farm assistant. Ask me about crop prices, best time to sell, mandi rates, weather impact, or MSP.",
        "fallback": "I can help you with crop prices, selling time, mandi rates, weather impact, and MSP. Please ask about a specific crop.",
    },
    "hi": {
        "greeting": "नमस्ते! मैं आपका AI कृषि सहायक हूं। फसल की कीमत, बेचने का सही समय, मंडी दर, या MSP के बारे में पूछें।",
        "fallback": "मैं फसल कीमत, बेचने का सही समय और MSP में मदद कर सकता हूं। किसी खास फसल के बारे में पूछें।",
    }
}

def generate_response(message: str, lang: str) -> str:
    msg = message.lower()
    r = RESPONSES.get(lang, RESPONSES["en"])

    matched_crop = next((c for c in ALL_CROPS if c.lower() in msg), None)

    if any(w in msg for w in ["hello","hi","namaste","नमस्ते","hey"]):
        return r["greeting"]

    if matched_crop:
        price = BASE_PRICES.get(matched_crop, 2000)
        result = predict_random_forest(matched_crop, "Agra", 7)
        preds  = result["predictions"]
        future = preds[-1]["price"] if preds else price
        pct    = round(((future - price) / price) * 100, 1)
        msp    = MSP_2024_25.get(matched_crop)
        msp_line = f" MSP is ₹{msp:,}/qtl." if msp else ""
        action = "Hold" if pct > 5 else ("Sell Now" if pct < -3 else "Sell in 2-3 days")

        if lang == "hi":
            return (f"{matched_crop} की कीमत अभी ₹{price:,}/क्विंटल है। "
                    f"अगले हफ्ते ₹{future:,} तक जाने का अनुमान है ({pct:+.1f}%)।"
                    f"{msp_line} सुझाव: {action}।")
        return (f"{matched_crop} is currently ₹{price:,}/qtl. "
                f"Forecast: ₹{future:,} next week ({pct:+.1f}%).{msp_line} "
                f"Recommendation: {action}.")

    if any(w in msg for w in ["msp","minimum support","न्यूनतम समर्थन"]):
        msps = list(MSP_2024_25.items())[:5]
        lines = ", ".join(f"{c}: ₹{p:,}" for c,p in msps)
        return f"Key MSP rates 2024-25: {lines}. Ask about a specific crop for details."

    if any(w in msg for w in ["weather","rain","मौसम","बारिश"]):
        if lang == "hi":
            return "मौसम फसल की कीमतों को सीधे प्रभावित करता है। बारिश से आपूर्ति बढ़ती है और कीमतें गिरती हैं। गर्मी या सूखे से कीमतें बढ़ती हैं।"
        return "Weather directly impacts prices. Rain increases supply → prices fall. Drought/heat → prices spike. Check the Weather section on the Dashboard for live impact analysis."

    if any(w in msg for w in ["sell","बेचना","kab bechu","best time"]):
        if lang == "hi":
            return "बेचने का सही समय जानने के लिए फसल का नाम बताएं। मैं मंडी डेटा और भविष्यवाणी के आधार पर सलाह दूंगा।"
        return "To get the best selling advice, tell me which crop you want to sell. I'll analyze mandi data and give a price forecast."

    if any(w in msg for w in ["best crop","which crop","कौन सी फसल"]):
        top = sorted(ALL_CROPS[:20], key=lambda c: BASE_PRICES.get(c,0), reverse=True)[:3]
        return f"Currently high-value crops: {', '.join(top)}. These have strong demand. Ask about any specific crop for detailed forecast."

    return r["fallback"]

class ChatRequest(BaseModel):
    message: str
    lang: str = "en"

@router.post("/chat")
async def chat(req: ChatRequest):
    response = generate_response(req.message, req.lang)
    return {"response": response, "lang": req.lang}
