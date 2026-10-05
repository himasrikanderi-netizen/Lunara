import logging,time
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.models import JourneyCreate,Report,ReportCreate,RouteOption,RouteSearch,VerificationCreate,SafePlaceResults
from app.services.reports import ReportService
from app.services.routing import RoutingService
from app.services.providers import ProviderError
from app.services.safe_places import SafePlaceService

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s %(message)s",level=logging.INFO)
log=logging.getLogger("lunara");settings=get_settings();routing=RoutingService(settings);reports=ReportService();safe_place_search=SafePlaceService(settings)
@asynccontextmanager
async def lifespan(_:FastAPI):log.info("Lunara API started environment=%s",settings.environment);yield;log.info("Lunara API stopped")
app=FastAPI(title=settings.app_name,version="0.1.0",lifespan=lifespan,docs_url="/docs" if settings.environment!="production" else None)
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=False,allow_methods=["GET","POST","DELETE"],allow_headers=["Authorization","Content-Type"])
@app.middleware("http")
async def request_log(request:Request,call_next):
    start=time.perf_counter();response=await call_next(request);log.info("request method=%s path=%s status=%s duration_ms=%d",request.method,request.url.path,response.status_code,(time.perf_counter()-start)*1000);return response
@app.exception_handler(ValueError)
async def invalid(_:Request,exc:ValueError):return JSONResponse(status_code=422,content={"detail":str(exc)})
@app.get("/health")
def health():return {"status":"ok","service":"lunara-api"}
@app.post("/api/v1/routes/search",response_model=list[RouteOption])
def route_search(query:RouteSearch):
    try:
        return routing.search(query)
    except ProviderError as exc:
        raise HTTPException(503,str(exc)) from exc
@app.post("/api/v1/reports",response_model=Report,status_code=201)
def create_report(report:ReportCreate):return reports.create(report)
@app.get("/api/v1/reports/nearby",response_model=list[Report])
def nearby_reports(lat:float,lng:float,radius_m:int=1000):
    if not 50<=radius_m<=5000:raise HTTPException(422,"radius_m must be 50–5000")
    return reports.nearby(lat,lng,radius_m)
@app.post("/api/v1/reports/{report_id}/verify",response_model=Report)
def verify(report_id:str,data:VerificationCreate):
    try:return reports.verify(report_id,data.verdict)
    except KeyError:raise HTTPException(404,"Report not found")
@app.post("/api/v1/journeys",status_code=201)
def create_journey(data:JourneyCreate):raise HTTPException(501,"Server-side journey tracking is not configured. Use the browser's static route sharing link.")
@app.post("/api/v1/journeys/{journey_id}/recalculate")
def recalculate(journey_id:str):raise HTTPException(501,"Live journey recalculation is not configured")
@app.get("/api/v1/safe-places/nearby")
def safe_places(lat:float,lng:float,category:str,radius_m:int=5000)->SafePlaceResults:
    try:
        places,source=safe_place_search.nearby(lat,lng,category,radius_m)
        return SafePlaceResults(places=places,source=source,data_status="Mapped search results only; the list may be incomplete and opening hours, staffing and availability are not verified" if places else "No mapped places found within the selected radius")
    except ProviderError as exc:
        raise HTTPException(503,str(exc)) from exc
