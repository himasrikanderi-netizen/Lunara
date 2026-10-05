from dataclasses import dataclass
from datetime import datetime, timezone
from math import exp

@dataclass(frozen=True)
class SegmentSignals:
    incident_severity:float=0; incident_age_days:float=365; report_reliability:float=.5
    lighting:float=.5; visibility:float=.5; isolation:float=.5; safe_place_proximity:float=.5
    public_activity:float=.5; transport_access:float=.5; hotspot:float=0; data_coverage:float=.5

def incident_decay(age_days:float, half_life_days:float=45)->float:
    return exp(-max(0,age_days)*0.693147/half_life_days)

def score_segment(s:SegmentSignals,arrival:datetime)->tuple[int,list[str]]:
    hour=arrival.astimezone(timezone.utc).hour
    night=1.0 if hour>=20 or hour<6 else .2
    incident=s.incident_severity*s.report_reliability*incident_decay(s.incident_age_days)
    environmental=((1-s.lighting)*.16+(1-s.visibility)*.10+s.isolation*.16+(1-s.public_activity)*.11)*night
    support=(s.safe_place_proximity*.08+s.transport_access*.06)
    risk=min(1,incident*.34+environmental+s.hotspot*.18-support)
    score=round(max(5,min(98,100*(1-risk))))
    factors=[]
    if s.lighting>=.7:factors.append("Better lighting coverage")
    if s.public_activity>=.7:factors.append("Active public area")
    if s.safe_place_proximity>=.7:factors.append("Safe places nearby")
    if incident>.25:factors.append("Recent reliable reports nearby")
    if s.isolation>.65:factors.append("More isolated road segment")
    return score,factors or ["Limited neutral safety context"]

def confidence_score(signals:list[SegmentSignals],freshness:float=.75,consistency:float=.8)->int:
    if not signals:return 0
    coverage=sum(s.data_coverage for s in signals)/len(signals)
    reliability=sum(s.report_reliability for s in signals)/len(signals)
    return round(100*(coverage*.4+freshness*.25+reliability*.2+consistency*.15))

def label_confidence(score:int)->str:
    return "High" if score>=75 else "Medium" if score>=45 else "Low"
