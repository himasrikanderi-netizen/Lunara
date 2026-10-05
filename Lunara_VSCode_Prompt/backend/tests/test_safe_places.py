from fastapi.testclient import TestClient
from app.main import app
from app.models import Coordinate, SafePlace
from app.services.safe_places import SafePlaceService
from app.config import Settings
import pytest

@pytest.mark.parametrize("category",["hospital","police","transport"])
def test_nearby_places_are_real_mapped_results(category,monkeypatch):
    place=SafePlace(id="node/123",category=category,name="Mapped place",
        location=Coordinate(lat=17.42,lng=78.52),distance_m=1200,
        osm_url="https://www.openstreetmap.org/node/123")
    from app import main
    class Search:
        def nearby(self,lat,lng,selected,radius_m):
            assert (lat,lng,selected,radius_m)==(17.411568,78.527463,category,5000)
            return [place],"OpenStreetMap via Nominatim"
    monkeypatch.setattr(main,"safe_place_search",Search())
    response=TestClient(app).get("/api/v1/safe-places/nearby",params={
        "lat":17.411568,"lng":78.527463,"category":category})
    assert response.status_code==200
    assert response.json()["places"][0]["name"]=="Mapped place"
    assert response.json()["source"]=="OpenStreetMap via Nominatim"

def test_invalid_nearby_category_is_rejected():
    with pytest.raises(ValueError):
        SafePlaceService(Settings()).nearby(17.4,78.5,"fictional")
