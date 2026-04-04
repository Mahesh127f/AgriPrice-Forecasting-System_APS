from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

from routers import prices, forecast, chatbot, weather, alerts, reports, auth, admin

app = FastAPI(
    title="AgriPrice Forecasting System (APS)",
    description="AI/ML powered agricultural price forecasting for Indian farmers",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,     prefix="/api/auth",     tags=["Auth"])
app.include_router(prices.router,   prefix="/api/prices",   tags=["Prices"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["Forecast"])
app.include_router(chatbot.router,  prefix="/api/chatbot",  tags=["Chatbot"])
app.include_router(weather.router,  prefix="/api/weather",  tags=["Weather"])
app.include_router(alerts.router,   prefix="/api/alerts",   tags=["Alerts"])
app.include_router(reports.router,  prefix="/api/reports",  tags=["Reports"])
app.include_router(admin.router,    prefix="/api/admin",    tags=["Admin"])

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def root():
    index = os.path.join(frontend_path, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"message": "AgriPrice APS API running", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
