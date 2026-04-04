# AgriPrice Forecasting System (APS) 🌾

AI/ML-powered agricultural price forecasting system for Indian farmers.

---

## Project Structure

```
APS/
├── backend/
│   ├── main.py              ← FastAPI app entry point
│   ├── requirements.txt     ← Python dependencies
│   ├── routers/
│   │   ├── prices.py        ← Price & historical data APIs
│   │   ├── forecast.py      ← ML prediction APIs
│   │   ├── chatbot.py       ← AI assistant API
│   │   ├── weather.py       ← Weather data API
│   │   ├── alerts.py        ← Price alerts CRUD
│   │   ├── reports.py       ← CSV report download
│   │   ├── auth.py          ← User login/register
│   │   └── admin.py         ← Admin stats & activity
│   ├── ml/
│   │   └── engine.py        ← Linear Regression, Random Forest, LSTM engines
│   ├── data/
│   │   └── master.py        ← All crops, states, mandis, MSP data
│   └── models/
│       └── database.py      ← SQLAlchemy DB models
└── frontend/
    └── index.html           ← Complete frontend (single file)
```

---

## Setup & Run

### Step 1 — Install Python dependencies

```bash
cd APS/backend
pip install -r requirements.txt
```

### Step 2 — Start the backend

```bash
python main.py
```

Backend runs at: **http://localhost:8000**
API docs at: **http://localhost:8000/docs**

### Step 3 — Open the frontend

Open `APS/frontend/index.html` directly in your browser.

> The frontend automatically connects to `http://localhost:8000/api`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/prices/current?crop=Onion&mandi=Agra` | Current price + volatility |
| GET | `/api/prices/historical?crop=Onion&days=90` | Historical price data |
| GET | `/api/prices/all-mandis?crop=Onion` | All mandi prices (for map) |
| GET | `/api/prices/compare?state=UP` | All crops comparison table |
| GET | `/api/prices/msp` | MSP tracker for all crops |
| GET | `/api/prices/crops` | All crops by category |
| GET | `/api/prices/states` | All states |
| GET | `/api/prices/mandis?state=UP` | Mandis for a state |
| GET | `/api/forecast/predict?crop=Onion&model=random_forest&days=30` | ML price prediction |
| GET | `/api/forecast/quick?crop=Onion` | 1/7/30 day quick forecast |
| GET | `/api/forecast/multi-model?crop=Onion` | Compare all 3 models |
| POST | `/api/chatbot/chat` | `{"message":"...", "lang":"en"}` |
| GET | `/api/weather/all` | Weather for all cities |
| GET | `/api/alerts/` | List alerts |
| POST | `/api/alerts/` | Create alert |
| DELETE | `/api/alerts/{id}` | Delete alert |
| GET | `/api/reports/download?crop=All` | Download CSV report |
| POST | `/api/auth/login` | `{"email":"...","password":"..."}` |
| POST | `/api/auth/register` | Register new user |
| GET | `/api/admin/stats` | System statistics |

---

## ML Models

| Model | MAE | RMSE | R² | Best For |
|-------|-----|------|----|----------|
| Linear Regression | ~40 | ~52 | 0.78 | Stable trends |
| Random Forest | ~35 | ~45 | 0.89 | Short-term (7-14 days) |
| LSTM | ~28 | ~38 | 0.92 | Long-term (30 days) |

---

## Features

- ✅ 95+ crops (Vegetables, Fruits, Pulses, Spices, Cereals)
- ✅ All 28 states + 8 UTs with their mandis
- ✅ 3 ML models: Linear Regression, Random Forest, LSTM
- ✅ Real-time price simulation with seasonal factors
- ✅ Interactive Leaflet.js mandi map
- ✅ AI chatbot (Hindi + English)
- ✅ Profit calculator
- ✅ MSP tracker with visual comparison
- ✅ Price alerts (add/remove)
- ✅ CSV report download (real download)
- ✅ Supply-demand indicator
- ✅ Weather impact analysis
- ✅ Admin dashboard with model metrics
- ✅ User auth (login/register)
- ✅ MAE / RMSE / R² model evaluation metrics
- ✅ Dark theme, responsive, mobile-friendly

---

## Default Login

```
Email:    ramesh@example.com
Password: farmer123
```

---

## To Connect Real Data (Production)

1. Replace `engine.py` price generators with actual **Agmarknet API** calls
2. Connect **OpenWeatherMap API** in `weather.py`
3. Connect **NewsAPI** for live agri news
4. Replace SQLite with **PostgreSQL**: set `DATABASE_URL` env var
5. Add **Groq/OpenAI** key in `chatbot.py` for LLM responses

---

## Tech Stack

- **Backend**: FastAPI + Python
- **ML**: Custom Linear Regression, Random Forest, LSTM (pure Python, no sklearn needed to run)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: Vanilla HTML/CSS/JS + Chart.js + Leaflet.js
- **Fonts**: Sora + JetBrains Mono
