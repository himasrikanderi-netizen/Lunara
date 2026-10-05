from datetime import datetime,timezone
from app.services.scoring import SegmentSignals,confidence_score,incident_decay,score_segment
def test_incident_decay_reduces_old_incidents():assert incident_decay(90)<incident_decay(2)
def test_better_environment_scores_higher():
    time=datetime(2026,1,1,22,tzinfo=timezone.utc)
    safer=SegmentSignals(lighting=.9,visibility=.9,isolation=.1,public_activity=.9,safe_place_proximity=.9)
    riskier=SegmentSignals(lighting=.1,visibility=.2,isolation=.9,public_activity=.1,safe_place_proximity=.1)
    assert score_segment(safer,time)[0]>score_segment(riskier,time)[0]
def test_confidence_is_separate_and_bounded():assert 0<=confidence_score([SegmentSignals(data_coverage=.8)])<=100
