import json
import pytest
from fake_trucks import fake_trucks
from foodtruckapi.providers.in_memory import InMemoryProvider
from freezegun import freeze_time


@pytest.fixture
def provider():
    provider = InMemoryProvider(trucks=fake_trucks, disable_fetch=True)
    return provider


json_fake_data1 = """
        [
          {
            "name": "Test1",
            "address": "Test Dr",
            "latlong": [0,0],
            "permit_approved": true
          }
        ]
"""


json_fake_data2 = """
        [
          {
            "name": "Test1",
            "address": "Test Dr",
            "latlong": [0,0],
            "permit_approved": true
          },
          {
            "name": "Test2",
            "address": "Test Dr",
            "latlong": [0,0],
            "permit_approved": true
          }
        ]
"""


def test_in_memory_provider_add(provider: InMemoryProvider):
    assert 8 == len(provider.trucks)


def test_in_memory_provider_filter(provider: InMemoryProvider):
    happy_trucks = provider.search(name="hap")
    assert len(happy_trucks) == 2
    assert "Happy Approved Truck" == happy_trucks[0].name
    assert "Another Happy Truck" == happy_trucks[1].name


def test_in_memory_provider_name_filter_incl_unapproved(provider: InMemoryProvider):
    happy_trucks = provider.search(only_approved=False, name="hap")
    assert len(happy_trucks) == 3
    assert "Happy Approved Truck" == happy_trucks[0].name
    assert "Another Happy Truck" == happy_trucks[1].name
    assert "Hap's Unapproved Truck" == happy_trucks[2].name


def test_in_memory_provider_closest(provider: InMemoryProvider):
    closest = provider.search(only_approved=False, latlong=(10, 10), limit=3)
    assert 3 == len(closest)
    assert "Near 1 Truck" == closest[0].name
    assert "Near 2 Truck" == closest[1].name
    assert "Near 3 Truck" == closest[2].name


def test_in_memory_provider_closest_approved(provider: InMemoryProvider):
    closest = provider.search(latlong=(10, 10), limit=3)
    assert 3 == len(closest)
    assert "Near 1 Truck" == closest[0].name
    assert "Near 2 Truck" == closest[1].name
    assert "Near 4 Truck" == closest[2].name


def test_in_memory_provider_fetch(requests_mock):
    provider = InMemoryProvider()
    requests_mock.get("https://fake", json=json.loads(json_fake_data1))
    provider.fetch_data(url="https://fake")
    assert 1 == len(provider.trucks)
    assert "Test1" == provider.trucks[0].name
    assert "Test Dr" == provider.trucks[0].address
    assert (0,0) == provider.trucks[0].latlong
    assert provider.trucks[0].permit_approved


def test_in_memory_provider_dual_fetch_within_ttl(requests_mock):
    provider = InMemoryProvider(data_ttl_secs=10)
    with freeze_time("2000-01-01 00:00:00"):
        requests_mock.get("https://fake", json=json.loads(json_fake_data1))
        provider.fetch_data(url="https://fake")
    with freeze_time("2000-01-01 00:00:05"):
        requests_mock.get("https://fake", json=json.loads(json_fake_data2))
        provider.fetch_data(url="https://fake")
    assert 1 == len(provider.trucks)


def test_in_memory_provider_dual_fetch_over_ttl(requests_mock):
    provider = InMemoryProvider(data_ttl_secs=10)
    with freeze_time("2000-01-01 00:00:00"):
        requests_mock.get("https://fake", json=json.loads(json_fake_data1))
        provider.fetch_data(url="https://fake")
    with freeze_time("2000-01-01 00:0:15"):
        requests_mock.get("https://fake", json=json.loads(json_fake_data2))
        provider.fetch_data(url="https://fake")
    assert 2 == len(provider.trucks)
