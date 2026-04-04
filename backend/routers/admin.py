from fastapi import APIRouter
from data.master import ALL_CROPS

router = APIRouter()

@router.get("/stats")
async def stats():
    return {"total_users":1284,"total_crops":len(ALL_CROPS),"mandis_covered":312,
            "uptime_pct":99.2,"predictions_today":1847,"api_calls_today":8432,
            "active_alerts":147,"datasets_count":24}

@router.get("/activity")
async def activity():
    return {"activities":[
        {"action":"Dataset uploaded: Agmarknet Apr 2025","time":"2h ago","type":"upload"},
        {"action":"Model retrained: LSTM Onion — RMSE 48","time":"5h ago","type":"model"},
        {"action":"New mandi added: Gondal, Gujarat","time":"12h ago","type":"data"},
        {"action":"Weather data synced: 24 cities","time":"1d ago","type":"sync"},
        {"action":"Admin approved 3 new users","time":"1d ago","type":"admin"},
        {"action":"Report generated: Maharashtra analysis","time":"2d ago","type":"report"},
        {"action":"Forecast API: 1,847 calls today","time":"today","type":"api"},
    ]}

@router.get("/model-performance")
async def model_performance():
    return {"months":["Jan","Feb","Mar","Apr"],
            "random_forest":[88.2,89.1,90.8,91.4],
            "lstm":         [85.1,86.5,89.2,90.1],
            "linear_reg":   [79.3,80.1,82.4,83.2],
            "daily_users":  [320,450,680,780]}
