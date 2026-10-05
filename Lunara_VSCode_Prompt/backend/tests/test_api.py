from datetime import datetime,timezone
from fastapi.testclient import TestClient
from app.main import app
from app.models import Coordinate, TravelMode
from app.services.routing import RoutingService
from app.config import Settings
import pytest
client=TestClient(app)
def test_health():assert client.get("/health").json()["status"]=="ok"
def test_current_location_placeholder_never_calls_nominatim():
    from app.services.providers import Geocoder
    class FailClient:
        def get(self, *args, **kwargs):
            raise AssertionError("Nominatim must not receive the placeholder")
    geocoder=Geocoder(Settings(),FailClient())
    try:
        geocoder.locate("Current location")
        assert False, "placeholder must be rejected"
    except ValueError as exc:
        assert "browser coordinates" in str(exc)
    assert geocoder.locate("17.411568, 78.527463")==Coordinate(lat=17.411568,lng=78.527463)
def test_search_returns_real_provider_geometry_contract(monkeypatch):
    class Geocoder:
        def locate(self, place):
            return Coordinate(lat=12.97,lng=77.57) if place=="Origin" else Coordinate(lat=12.98,lng=77.60)
    class Router:
        def routes(self, points, mode, alternatives=True):
            assert mode == TravelMode.driving
            def route(offset, duration):
                return {"duration":duration,"distance":4200+offset*100,"geometry":{"coordinates":[[77.57,12.97],[77.58,12.975+offset*.001],[77.60,12.98]]},"legs":[{"steps":[{"name":"Main Road" if offset else "","distance":4200}]}]}
            return [route(0,1800),route(1,1950),route(2,2100)]
    from app import main
    monkeypatch.setattr(main,"routing",RoutingService(Settings(),Geocoder(),Router()))
    r=client.post("/api/v1/routes/search",json={"origin":"Origin","destination":"Destination","departure_time":datetime.now(timezone.utc).isoformat(),"preference":0,"travel_mode":"driving"})
    assert r.status_code==200
    assert {x["label"] for x in r.json()}=={"Safest","Balanced","Fastest"}
    assert all(x["geometry_source"]=="OpenStreetMap via OSRM" for x in r.json())
    assert all("historical incidents" in x["unavailable_factors"] for x in r.json())
    assert all(x["travel_mode"]=="driving" and x["traffic_included"] is False for x in r.json())
    assert all(x["resolved_origin"]=={"lat":12.97,"lng":77.57} for x in r.json())
def test_osrm_mode_selects_car_graph_not_foot_graph():
    from app.services.providers import OSRMRouter
    class Response:
        def raise_for_status(self): pass
        def json(self): return {"code":"Ok","routes":[{"duration":10,"distance":100,"geometry":{"coordinates":[[78.5,17.4],[78.51,17.41]]}}]}
    class Client:
        url=""
        def get(self,url,**kwargs): self.url=url; return Response()
    fake=Client();router=OSRMRouter(Settings(),fake)
    router.routes([Coordinate(lat=17.4,lng=78.5),Coordinate(lat=17.41,lng=78.51)],TravelMode.driving)
    assert "/routed-car/route/v1/driving/" in fake.url
    router.routes([Coordinate(lat=17.4,lng=78.5),Coordinate(lat=17.41,lng=78.51)],TravelMode.walking)
    assert "/routed-foot/route/v1/driving/" in fake.url
def test_geometry_must_end_near_requested_locations():
    from app.services.routing import _validate_route
    from app.services.providers import ProviderError
    bad={"distance":5000,"duration":900,"geometry":{"coordinates":[[78.527463,17.411568],[78.900000,17.900000]]}}
    try:
        _validate_route(bad,Coordinate(lat=17.411568,lng=78.527463),Coordinate(lat=17.433859,lng=78.502051))
        assert False, "a route ending far from the destination must not be scored"
    except ProviderError as exc:
        assert "endpoint" in str(exc)

@pytest.mark.parametrize("selected,profile",[
    ("driving",TravelMode.driving),("walking",TravelMode.walking),("cycling",TravelMode.cycling),
    ("rapido_bike",TravelMode.driving),("rapido_auto",TravelMode.driving),("rapido_cab",TravelMode.driving),
])
def test_all_six_modes_preserve_endpoints_and_use_supported_profile(selected,profile,monkeypatch):
    class Geocoder:
        def locate(self,place):
            return Coordinate(lat=17.411568,lng=78.527463) if place=="Origin" else Coordinate(lat=17.433859,lng=78.502051)
    class Router:
        modes=[]
        def routes(self,points,mode,alternatives=True):
            self.modes.append(mode)
            return [{"duration":600+index*90,"distance":5000+index*200,
                     "geometry":{"coordinates":[[78.527463,17.411568],[78.515+index*.001,17.42],[78.502051,17.433859]]},
                     "legs":[{"steps":[{"name":"Main Road","distance":5000}]}]} for index in range(3)]
    router=Router()
    from app import main
    monkeypatch.setattr(main,"routing",RoutingService(Settings(),Geocoder(),router))
    response=client.post("/api/v1/routes/search",json={"origin":"Origin","destination":"Destination","departure_time":datetime.now(timezone.utc).isoformat(),"preference":50,"travel_mode":selected})
    assert response.status_code==200
    assert router.modes==[profile]
    assert all(item["travel_mode"]==selected and item["routing_profile"]==profile.value for item in response.json())
    assert all(item["resolved_origin"]=={"lat":17.411568,"lng":78.527463} and item["resolved_destination"]=={"lat":17.433859,"lng":78.502051} for item in response.json())
    if selected.startswith("rapido_"):
        assert all("Rapido fare" in item["unavailable_factors"] for item in response.json())
def test_report_and_verify():
    payload={"category":"poor_lighting","severity":3,"latitude":12.97,"longitude":77.59,"occurred_at":datetime.now(timezone.utc).isoformat()}
    made=client.post("/api/v1/reports",json=payload);assert made.status_code==201
    checked=client.post(f"/api/v1/reports/{made.json()['id']}/verify",json={"verdict":"still_relevant"});assert checked.json()["reliability_score"]>made.json()["reliability_score"]
