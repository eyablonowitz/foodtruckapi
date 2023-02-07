import json
import os
from fastapi.testclient import TestClient
from foodtruckapi.api import app


def mock_data(requests_mock):
    json_fake_data_file = os.path.join(os.path.dirname(__file__), 'test_datasf.json')
    with open(json_fake_data_file, "r") as f:
        json_fake_data = f.read()
    requests_mock.get("https://data.sfgov.org/resource/rqzj-sfat.json", json=json.loads(json_fake_data))
    return None


def test_get_all_trucks(requests_mock):
    mock_data(requests_mock)
    with TestClient(app) as client:
        response = client.get("/foodtruckapi/datasf/search?only_approved=False")
        assert response.status_code == 200
        assert len(response.json()) == 4


def test_get_approved(requests_mock):
    mock_data(requests_mock)
    with TestClient(app) as client:
        response = client.get("/foodtruckapi/datasf/search?only_approved=True")
        assert response.status_code == 200
        assert len(response.json()) == 2


def test_search_by_name(requests_mock):
    mock_data(requests_mock)
    with TestClient(app) as client:
        response = client.get("/foodtruckapi/datasf/search?name=bonito")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]['name'] == 'Bonito Poke'


def test_search_by_address(requests_mock):
    mock_data(requests_mock)
    with TestClient(app) as client:
        response = client.get("/foodtruckapi/datasf/search?address=berry")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]['address'] == '185 BERRY ST'


def test_search_limit(requests_mock):
    mock_data(requests_mock)
    with TestClient(app) as client:
        response = client.get("/foodtruckapi/datasf/search?limit=1")
        assert response.status_code == 200
        assert len(response.json()) == 1


def test_sort_by_distance(requests_mock):
    mock_data(requests_mock)
    with TestClient(app) as client:
        response = client.get("/foodtruckapi/datasf/search?latlong=37.77632714778992,-122.39179682107691")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]['name'] == 'Off the Grid Services, LLC'


def test_bad_provider_name_yields_invalid_error(requests_mock):
    mock_data(requests_mock)
    with TestClient(app) as client:
        response = client.get("/foodtruckapi/foo/search?limit=1")
        response_json = response.json()
        assert response.status_code == 422
        assert "value is not a valid enumeration member" in response_json['detail'][0]['msg']
