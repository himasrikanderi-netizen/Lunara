from fastapi.testclient import TestClient
from app.config import Settings
from app.main import app
from app.models import Coordinate
from app.services.providers import Geocoder

class Response:
    def __init__(self,payload):self.payload=payload
    def raise_for_status(self):pass
    def json(self):return self.payload

class FakeClient:
    def __init__(self):self.calls=[]
    def get(self,url,**kwargs):
        self.calls.append((url,kwargs))
        if url.endswith("/reverse"):
            return Response({"display_name":"Secunderabad Junction, Hyderabad","name":"Secunderabad Junction"})
        return Response([{"display_name":"Secunderabad Junction, Hyderabad","name":"Secunderabad Junction","lat":"17.4338591","lon":"78.502051"}])

def test_search_and_reverse_preserve_exact_map_point(monkeypatch):
    fake=FakeClient()
    geocoder=Geocoder(Settings(),fake)
    from app import main
    monkeypatch.setattr(main,"place_search",geocoder)
    client=TestClient(app)
    result=client.get("/api/v1/places/search",params={"q":"Secunderabad railway station"})
    assert result.status_code==200
    assert result.json()[0]["location"]=={"lat":17.4338591,"lng":78.502051}
    reverse=client.get("/api/v1/places/reverse",params={"lat":17.43,"lng":78.50})
    assert reverse.status_code==200
    assert reverse.json()["name"]=="Secunderabad Junction"
    assert reverse.json()["location"]=={"lat":17.43,"lng":78.50}
    assert fake.calls[0][0].endswith("/search")
    assert fake.calls[1][0].endswith("/reverse")
    assert geocoder.reverse(Coordinate(lat=17.43,lng=78.50)).location==Coordinate(lat=17.43,lng=78.50)
    assert len(fake.calls)==2

def test_short_search_rejected():
    response=TestClient(app).get("/api/v1/places/search",params={"q":"a"})
    assert response.status_code==422
