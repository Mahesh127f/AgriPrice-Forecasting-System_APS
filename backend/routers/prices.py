from fastapi import APIRouter, Query
from typing import Optional
from data.master import BASE_PRICES, ALL_CROPS, CROPS, STATES_MANDIS, MANDI_COORDS, CATEGORY_MAP, MSP_2024_25
from ml.engine import generate_historical, get_volatility, get_msp_analysis
import random, math

router = APIRouter()

@router.get("/crops")
async def get_crops(category: Optional[str] = None):
    if category and category in CROPS:
        return {"category": category, "crops": CROPS[category]}
    return {"categories": {k: v for k, v in CROPS.items()}, "all": ALL_CROPS}

@router.get("/states")
async def get_states():
    return {"states": list(STATES_MANDIS.keys())}

@router.get("/mandis")
async def get_mandis(state: str):
    mandis = STATES_MANDIS.get(state, [])
    return {"state": state, "mandis": mandis}

@router.get("/current")
async def get_current_price(crop: str, mandi: str = "Agra"):
    base = BASE_PRICES.get(crop, 2000)
    mandi_factor = 0.92 + (hash(mandi) % 20) / 100
    noise = 1 + random.gauss(0, 0.02)
    price = round(base * mandi_factor * noise)
    prev_price = round(price * (1 + random.gauss(0, 0.04)))
    change = price - prev_price
    hist = generate_historical(crop, mandi, 30)
    hist_prices = [h["price"] for h in hist]
    vol = get_volatility(crop, hist_prices)
    msp = get_msp_analysis(crop, price)
    return {
        "crop": crop,
        "mandi": mandi,
        "category": CATEGORY_MAP.get(crop, "unknown"),
        "price": price,
        "prev_price": prev_price,
        "change": change,
        "change_pct": round((change / prev_price) * 100, 2) if prev_price else 0,
        "min_price": round(price * 0.92),
        "max_price": round(price * 1.08),
        "arrivals_tonnes": round(random.uniform(50, 800), 1),
        "unit": "₹/quintal",
        "volatility": vol,
        "msp_analysis": msp
    }

@router.get("/historical")
async def get_historical(crop: str, mandi: str = "Agra", days: int = 90):
    days = min(days, 365)
    data = generate_historical(crop, mandi, days)
    return {"crop": crop, "mandi": mandi, "days": days, "data": data}

@router.get("/all-mandis")
async def get_all_mandi_prices(crop: str):
    base = BASE_PRICES.get(crop, 2000)
    results = []
    for mandi, coords in MANDI_COORDS.items():
        mf = 0.88 + (hash(mandi + crop) % 30) / 100
        price = round(base * mf * (1 + random.gauss(0, 0.03)))
        results.append({
            "mandi": mandi, "price": price,
            "lat": coords["lat"], "lng": coords["lng"],
            "change_pct": round(random.gauss(2, 5), 1),
            "arrivals": round(random.uniform(30, 600), 1)
        })
    results.sort(key=lambda x: x["price"], reverse=True)
    return {"crop": crop, "mandis": results}

@router.get("/compare")
async def compare_crops(state: str = "Uttar Pradesh"):
    results = []
    for crop in ALL_CROPS[:25]:
        base = BASE_PRICES.get(crop, 1000)
        sf = 0.9 + (hash(crop + state) % 20) / 100
        price = round(base * sf)
        chg7  = round(random.gauss(3, 8), 1)
        chg30 = round(random.gauss(5, 14), 1)
        vols  = ["Low","Medium","High"]
        vol   = vols[hash(crop) % 3]
        recs  = ["Sell Now","Hold","Wait"]
        rec   = recs[hash(crop+state) % 3]
        results.append({
            "crop": crop, "category": CATEGORY_MAP.get(crop,""),
            "price": price, "change_7d": chg7, "change_30d": chg30,
            "volatility": vol, "recommendation": rec,
            "has_msp": crop in MSP_2024_25,
            "msp": MSP_2024_25.get(crop)
        })
    return {"state": state, "crops": results}

@router.get("/msp")
async def get_msp_tracker():
    results = []
    for crop, msp in MSP_2024_25.items():
        market = BASE_PRICES.get(crop, msp)
        noise  = 1 + random.gauss(0, 0.04)
        market_price = round(market * noise)
        diff = market_price - msp
        results.append({
            "crop": crop, "msp": msp, "market_price": market_price,
            "diff": diff, "diff_pct": round((diff/msp)*100, 1),
            "above_msp": market_price >= msp,
            "category": CATEGORY_MAP.get(crop,"")
        })
    results.sort(key=lambda x: x["diff_pct"])
    return {"year": "2024-25", "crops": results}
