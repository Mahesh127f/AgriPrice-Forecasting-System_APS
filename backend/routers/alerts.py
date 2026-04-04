from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from data.master import BASE_PRICES

router = APIRouter()

_store = [
    {"id":1,"crop":"Onion","alert_type":"Price rises above","threshold":2500,"is_active":True,"triggered":False,"created_at":"2025-04-01"},
    {"id":2,"crop":"Tomato","alert_type":"Price falls below","threshold":1500,"is_active":True,"triggered":False,"created_at":"2025-04-01"},
    {"id":3,"crop":"Potato","alert_type":"Price changes by","threshold":200,"is_active":True,"triggered":False,"created_at":"2025-03-31"},
]
_nid = 4

class AlertCreate(BaseModel):
    crop: str
    alert_type: str
    threshold: float

@router.get("/")
async def get_alerts():
    return {"alerts": _store, "count": len(_store)}

@router.post("/")
async def create_alert(a: AlertCreate):
    global _nid
    new = {"id":_nid,"crop":a.crop,"alert_type":a.alert_type,"threshold":a.threshold,
           "is_active":True,"triggered":False,"created_at":datetime.now().strftime("%Y-%m-%d")}
    _store.append(new)
    _nid += 1
    cp = BASE_PRICES.get(a.crop, 0)
    trig = (a.alert_type=="Price rises above" and cp>a.threshold) or (a.alert_type=="Price falls below" and cp<a.threshold)
    return {"alert": new, "immediately_triggered": trig}

@router.delete("/{alert_id}")
async def delete_alert(alert_id: int):
    global _store
    before = len(_store)
    _store = [x for x in _store if x["id"]!=alert_id]
    if len(_store)==before:
        raise HTTPException(404,"Alert not found")
    return {"deleted": alert_id, "remaining": len(_store)}
