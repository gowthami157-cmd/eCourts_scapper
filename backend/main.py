from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime, timedelta

from services.ecourts_scraper import ECourtsScraper
from services.database import Database

app = FastAPI(title="eCourts Scraper API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scraper = ECourtsScraper()
db = Database()

class CaseSearchByCNR(BaseModel):
    cnr: str
    state_code: Optional[str] = None
    district_code: Optional[str] = None

class CaseSearchByDetails(BaseModel):
    state_code: str
    district_code: str
    court_code: str
    case_type: str
    case_number: str
    case_year: str

class CauseListRequest(BaseModel):
    state_code: str
    district_code: str
    court_complex_code: str
    court_code: Optional[str] = None
    court_name: Optional[str] = None
    cause_type: str = "civ"
    captcha_code: str
    date: str

@app.get("/")
async def root():
    return {
        "message": "eCourts Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "states": "/api/states",
            "districts": "/api/districts/{state_code}",
            "court_complexes": "/api/court-complexes/{state_code}/{district_code}",
            "courts": "/api/courts/{state_code}/{district_code}/{complex_code}",
            "search_cnr": "/api/search/cnr",
            "search_case": "/api/search/case",
            "cause_list": "/api/cause-list",
            "download_pdf": "/api/download/pdf"
        }
    }

@app.get("/api/states")
async def get_states():
    try:
        states = await scraper.fetch_states()
        await db.cache_states(states)
        return {"success": True, "data": states}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/districts/{state_code}")
async def get_districts(state_code: str):
    try:
        districts = await scraper.fetch_districts(state_code)
        await db.cache_districts(state_code, districts)
        return {"success": True, "data": districts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/court-complexes/{state_code}/{district_code}")
async def get_court_complexes(state_code: str, district_code: str):
    try:
        complexes = await scraper.fetch_court_complexes(state_code, district_code)
        await db.cache_court_complexes(state_code, district_code, complexes)
        return {"success": True, "data": complexes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/courts/{state_code}/{district_code}/{complex_code}")
async def get_courts(state_code: str, district_code: str, complex_code: str):
    try:
        courts = await scraper.fetch_courts(state_code, district_code, complex_code)
        await db.cache_courts(state_code, district_code, complex_code, courts)
        return {"success": True, "data": courts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search/cnr")
async def search_by_cnr(request: CaseSearchByCNR):
    try:
        result = await scraper.search_case_by_cnr(
            request.cnr,
            request.state_code,
            request.district_code
        )

        if result:
            await db.save_search_result(result)

        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search/case")
async def search_by_case_details(request: CaseSearchByDetails):
    try:
        result = await scraper.search_case_by_details(
            request.state_code,
            request.district_code,
            request.court_code,
            request.case_type,
            request.case_number,
            request.case_year
        )

        if result:
            await db.save_search_result(result)

        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cause-list")
async def get_cause_list(request: CauseListRequest):
    try:
        cause_list = await scraper.fetch_cause_list(
            request.state_code,
            request.district_code,
            request.court_complex_code,
            request.court_code,
            request.date,
            request.captcha_code,
            request.cause_type,
            request.court_name
        )

        if cause_list and cause_list.get("cases"):
            await db.save_cause_list(cause_list)

        return {"success": True, "data": cause_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cause-list/captcha")
async def get_cause_list_captcha():
    try:
        captcha = await scraper.fetch_cause_list_captcha()
        if not captcha:
            raise HTTPException(status_code=503, detail="Unable to retrieve captcha at this time.")
        return {"success": True, "data": captcha}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/pdf")
async def download_pdf(
    state_code: str = Query(...),
    district_code: str = Query(...),
    court_complex_code: str = Query(...),
    court_code: Optional[str] = Query(None),
    date: str = Query(...)
):
    try:
        pdf_path = await scraper.download_cause_list_pdf(
            state_code,
            district_code,
            court_complex_code,
            court_code,
            date
        )

        if pdf_path and os.path.exists(pdf_path):
            return FileResponse(
                pdf_path,
                media_type="application/pdf",
                filename=os.path.basename(pdf_path)
            )
        else:
            raise HTTPException(status_code=404, detail="PDF not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
