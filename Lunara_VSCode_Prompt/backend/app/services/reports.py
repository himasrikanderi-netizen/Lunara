from datetime import datetime,timezone
from math import asin,cos,radians,sin,sqrt
from uuid import uuid4
from app.models import Report,ReportCreate

def distance_m(a:tuple[float,float],b:tuple[float,float])->float:
    p1,p2=radians(a[0]),radians(b[0]);dp=radians(b[0]-a[0]);dl=radians(b[1]-a[1]);h=sin(dp/2)**2+cos(p1)*cos(p2)*sin(dl/2)**2;return 12742000*asin(sqrt(h))

class ReportService:
    def __init__(self):self.reports:list[Report]=[]
    def create(self,data:ReportCreate)->Report:
        now=datetime.now(timezone.utc); age=abs((now-data.occurred_at).total_seconds())
        if age>365*86400:raise ValueError("Reports must relate to the last year")
        duplicate=any(r.category==data.category and distance_m((r.latitude,r.longitude),(data.latitude,data.longitude))<100 and abs((r.occurred_at-data.occurred_at).total_seconds())<3600 for r in self.reports)
        report=Report(**data.model_dump(),id=str(uuid4()),status="possible_duplicate" if duplicate else "pending",reliability_score=20 if duplicate else 35)
        self.reports.insert(0,report);return report
    def nearby(self,lat:float,lng:float,radius_m:int)->list[Report]:
        return [r for r in self.reports if distance_m((lat,lng),(r.latitude,r.longitude))<=radius_m]
    def verify(self,report_id:str,verdict:str)->Report:
        report=next((r for r in self.reports if r.id==report_id),None)
        if not report:raise KeyError(report_id)
        if verdict=="still_relevant":report.reliability_score=min(95,report.reliability_score+10)
        elif verdict=="duplicate_inaccurate":report.reliability_score=max(5,report.reliability_score-12)
        else:report.status="resolved"
        return report
