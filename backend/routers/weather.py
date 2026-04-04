from fastapi import APIRouter
import random
from datetime import datetime

router = APIRouter()

WEATHER_DATA = {
    "Agra":        {"temp":34,"condition":"Dry","humidity":28,"rainfall":0,"impact":"Price up likely","impact_type":"negative"},
    "Nashik":      {"temp":28,"condition":"Rain","humidity":72,"rainfall":12,"impact":"Supply boost","impact_type":"positive"},
    "Bengaluru":   {"temp":26,"condition":"Clear","humidity":60,"rainfall":0,"impact":"Neutral","impact_type":"neutral"},
    "Patna":       {"temp":31,"condition":"Humid","humidity":80,"rainfall":0,"impact":"Storage risk","impact_type":"negative"},
    "Hyderabad":   {"temp":33,"condition":"Haze","humidity":55,"rainfall":0,"impact":"Neutral","impact_type":"neutral"},
    "Jaipur":      {"temp":38,"condition":"Hot","humidity":20,"rainfall":0,"impact":"Price spike likely","impact_type":"negative"},
    "Chennai":     {"temp":32,"condition":"Partly Cloudy","humidity":74,"rainfall":2,"impact":"Slight supply boost","impact_type":"positive"},
    "Kolkata":     {"temp":30,"condition":"Humid","humidity":82,"rainfall":5,"impact":"Neutral","impact_type":"neutral"},
    "Lucknow":     {"temp":33,"condition":"Dry","humidity":35,"rainfall":0,"impact":"Price up likely","impact_type":"negative"},
    "Pune":        {"temp":27,"condition":"Pleasant","humidity":65,"rainfall":0,"impact":"Neutral","impact_type":"neutral"},
    "Mumbai":      {"temp":30,"condition":"Humid","humidity":88,"rainfall":8,"impact":"Slight supply boost","impact_type":"positive"},
    "Bhopal":      {"temp":35,"condition":"Hot","humidity":30,"rainfall":0,"impact":"Price rise possible","impact_type":"negative"},
}

@router.get("/current")
async def get_weather(city: str = "Agra"):
    data = WEATHER_DATA.get(city, {"temp":30,"condition":"Clear","humidity":60,"rainfall":0,"impact":"Neutral","impact_type":"neutral"})
    return {"city": city, **data, "wind_kmh": round(random.uniform(5,25)), "timestamp": datetime.now().isoformat()}

@router.get("/all")
async def get_all_weather():
    return {"cities": [{"city":c, **d} for c,d in WEATHER_DATA.items()]}
