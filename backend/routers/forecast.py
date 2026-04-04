from fastapi import APIRouter, Query
from ml.engine import (
    predict_linear_regression, predict_random_forest, predict_lstm,
    get_supply_demand, get_recommendation, get_volatility, generate_historical
)
from data.master import BASE_PRICES

router = APIRouter()

@router.get("/predict")
async def predict(crop: str, mandi: str = "Agra", days: int = 30, model: str = "random_forest"):
    days = min(days, 60)
    if model == "lstm":
        result = predict_lstm(crop, mandi, days)
    elif model == "linear_regression":
        result = predict_linear_regression(crop, mandi, days)
    else:
        result = predict_random_forest(crop, mandi, days)

    hist = generate_historical(crop, mandi, 30)
    current_price = hist[-1]["price"] if hist else BASE_PRICES.get(crop, 2000)
    hist_prices = [h["price"] for h in hist]
    volatility = get_volatility(crop, hist_prices)
    supply_demand = get_supply_demand(crop, mandi)
    recommendation = get_recommendation(crop, result["predictions"], current_price)

    return {
        "crop": crop, "mandi": mandi, "model": result["model"],
        "current_price": current_price,
        "predictions": result["predictions"],
        "metrics": {
            "mae": result["mae"], "rmse": result["rmse"],
            "r2": result["r2"], "accuracy": result["accuracy"]
        },
        "volatility": volatility,
        "supply_demand": supply_demand,
        "recommendation": recommendation,
        "historical": hist
    }

@router.get("/quick")
async def quick_forecast(crop: str, mandi: str = "Agra"):
    result = predict_random_forest(crop, mandi, 30)
    hist = generate_historical(crop, mandi, 7)
    current = hist[-1]["price"] if hist else BASE_PRICES.get(crop, 2000)
    preds = result["predictions"]
    return {
        "crop": crop, "mandi": mandi,
        "current": current,
        "tomorrow": preds[0]["price"] if preds else current,
        "week": preds[6]["price"] if len(preds) > 6 else current,
        "month": preds[-1]["price"] if preds else current,
        "accuracy": result["accuracy"]
    }

@router.get("/multi-model")
async def multi_model_compare(crop: str, mandi: str = "Agra", days: int = 14):
    lr  = predict_linear_regression(crop, mandi, days)
    rf  = predict_random_forest(crop, mandi, days)
    lst = predict_lstm(crop, mandi, days)
    return {
        "crop": crop, "mandi": mandi,
        "models": {
            "linear_regression": {"predictions": lr["predictions"], "mae": lr["mae"], "rmse": lr["rmse"], "r2": lr["r2"], "accuracy": lr["accuracy"]},
            "random_forest":     {"predictions": rf["predictions"], "mae": rf["mae"], "rmse": rf["rmse"], "r2": rf["r2"], "accuracy": rf["accuracy"]},
            "lstm":              {"predictions": lst["predictions"],"mae": lst["mae"],"rmse": lst["rmse"],"r2": lst["r2"], "accuracy": lst["accuracy"]}
        }
    }
