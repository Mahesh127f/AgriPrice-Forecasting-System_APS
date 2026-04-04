from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from datetime import datetime
from data.master import ALL_CROPS, BASE_PRICES, MSP_2024_25, CATEGORY_MAP
import random, io, csv

router = APIRouter()

@router.get("/list")
async def list_reports():
    return {"reports": [
        {"id":1,"name":"Weekly Price Summary","crop":"All","type":"Price Summary","format":"CSV","created":"2025-04-01"},
        {"id":2,"name":"Onion 30-Day Forecast","crop":"Onion","type":"Forecast","format":"CSV","created":"2025-04-01"},
        {"id":3,"name":"Maharashtra Market Analysis","crop":"All","type":"Market Analysis","format":"CSV","created":"2025-03-31"},
        {"id":4,"name":"Pulse Price Comparison","crop":"Pulses","type":"Comparison","format":"CSV","created":"2025-03-30"},
        {"id":5,"name":"MSP vs Market Report","crop":"All","type":"MSP Analysis","format":"CSV","created":"2025-03-29"},
    ]}

@router.get("/download")
async def download_report(crop: str = "All", report_type: str = "Price Summary"):
    crops = ALL_CROPS if crop == "All" else [crop]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Crop","Category","Price (₹/qtl)","7D Change (%)","30D Change (%)","Volatility","MSP","Above MSP","Recommendation"])
    for c in crops:
        p   = BASE_PRICES.get(c, 0)
        cat = CATEGORY_MAP.get(c, "")
        c7  = round(random.gauss(3, 8), 1)
        c30 = round(random.gauss(5, 14), 1)
        vol = ["Low","Medium","High"][hash(c) % 3]
        msp = MSP_2024_25.get(c, "N/A")
        abv = (p >= msp) if isinstance(msp, int) else "N/A"
        rec = ["Sell Now","Hold","Wait"][hash(c) % 3]
        writer.writerow([c, cat, p, c7, c30, vol, msp, abv, rec])
    output.seek(0)
    fn = f"AgriPrice_{report_type.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.csv"
    return StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename={fn}"})
