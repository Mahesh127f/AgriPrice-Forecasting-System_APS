from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import random, os
from datetime import datetime
from data.master import BASE_PRICES, ALL_CROPS, STATES_MANDIS

# ─── WEATHER ────────────────────────────────────────────────
router_weather = APIRouter()

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

@router_weather.get("/current")
async def get_weather(city: str = "Agra"):
    data = WEATHER_DATA.get(city, {"temp":30,"condition":"Clear","humidity":60,"rainfall":0,"impact":"Neutral","impact_type":"neutral"})
    return {"city": city, **data, "wind_kmh": round(random.uniform(5, 25)), "timestamp": datetime.now().isoformat()}

@router_weather.get("/all")
async def get_all_weather():
    return {"cities": [{"city": c, **d} for c, d in WEATHER_DATA.items()]}

# ─── ALERTS ─────────────────────────────────────────────────
router_alerts = APIRouter()
_alerts_store = [
    {"id":1,"crop":"Onion","alert_type":"Price rises above","threshold":2500,"is_active":True,"triggered":False,"created_at":"2025-04-01"},
    {"id":2,"crop":"Tomato","alert_type":"Price falls below","threshold":1500,"is_active":True,"triggered":False,"created_at":"2025-04-01"},
    {"id":3,"crop":"Potato","alert_type":"Price changes by","threshold":200,"is_active":True,"triggered":False,"created_at":"2025-03-31"},
]
_next_id = 4

class AlertCreate(BaseModel):
    crop: str
    alert_type: str
    threshold: float

@router_alerts.get("/")
async def get_alerts():
    return {"alerts": _alerts_store, "count": len(_alerts_store)}

@router_alerts.post("/")
async def create_alert(alert: AlertCreate):
    global _next_id
    new = {"id": _next_id, "crop": alert.crop, "alert_type": alert.alert_type,
           "threshold": alert.threshold, "is_active": True, "triggered": False,
           "created_at": datetime.now().strftime("%Y-%m-%d")}
    _alerts_store.append(new)
    _next_id += 1
    current = BASE_PRICES.get(alert.crop, 0)
    triggered = False
    if alert.alert_type == "Price rises above" and current > alert.threshold:
        triggered = True
    elif alert.alert_type == "Price falls below" and current < alert.threshold:
        triggered = True
    return {"alert": new, "immediately_triggered": triggered}

@router_alerts.delete("/{alert_id}")
async def delete_alert(alert_id: int):
    global _alerts_store
    before = len(_alerts_store)
    _alerts_store = [a for a in _alerts_store if a["id"] != alert_id]
    if len(_alerts_store) == before:
        from fastapi import HTTPException
        raise HTTPException(404, "Alert not found")
    return {"deleted": alert_id, "remaining": len(_alerts_store)}

# ─── REPORTS ────────────────────────────────────────────────
router_reports = APIRouter()

@router_reports.get("/list")
async def list_reports():
    return {"reports": [
        {"id":1,"name":"Weekly Price Summary","crop":"All","type":"Price Summary","format":"CSV","created":"2025-04-01"},
        {"id":2,"name":"Onion 30-Day Forecast","crop":"Onion","type":"Forecast","format":"CSV","created":"2025-04-01"},
        {"id":3,"name":"Maharashtra Market Analysis","crop":"All","type":"Market Analysis","format":"CSV","created":"2025-03-31"},
        {"id":4,"name":"Pulse Price Comparison","crop":"Pulses","type":"Comparison","format":"CSV","created":"2025-03-30"},
        {"id":5,"name":"MSP vs Market Report","crop":"All","type":"MSP Analysis","format":"CSV","created":"2025-03-29"},
    ]}

from fastapi.responses import StreamingResponse
import io, csv as csv_mod

@router_reports.get("/download")
async def download_report(crop: str = "All", report_type: str = "Price Summary"):
    from data.master import BASE_PRICES as BP, MSP_2024_25 as MSP, CATEGORY_MAP as CM
    crops = ALL_CROPS if crop == "All" else [crop]
    output = io.StringIO()
    writer = csv_mod.writer(output)
    writer.writerow(["Crop","Category","Price (₹/qtl)","7D Change (%)","30D Change (%)","Volatility","MSP","Above MSP","Recommendation"])
    for c in crops:
        p    = BP.get(c, 0)
        cat  = CM.get(c, "")
        c7   = round(random.gauss(3, 8), 1)
        c30  = round(random.gauss(5, 14), 1)
        vols = ["Low","Medium","High"]
        vol  = vols[hash(c) % 3]
        msp  = MSP.get(c, "N/A")
        abv  = (p >= msp) if isinstance(msp, int) else "N/A"
        recs = ["Sell Now","Hold","Wait"]
        rec  = recs[hash(c) % 3]
        writer.writerow([c, cat, p, c7, c30, vol, msp, abv, rec])
    output.seek(0)
    filename = f"AgriPrice_{report_type.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.csv"
    return StreamingResponse(io.BytesIO(output.getvalue().encode()),
                             media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename={filename}"})

# ─── AUTH ────────────────────────────────────────────────────
router_auth = APIRouter()
_users = [{"id":1,"name":"Ramesh Kumar","email":"ramesh@example.com","password":"farmer123","state":"Uttar Pradesh","district":"Agra","role":"farmer"}]
_next_uid = 2

class LoginReq(BaseModel):
    email: str
    password: str

class RegisterReq(BaseModel):
    name: str
    email: str
    password: str
    state: str
    district: str

@router_auth.post("/login")
async def login(req: LoginReq):
    user = next((u for u in _users if u["email"]==req.email and u["password"]==req.password), None)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(401, "Invalid credentials")
    return {"token": f"mock_token_{user['id']}", "user": {k:v for k,v in user.items() if k!="password"}}

@router_auth.post("/register")
async def register(req: RegisterReq):
    global _next_uid
    if any(u["email"]==req.email for u in _users):
        from fastapi import HTTPException
        raise HTTPException(400, "Email already registered")
    user = {"id":_next_uid,"name":req.name,"email":req.email,"password":req.password,"state":req.state,"district":req.district,"role":"farmer"}
    _users.append(user)
    _next_uid += 1
    return {"token": f"mock_token_{user['id']}", "user": {k:v for k,v in user.items() if k!="password"}}

@router_auth.get("/me")
async def me(token: str = ""):
    if not token.startswith("mock_token_"):
        from fastapi import HTTPException
        raise HTTPException(401, "Invalid token")
    uid = int(token.replace("mock_token_",""))
    user = next((u for u in _users if u["id"]==uid), None)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(404, "User not found")
    return {k:v for k,v in user.items() if k!="password"}

# ─── ADMIN ────────────────────────────────────────────────────
router_admin = APIRouter()

@router_admin.get("/stats")
async def admin_stats():
    return {
        "total_users": 1284, "total_crops": len(ALL_CROPS),
        "mandis_covered": 312, "uptime_pct": 99.2,
        "predictions_today": 1847, "api_calls_today": 8432,
        "active_alerts": 147, "datasets_count": 24
    }

@router_admin.get("/activity")
async def activity_log():
    return {"activities": [
        {"action":"Dataset uploaded: Agmarknet Apr 2025","time":"2h ago","type":"upload"},
        {"action":"Model retrained: LSTM Onion — RMSE 48","time":"5h ago","type":"model"},
        {"action":"User Ramesh Kumar set price alert","time":"6h ago","type":"user"},
        {"action":"New mandi added: Gondal, Gujarat","time":"12h ago","type":"data"},
        {"action":"Weather data synced: 24 cities","time":"1d ago","type":"sync"},
        {"action":"Admin approved 3 new users","time":"1d ago","type":"admin"},
        {"action":"Report generated: Maharashtra analysis","time":"2d ago","type":"report"},
        {"action":"Forecast API: 1,847 calls today","time":"today","type":"api"},
    ]}

@router_admin.get("/model-performance")
async def model_performance():
    return {
        "months": ["Jan","Feb","Mar","Apr"],
        "random_forest": [88.2, 89.1, 90.8, 91.4],
        "lstm":          [85.1, 86.5, 89.2, 90.1],
        "linear_reg":    [79.3, 80.1, 82.4, 83.2],
        "daily_users":   [320, 450, 680, 780]
    }

# ─── WIRE UP ─────────────────────────────────────────────────
weather = router_weather
alerts  = router_alerts
reports = router_reports
auth    = router_auth
admin   = router_admin

# create module-level routers that main.py can import
import sys, types

def _make_module(name, rtr):
    m = types.ModuleType(name)
    m.router = rtr
    sys.modules[f"routers.{name}"] = m
    return m

_make_module("weather", router_weather)
_make_module("alerts",  router_alerts)
_make_module("reports", router_reports)
_make_module("auth",    router_auth)
_make_module("admin",   router_admin)
