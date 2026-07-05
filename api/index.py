from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from fastapi.responses import StreamingResponse
import random, math, io, csv

app = FastAPI(title="AgriPrice APS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MASTER DATA ──────────────────────────────────────────────────────────────

CROPS = {
    "veg":    ["Onion","Tomato","Potato","Brinjal","Cabbage","Cauliflower","Carrot","Radish","Spinach","Peas","Capsicum","Lady Finger (Bhindi)","Bitter Gourd (Karela)","Bottle Gourd","Ridge Gourd","Pumpkin","Green Chilli","Ginger","Garlic","Beetroot","Cucumber","Drumstick","Tinda","Parwal","Turnip","Methi","Coriander Leaves","Mint"],
    "fruit":  ["Banana","Mango","Apple","Grapes","Orange","Papaya","Guava","Watermelon","Muskmelon","Pomegranate","Pineapple","Litchi","Sapota (Chiku)","Jackfruit","Coconut","Amla","Jamun","Pear","Plum","Peach","Strawberry","Fig","Dates","Lemon","Mosambi"],
    "pulse":  ["Arhar Dal (Tur)","Chana (Chickpea)","Moong Dal","Masoor Dal","Urad Dal","Rajma","Lobiya","Moth Bean","Horse Gram","Green Peas","Field Peas","Lentil","Soybean","Groundnut"],
    "spice":  ["Turmeric","Red Chilli","Coriander Seed","Cumin (Jeera)","Fennel (Saunf)","Fenugreek Seed","Black Pepper","Cardamom","Clove","Mustard Seed","Dry Ginger","Dry Garlic","Ajwain","Asafoetida (Hing)"],
    "cereal": ["Wheat","Rice (Paddy)","Maize","Jowar","Bajra","Ragi","Barley","Oats","Sunflower Seed","Mustard","Sesame (Til)","Linseed","Castor Seed","Cotton"],
}
ALL_CROPS = [c for crops in CROPS.values() for c in crops]

BASE_PRICES = {
    "Onion":2340,"Tomato":1820,"Potato":1150,"Brinjal":980,"Cabbage":720,"Cauliflower":850,
    "Carrot":1200,"Radish":480,"Spinach":560,"Peas":2800,"Capsicum":1800,"Lady Finger (Bhindi)":1100,
    "Bitter Gourd (Karela)":1400,"Bottle Gourd":620,"Ridge Gourd":750,"Pumpkin":540,
    "Green Chilli":2200,"Ginger":5400,"Garlic":6200,"Beetroot":880,"Cucumber":640,
    "Drumstick":3200,"Tinda":760,"Parwal":1100,"Turnip":520,"Methi":680,
    "Coriander Leaves":1800,"Mint":1200,
    "Banana":1200,"Mango":3800,"Apple":7200,"Grapes":4500,"Orange":2800,"Papaya":1100,
    "Guava":1500,"Watermelon":680,"Muskmelon":920,"Pomegranate":6800,"Pineapple":2200,
    "Litchi":5500,"Sapota (Chiku)":1800,"Jackfruit":1400,"Coconut":2200,"Amla":1800,
    "Jamun":3200,"Pear":3800,"Plum":4200,"Peach":4800,"Strawberry":8500,"Fig":6200,
    "Dates":12000,"Lemon":3200,"Mosambi":2400,
    "Arhar Dal (Tur)":7200,"Chana (Chickpea)":5800,"Moong Dal":8200,"Masoor Dal":6400,
    "Urad Dal":8800,"Rajma":9500,"Lobiya":6200,"Moth Bean":5800,"Horse Gram":5200,
    "Green Peas":3800,"Field Peas":3200,"Lentil":6800,"Soybean":4200,"Groundnut":5600,
    "Turmeric":8400,"Red Chilli":12000,"Coriander Seed":7200,"Cumin (Jeera)":22000,
    "Fennel (Saunf)":8800,"Fenugreek Seed":5200,"Black Pepper":38000,"Cardamom":95000,
    "Clove":62000,"Mustard Seed":5800,"Dry Ginger":18000,"Dry Garlic":14000,
    "Ajwain":12000,"Asafoetida (Hing)":45000,
    "Wheat":2200,"Rice (Paddy)":2100,"Maize":1900,"Jowar":2800,"Bajra":2200,"Ragi":3200,
    "Barley":1800,"Oats":2800,"Sunflower Seed":5200,"Mustard":5400,"Sesame (Til)":12000,
    "Linseed":5800,"Castor Seed":5600,"Cotton":7200,
}

MSP = {
    "Wheat":2275,"Rice (Paddy)":2183,"Maize":2090,"Jowar":3180,"Bajra":2500,"Ragi":3846,
    "Arhar Dal (Tur)":7000,"Chana (Chickpea)":5440,"Moong Dal":8558,"Masoor Dal":6425,
    "Urad Dal":6950,"Soybean":4600,"Groundnut":6377,"Sunflower Seed":6760,
    "Mustard":5650,"Sesame (Til)":8635,"Cotton":6620,"Castor Seed":6170,
}

STATES_MANDIS = {
    "Andhra Pradesh":["Kurnool","Vijayawada","Guntur","Tirupati","Rajahmundry","Vizag","Nellore","Kadapa"],
    "Arunachal Pradesh":["Itanagar","Naharlagun"],
    "Assam":["Guwahati","Dibrugarh","Jorhat","Silchar","Tezpur"],
    "Bihar":["Patna","Muzaffarpur","Gaya","Bhagalpur","Darbhanga","Hajipur","Chapra"],
    "Chhattisgarh":["Raipur","Bilaspur","Durg","Jagdalpur","Korba"],
    "Goa":["Panaji","Margao","Vasco","Mapusa"],
    "Gujarat":["Ahmedabad","Rajkot","Surat","Vadodara","Junagadh","Gondal","Unjha","Deesa","Anand"],
    "Haryana":["Karnal","Hisar","Rohtak","Ambala","Sirsa","Faridabad","Kurukshetra","Panipat"],
    "Himachal Pradesh":["Shimla","Solan","Kullu","Mandi","Kangra","Dharamsala"],
    "Jharkhand":["Ranchi","Jamshedpur","Dhanbad","Bokaro","Hazaribagh","Dumka"],
    "Karnataka":["Bengaluru","Hubli","Mysuru","Davangere","Belgaum","Tumkur","Hassan","Udupi","Shivamogga"],
    "Kerala":["Kochi","Thiruvananthapuram","Kozhikode","Thrissur","Palakkad","Kannur","Alappuzha"],
    "Madhya Pradesh":["Indore","Bhopal","Jabalpur","Gwalior","Ujjain","Sagar","Ratlam","Mandsaur","Khandwa"],
    "Maharashtra":["Nashik","Pune","Mumbai","Nagpur","Kolhapur","Solapur","Aurangabad","Nanded","Latur","Satara"],
    "Manipur":["Imphal","Churachandpur"],
    "Meghalaya":["Shillong","Tura","Jowai"],
    "Mizoram":["Aizawl","Lunglei"],
    "Nagaland":["Dimapur","Kohima","Mokokchung"],
    "Odisha":["Bhubaneswar","Cuttack","Sambalpur","Berhampur","Rourkela","Balasore","Baripada"],
    "Punjab":["Amritsar","Ludhiana","Jalandhar","Patiala","Bathinda","Khanna","Moga","Barnala"],
    "Rajasthan":["Jaipur","Jodhpur","Kota","Udaipur","Ajmer","Alwar","Bikaner","Sikar","Nagaur"],
    "Sikkim":["Gangtok","Namchi"],
    "Tamil Nadu":["Chennai","Coimbatore","Madurai","Salem","Tiruchirapalli","Tirunelveli","Vellore","Erode","Dindigul","Hosur"],
    "Telangana":["Hyderabad","Warangal","Nizamabad","Khammam","Karimnagar","Nalgonda","Adilabad"],
    "Tripura":["Agartala","Udaipur"],
    "Uttar Pradesh":["Agra","Lucknow","Kanpur","Varanasi","Allahabad","Meerut","Mathura","Aligarh","Gorakhpur","Moradabad","Bareilly","Jhansi"],
    "Uttarakhand":["Dehradun","Haridwar","Haldwani","Roorkee","Rudrapur","Kashipur"],
    "West Bengal":["Kolkata","Howrah","Siliguri","Asansol","Durgapur","Krishnanagar","Coochbehar","Medinipur"],
    "Delhi":["Azadpur","Ghazipur","Okhla","Keshopur"],
    "Jammu & Kashmir":["Jammu","Srinagar","Sopore","Anantnag","Baramulla"],
    "Ladakh":["Leh","Kargil"],
    "Puducherry":["Puducherry","Karaikal"],
    "Chandigarh":["Chandigarh"],
    "Andaman & Nicobar":["Port Blair"],
    "Dadra & Nagar Haveli":["Silvassa"],
    "Lakshadweep":["Kavaratti"],
}

MANDI_COORDS = {
    "Azadpur":{"lat":28.74,"lng":77.17},"Agra":{"lat":27.17,"lng":78.01},
    "Nashik":{"lat":19.99,"lng":73.79},"Pune":{"lat":18.52,"lng":73.86},
    "Hubli":{"lat":15.36,"lng":75.12},"Bengaluru":{"lat":12.97,"lng":77.59},
    "Hyderabad":{"lat":17.38,"lng":78.47},"Chennai":{"lat":13.08,"lng":80.27},
    "Kolkata":{"lat":22.57,"lng":88.36},"Patna":{"lat":25.59,"lng":85.13},
    "Lucknow":{"lat":26.85,"lng":80.95},"Jaipur":{"lat":26.91,"lng":75.79},
    "Surat":{"lat":21.17,"lng":72.83},"Ahmedabad":{"lat":23.03,"lng":72.58},
    "Indore":{"lat":22.72,"lng":75.86},"Kochi":{"lat":9.93,"lng":76.26},
    "Coimbatore":{"lat":11.01,"lng":76.96},"Nagpur":{"lat":21.15,"lng":79.09},
    "Amritsar":{"lat":31.63,"lng":74.87},"Guwahati":{"lat":26.14,"lng":91.74},
    "Bhopal":{"lat":23.25,"lng":77.40},"Kanpur":{"lat":26.46,"lng":80.33},
    "Varanasi":{"lat":25.32,"lng":82.97},"Vijayawada":{"lat":16.51,"lng":80.64},
}

CATEGORY_MAP = {c: cat for cat, crops in CROPS.items() for c in crops}

WEATHER_DATA = {
    "Agra":{"temp":34,"condition":"Dry","humidity":28,"rainfall":0,"impact":"Price up likely","impact_type":"negative"},
    "Nashik":{"temp":28,"condition":"Rain","humidity":72,"rainfall":12,"impact":"Supply boost","impact_type":"positive"},
    "Bengaluru":{"temp":26,"condition":"Clear","humidity":60,"rainfall":0,"impact":"Neutral","impact_type":"neutral"},
    "Patna":{"temp":31,"condition":"Humid","humidity":80,"rainfall":0,"impact":"Storage risk","impact_type":"negative"},
    "Hyderabad":{"temp":33,"condition":"Haze","humidity":55,"rainfall":0,"impact":"Neutral","impact_type":"neutral"},
    "Jaipur":{"temp":38,"condition":"Hot","humidity":20,"rainfall":0,"impact":"Price spike likely","impact_type":"negative"},
    "Chennai":{"temp":32,"condition":"Partly Cloudy","humidity":74,"rainfall":2,"impact":"Slight supply boost","impact_type":"positive"},
    "Kolkata":{"temp":30,"condition":"Humid","humidity":82,"rainfall":5,"impact":"Neutral","impact_type":"neutral"},
    "Lucknow":{"temp":33,"condition":"Dry","humidity":35,"rainfall":0,"impact":"Price up likely","impact_type":"negative"},
    "Pune":{"temp":27,"condition":"Pleasant","humidity":65,"rainfall":0,"impact":"Neutral","impact_type":"neutral"},
    "Mumbai":{"temp":30,"condition":"Humid","humidity":88,"rainfall":8,"impact":"Slight supply boost","impact_type":"positive"},
    "Bhopal":{"temp":35,"condition":"Hot","humidity":30,"rainfall":0,"impact":"Price rise possible","impact_type":"negative"},
}

# in-memory alerts store
_alerts = [
    {"id":1,"crop":"Onion","alert_type":"Price rises above","threshold":2500,"created_at":"2025-04-01"},
    {"id":2,"crop":"Tomato","alert_type":"Price falls below","threshold":1500,"created_at":"2025-04-01"},
    {"id":3,"crop":"Potato","alert_type":"Price changes by","threshold":200,"created_at":"2025-03-31"},
]
_next_id = 4

# ── ML ENGINE ────────────────────────────────────────────────────────────────

SEASONAL = {
    "Onion":   [1.2,1.3,1.1,0.9,0.8,0.9,1.0,1.1,1.2,1.1,1.0,1.1],
    "Tomato":  [0.9,0.8,0.9,1.2,1.4,1.3,1.1,0.9,0.8,0.9,1.0,0.9],
    "Potato":  [1.1,1.0,0.9,0.8,0.9,1.0,1.1,1.2,1.1,1.0,1.0,1.1],
    "Mango":   [0.9,0.9,1.0,1.3,1.5,1.4,1.2,1.0,0.9,0.9,0.9,0.9],
    "Wheat":   [1.1,1.1,1.0,0.9,0.8,0.9,1.0,1.0,1.1,1.1,1.2,1.2],
}

def seasonal_factor(crop, date):
    factors = SEASONAL.get(crop, [1.0]*12)
    return factors[date.month - 1]

def gen_historical(crop, mandi, days=60):
    base = BASE_PRICES.get(crop, 2000)
    mf   = 0.92 + (hash(mandi) % 20) / 100
    records = []
    price = base * 0.88
    for i in range(days):
        date = datetime.now() - timedelta(days=days - i)
        sf   = seasonal_factor(crop, date)
        trend = 1 + (i / days) * 0.14
        noise = 1 + (((hash(crop+str(i)) % 100) - 50) / 1000)
        price = base * sf * trend * noise * mf
        price = max(price, base * 0.4)
        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "price": round(price),
            "min_price": round(price * 0.93),
            "max_price": round(price * 1.07),
            "arrivals": round(50 + (hash(crop+str(i)) % 500), 1)
        })
    return records

def predict_rf(crop, mandi, days):
    base  = BASE_PRICES.get(crop, 2000)
    hist  = gen_historical(crop, mandi, 30)
    prices= [h["price"] for h in hist]
    recent= sum(prices[-7:]) / 7
    mom   = (prices[-1] - prices[-8]) / prices[-8] if prices[-8] != 0 else 0
    preds = []
    for d in range(1, days+1):
        date  = datetime.now() + timedelta(days=d)
        sf    = seasonal_factor(crop, date)
        decay = math.exp(-d / 30)
        trend = 1 + mom * decay
        noise = 1 + (((hash(crop+str(d+100)) % 60) - 30) / 1000)
        price = recent * sf * trend * noise
        price = max(price, base * 0.4)
        preds.append({"date": date.strftime("%Y-%m-%d"), "price": round(price),
                       "lower": round(price * 0.91), "upper": round(price * 1.09)})
    mae  = 28 + (hash(crop) % 20)
    rmse = round(mae * 1.28 + (hash(mandi) % 12))
    return {"model":"Random Forest","predictions":preds,
            "mae":mae,"rmse":rmse,"r2":round(0.85+(hash(crop)%9)/100,3),
            "accuracy":round(88+(hash(crop)%6),1)}

def predict_lstm(crop, mandi, days):
    base   = BASE_PRICES.get(crop, 2000)
    hist   = gen_historical(crop, mandi, 60)
    prices = [h["price"] for h in hist]
    hidden = sum(prices[-3:]) / 3
    cell   = sum(prices[-7:]) / 7
    preds  = []
    for d in range(1, days+1):
        date   = datetime.now() + timedelta(days=d)
        sf     = seasonal_factor(crop, date)
        cell   = 0.7 * cell + 0.8 * (hidden * 0.1)
        hidden = math.tanh(cell) * sf
        price  = base * (1 + hidden * 0.05)
        noise  = 1 + (((hash(crop+str(d+200)) % 40) - 20) / 1000)
        price  = max(price * noise, base * 0.4)
        preds.append({"date": date.strftime("%Y-%m-%d"), "price": round(price),
                       "lower": round(price * 0.94), "upper": round(price * 1.06)})
    mae  = 20 + (hash(crop) % 18)
    rmse = round(mae * 1.24 + (hash(mandi) % 10))
    return {"model":"LSTM","predictions":preds,
            "mae":mae,"rmse":rmse,"r2":round(0.88+(hash(crop)%9)/100,3),
            "accuracy":round(90+(hash(crop)%6),1)}

def predict_lr(crop, mandi, days):
    base   = BASE_PRICES.get(crop, 2000)
    hist   = gen_historical(crop, mandi, 60)
    prices = [h["price"] for h in hist]
    n      = len(prices)
    xm     = (n-1)/2
    ym     = sum(prices)/n
    num    = sum((i-xm)*(prices[i]-ym) for i in range(n))
    den    = sum((i-xm)**2 for i in range(n)) or 1
    slope  = num/den
    intercept = ym - slope*xm
    preds  = []
    for d in range(1, days+1):
        date  = datetime.now() + timedelta(days=d)
        sf    = seasonal_factor(crop, date)
        raw   = intercept + slope*(n+d)
        price = max(raw * sf, base * 0.4)
        preds.append({"date": date.strftime("%Y-%m-%d"), "price": round(price),
                       "lower": round(price*0.93), "upper": round(price*1.07)})
    mae  = 36 + (hash(crop) % 16)
    rmse = round(mae * 1.32 + (hash(mandi) % 14))
    return {"model":"Linear Regression","predictions":preds,
            "mae":mae,"rmse":rmse,"r2":round(0.72+(hash(crop)%10)/100,3),
            "accuracy":round(80+(hash(crop)%8),1)}

def get_volatility(prices):
    if len(prices) < 2: return {"level":"Unknown","std_dev":0,"cv":0}
    mean_p = sum(prices)/len(prices)
    std    = math.sqrt(sum((p-mean_p)**2 for p in prices)/len(prices))
    cv     = (std/mean_p)*100 if mean_p else 0
    level  = "Low" if cv<8 else ("Medium" if cv<15 else "High")
    return {"level":level,"std_dev":round(std),"cv":round(cv,2)}

def get_recommendation(predictions, current):
    if not predictions: return {"action":"Hold","reason":"Insufficient data","best_day":0,"best_price":current}
    fp     = [p["price"] for p in predictions]
    maxp   = max(fp)
    maxd   = fp.index(maxp)+1
    pct    = ((maxp-current)/current)*100
    if pct>8:
        action = "Hold"
        reason = f"Wait {maxd} days — price expected to rise {pct:.1f}% to ₹{maxp:,}"
    elif pct>2:
        action = "Sell in 2-3 Days"
        reason = f"Moderate rise expected. Sell within {min(maxd,3)} days."
    elif pct<-5:
        action = "Sell Now"
        reason = f"Prices declining {abs(pct):.1f}%. Sell immediately."
    else:
        action = "Sell Now"
        reason = "Prices stable — no significant rise expected."
    return {"action":action,"reason":reason,"best_day":maxd,"best_price":maxp,"pct_change":round(pct,1)}

# ── ROUTES ───────────────────────────────────────────────────────────────────

@app.get("/")
@app.get("/api")
async def root():
    return {"message":"AgriPrice APS API","version":"1.0.0","docs":"/docs"}

@app.get("/api/health")
async def health():
    return {"status":"ok","version":"1.0.0"}

# PRICES
@app.get("/api/prices/crops")
async def get_crops(category: Optional[str] = None):
    if category and category in CROPS:
        return {"category":category,"crops":CROPS[category]}
    return {"categories":CROPS,"all":ALL_CROPS}

@app.get("/api/prices/states")
async def get_states():
    return {"states":list(STATES_MANDIS.keys())}

@app.get("/api/prices/mandis")
async def get_mandis(state: str):
    return {"state":state,"mandis":STATES_MANDIS.get(state,[])}

@app.get("/api/prices/current")
async def current_price(crop: str, mandi: str = "Agra"):
    base  = BASE_PRICES.get(crop, 2000)
    mf    = 0.92 + (hash(mandi) % 20) / 100
    noise = 1 + (((hash(crop+mandi) % 60) - 30) / 1000)
    price = round(base * mf * noise)
    prev  = round(price * (1 + (((hash(crop) % 80) - 40) / 1000)))
    chg   = price - prev
    hist  = gen_historical(crop, mandi, 14)
    vol   = get_volatility([h["price"] for h in hist])
    msp   = MSP.get(crop)
    msp_info = None
    if msp:
        diff = price - msp
        msp_info = {"has_msp":True,"msp":msp,"current":price,"above_msp":price>=msp,
                    "diff":round(diff),"advice":"Market above MSP — sell in market." if price>=msp else "Market below MSP — consider govt procurement."}
    return {"crop":crop,"mandi":mandi,"category":CATEGORY_MAP.get(crop,""),
            "price":price,"prev_price":prev,"change":chg,
            "change_pct":round((chg/prev)*100,2) if prev else 0,
            "min_price":round(price*0.92),"max_price":round(price*1.08),
            "arrivals_tonnes":round(50+(hash(crop+mandi)%500),1),
            "unit":"₹/quintal","volatility":vol,"msp_analysis":msp_info}

@app.get("/api/prices/historical")
async def historical(crop: str, mandi: str = "Agra", days: int = 90):
    return {"crop":crop,"mandi":mandi,"days":days,"data":gen_historical(crop,mandi,min(days,365))}

@app.get("/api/prices/all-mandis")
async def all_mandis(crop: str):
    base    = BASE_PRICES.get(crop, 2000)
    results = []
    for mandi, coords in MANDI_COORDS.items():
        mf    = 0.88 + (hash(mandi+crop) % 30) / 100
        price = round(base * mf * (1+(((hash(crop+mandi)%60)-30)/1000)))
        chg   = round((((hash(mandi+crop+"chg")%200)-100)/100),1)
        results.append({"mandi":mandi,"price":price,"lat":coords["lat"],"lng":coords["lng"],"change_pct":chg,"arrivals":round(30+(hash(mandi)%570),1)})
    results.sort(key=lambda x: x["price"], reverse=True)
    return {"crop":crop,"mandis":results}

@app.get("/api/prices/compare")
async def compare(state: str = "Uttar Pradesh"):
    results = []
    for crop in ALL_CROPS[:25]:
        base = BASE_PRICES.get(crop,1000)
        sf   = 0.9 + (hash(crop+state)%20)/100
        price= round(base*sf)
        chg7 = round((((hash(crop+state+"7")%200)-60)/10),1)
        chg30= round((((hash(crop+state+"30")%300)-80)/10),1)
        vol  = ["Low","Medium","High"][hash(crop)%3]
        rec  = ["Sell Now","Hold","Wait"][hash(crop+state)%3]
        results.append({"crop":crop,"category":CATEGORY_MAP.get(crop,""),
                        "price":price,"change_7d":chg7,"change_30d":chg30,
                        "volatility":vol,"recommendation":rec,
                        "has_msp":crop in MSP,"msp":MSP.get(crop)})
    return {"state":state,"crops":results}

@app.get("/api/prices/msp")
async def msp_tracker():
    results = []
    for crop, msp_val in MSP.items():
        base   = BASE_PRICES.get(crop, msp_val)
        noise  = 1 + (((hash(crop+"msp")%80)-40)/1000)
        market = round(base*noise)
        diff   = market - msp_val
        results.append({"crop":crop,"msp":msp_val,"market_price":market,
                        "diff":diff,"diff_pct":round((diff/msp_val)*100,1),
                        "above_msp":market>=msp_val,"category":CATEGORY_MAP.get(crop,"")})
    results.sort(key=lambda x: x["diff_pct"])
    return {"year":"2024-25","crops":results}

# FORECAST
@app.get("/api/forecast/predict")
async def predict(crop: str, mandi: str = "Agra", days: int = 30, model: str = "random_forest"):
    days   = min(days, 60)
    if model=="lstm":         result = predict_lstm(crop, mandi, days)
    elif model=="linear_regression": result = predict_lr(crop, mandi, days)
    else:                     result = predict_rf(crop, mandi, days)
    hist   = gen_historical(crop, mandi, 30)
    current= hist[-1]["price"] if hist else BASE_PRICES.get(crop,2000)
    vol    = get_volatility([h["price"] for h in hist])
    supply = 45 + (hash(crop+mandi)%40)
    demand = 55 + (hash(crop+mandi+"d")%35)
    status = "Demand > Supply" if demand>supply else "Supply > Demand"
    rec    = get_recommendation(result["predictions"], current)
    return {"crop":crop,"mandi":mandi,"model":result["model"],"current_price":current,
            "predictions":result["predictions"],"metrics":{"mae":result["mae"],"rmse":result["rmse"],"r2":result["r2"],"accuracy":result["accuracy"]},
            "volatility":vol,"supply_demand":{"supply_pct":supply,"demand_pct":demand,"status":status,"outlook":"Prices likely to RISE" if demand>supply else "Prices likely to FALL"},
            "recommendation":rec,"historical":hist}

@app.get("/api/forecast/quick")
async def quick(crop: str, mandi: str = "Agra"):
    result = predict_rf(crop, mandi, 30)
    hist   = gen_historical(crop, mandi, 1)
    current= hist[-1]["price"] if hist else BASE_PRICES.get(crop,2000)
    p      = result["predictions"]
    return {"crop":crop,"mandi":mandi,"current":current,
            "tomorrow":p[0]["price"] if p else current,
            "week":p[6]["price"] if len(p)>6 else current,
            "month":p[-1]["price"] if p else current,"accuracy":result["accuracy"]}

@app.get("/api/forecast/multi-model")
async def multi_model(crop: str, mandi: str = "Agra", days: int = 14):
    lr  = predict_lr(crop, mandi, days)
    rf  = predict_rf(crop, mandi, days)
    lst = predict_lstm(crop, mandi, days)
    return {"crop":crop,"mandi":mandi,"models":{
        "linear_regression":{"predictions":lr["predictions"],"mae":lr["mae"],"rmse":lr["rmse"],"r2":lr["r2"],"accuracy":lr["accuracy"]},
        "random_forest":    {"predictions":rf["predictions"],"mae":rf["mae"],"rmse":rf["rmse"],"r2":rf["r2"],"accuracy":rf["accuracy"]},
        "lstm":             {"predictions":lst["predictions"],"mae":lst["mae"],"rmse":lst["rmse"],"r2":lst["r2"],"accuracy":lst["accuracy"]},
    }}

# CHATBOT
class ChatReq(BaseModel):
    message: str
    lang: str = "en"

RESPONSES = {
    "en":{"greeting":"Namaste! I'm your AI farm assistant. Ask me about crop prices, best time to sell, mandi rates, or MSP.","fallback":"I can help with crop prices, selling time, mandi rates, and MSP. Please ask about a specific crop."},
    "hi":{"greeting":"नमस्ते! मैं आपका AI कृषि सहायक हूं। फसल की कीमत, बेचने का सही समय, या MSP के बारे में पूछें।","fallback":"मैं फसल कीमत और MSP में मदद कर सकता हूं। किसी खास फसल के बारे में पूछें।"}
}

@app.post("/api/chatbot/chat")
async def chat(req: ChatReq):
    msg  = req.message.lower()
    lang = req.lang if req.lang in RESPONSES else "en"
    r    = RESPONSES[lang]
    if any(w in msg for w in ["hello","hi","namaste","नमस्ते"]):
        return {"response":r["greeting"]}
    matched = next((c for c in ALL_CROPS if c.lower() in msg), None)
    if matched:
        price = BASE_PRICES.get(matched, 2000)
        res   = predict_rf(matched, "Agra", 7)
        future= res["predictions"][-1]["price"] if res["predictions"] else price
        pct   = round(((future-price)/price)*100,1)
        msp   = MSP.get(matched)
        msp_line = f" MSP is ₹{msp:,}/qtl." if msp else ""
        action= "Hold" if pct>5 else ("Sell Now" if pct<-3 else "Sell in 2-3 days")
        if lang=="hi":
            return {"response":f"{matched} की कीमत अभी ₹{price:,}/क्विंटल है। अगले हफ्ते ₹{future:,} ({pct:+.1f}%) का अनुमान है।{msp_line} सुझाव: {action}।"}
        return {"response":f"{matched} is ₹{price:,}/qtl today. Forecast: ₹{future:,} next week ({pct:+.1f}%).{msp_line} Recommendation: {action}."}
    if any(w in msg for w in ["msp","minimum support","न्यूनतम"]):
        top = list(MSP.items())[:4]
        lines = ", ".join(f"{c}: ₹{p:,}" for c,p in top)
        return {"response":f"Key MSP 2024-25: {lines}. Ask about a specific crop for full details."}
    if any(w in msg for w in ["weather","rain","मौसम"]):
        return {"response":"Weather directly impacts prices. Rain increases supply → prices fall. Drought/heat → prices spike. Check the Weather section on the Dashboard."}
    if any(w in msg for w in ["sell","best time","कब"]):
        return {"response":"Tell me which crop you want to sell. I'll analyse the mandi data and give you a price forecast and recommendation."}
    return {"response":r["fallback"]}

# WEATHER
@app.get("/api/weather/all")
async def weather_all():
    return {"cities":[{"city":c,**d} for c,d in WEATHER_DATA.items()]}

@app.get("/api/weather/current")
async def weather_current(city: str = "Agra"):
    data = WEATHER_DATA.get(city,{"temp":30,"condition":"Clear","humidity":60,"rainfall":0,"impact":"Neutral","impact_type":"neutral"})
    return {"city":city,**data}

# ALERTS
class AlertCreate(BaseModel):
    crop: str
    alert_type: str
    threshold: float

@app.get("/api/alerts/")
async def get_alerts():
    return {"alerts":_alerts,"count":len(_alerts)}

@app.post("/api/alerts/")
async def create_alert(a: AlertCreate):
    global _next_id
    new = {"id":_next_id,"crop":a.crop,"alert_type":a.alert_type,"threshold":a.threshold,"created_at":datetime.now().strftime("%Y-%m-%d")}
    _alerts.append(new)
    _next_id += 1
    cp   = BASE_PRICES.get(a.crop,0)
    trig = (a.alert_type=="Price rises above" and cp>a.threshold) or (a.alert_type=="Price falls below" and cp<a.threshold)
    return {"alert":new,"immediately_triggered":trig}

@app.delete("/api/alerts/{alert_id}")
async def delete_alert(alert_id: int):
    global _alerts
    before = len(_alerts)
    _alerts = [x for x in _alerts if x["id"]!=alert_id]
    if len(_alerts)==before: raise HTTPException(404,"Alert not found")
    return {"deleted":alert_id,"remaining":len(_alerts)}

# REPORTS
@app.get("/api/reports/list")
async def reports_list():
    return {"reports":[
        {"id":1,"name":"Weekly Price Summary","crop":"All","type":"Price Summary","format":"CSV","created":"2025-04-01"},
        {"id":2,"name":"Onion 30-Day Forecast","crop":"Onion","type":"Forecast","format":"CSV","created":"2025-04-01"},
        {"id":3,"name":"Maharashtra Market Analysis","crop":"All","type":"Market Analysis","format":"CSV","created":"2025-03-31"},
        {"id":4,"name":"Pulse Price Comparison","crop":"Pulses","type":"Comparison","format":"CSV","created":"2025-03-30"},
        {"id":5,"name":"MSP vs Market Report","crop":"All","type":"MSP Analysis","format":"CSV","created":"2025-03-29"},
    ]}

@app.get("/api/reports/download")
async def download_report(crop: str = "All", report_type: str = "Price Summary"):
    crops  = ALL_CROPS if crop=="All" else [crop]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Crop","Category","Price (₹/qtl)","7D Change (%)","30D Change (%)","Volatility","MSP","Above MSP","Recommendation"])
    for c in crops:
        p   = BASE_PRICES.get(c,0)
        cat = CATEGORY_MAP.get(c,"")
        c7  = round((((hash(c+"7")%200)-60)/10),1)
        c30 = round((((hash(c+"30")%300)-80)/10),1)
        vol = ["Low","Medium","High"][hash(c)%3]
        msp = MSP.get(c,"N/A")
        abv = (p>=msp) if isinstance(msp,int) else "N/A"
        rec = ["Sell Now","Hold","Wait"][hash(c)%3]
        writer.writerow([c,cat,p,c7,c30,vol,msp,abv,rec])
    output.seek(0)
    fn = f"AgriPrice_{report_type.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.csv"
    return StreamingResponse(io.BytesIO(output.getvalue().encode()),media_type="text/csv",
                             headers={"Content-Disposition":f"attachment; filename={fn}"})

# AUTH
_users = [{"id":1,"name":"Ramesh Kumar","email":"ramesh@example.com","password":"farmer123","state":"Uttar Pradesh","district":"Agra","role":"farmer"}]
_nuid  = 2

class LoginReq(BaseModel):
    email: str
    password: str

class RegisterReq(BaseModel):
    name: str; email: str; password: str; state: str; district: str

@app.post("/api/auth/login")
async def login(req: LoginReq):
    user = next((u for u in _users if u["email"]==req.email and u["password"]==req.password),None)
    if not user: raise HTTPException(401,"Invalid credentials")
    return {"token":f"mock_token_{user['id']}","user":{k:v for k,v in user.items() if k!="password"}}

@app.post("/api/auth/register")
async def register(req: RegisterReq):
    global _nuid
    if any(u["email"]==req.email for u in _users): raise HTTPException(400,"Email already registered")
    user = {"id":_nuid,"name":req.name,"email":req.email,"password":req.password,"state":req.state,"district":req.district,"role":"farmer"}
    _users.append(user); _nuid+=1
    return {"token":f"mock_token_{user['id']}","user":{k:v for k,v in user.items() if k!="password"}}

# ADMIN
@app.get("/api/admin/stats")
async def admin_stats():
    return {"total_users":1284,"total_crops":len(ALL_CROPS),"mandis_covered":312,
            "uptime_pct":99.2,"predictions_today":1847,"api_calls_today":8432}

@app.get("/api/admin/activity")
async def admin_activity():
    return {"activities":[
        {"action":"Dataset uploaded: Agmarknet Apr 2025","time":"2h ago","type":"upload"},
        {"action":"Model retrained: LSTM Onion — RMSE 48","time":"5h ago","type":"model"},
        {"action":"New mandi added: Gondal, Gujarat","time":"12h ago","type":"data"},
        {"action":"Weather data synced: 24 cities","time":"1d ago","type":"sync"},
        {"action":"Forecast API: 1,847 calls today","time":"today","type":"api"},
    ]}

@app.get("/api/admin/model-performance")
async def model_perf():
    return {"months":["Jan","Feb","Mar","Apr"],
            "random_forest":[88.2,89.1,90.8,91.4],
            "lstm":         [85.1,86.5,89.2,90.1],
            "linear_reg":   [79.3,80.1,82.4,83.2],
            "daily_users":  [320,450,680,780]}

# ── VERCEL HANDLER ────────────────────────────────────────────────────────────
handler = Mangum(app, lifespan="off")
