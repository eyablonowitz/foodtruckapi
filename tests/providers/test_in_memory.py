import pytest
from fake_trucks import fake_trucks
from foodtruckapi.providers.in_memory import InMemoryProvider


@pytest.fixture
def provider():
    provider = InMemoryProvider(trucks=fake_trucks)
    return provider


def test_food_trucks_add(provider: InMemoryProvider):
    assert 8 == len(provider.trucks)


def test_food_trucks_filter(provider: InMemoryProvider):
    happy_trucks = provider.search(name="hap")
    assert len(happy_trucks) == 2
    assert "Happy Approved Truck" == happy_trucks[0].name
    assert "Another Happy Truck" == happy_trucks[1].name


def test_food_trucks_name_filter_incl_unapproved(provider: InMemoryProvider):
    happy_trucks = provider.search(only_approved=False, name="hap")
    assert len(happy_trucks) == 3
    assert "Happy Approved Truck" == happy_trucks[0].name
    assert "Another Happy Truck" == happy_trucks[1].name
    assert "Hap's Unapproved Truck" == happy_trucks[2].name


def test_food_trucks_closest(provider: InMemoryProvider):
    closest = provider.search(only_approved=False, latlong=(10, 10), limit=3)
    assert 3 == len(closest)
    assert "Near 1 Truck" == closest[0].name
    assert "Near 2 Truck" == closest[1].name
    assert "Near 3 Truck" == closest[2].name


def test_food_trucks_closest_approved(provider: InMemoryProvider):
    closest = provider.search(latlong=(10, 10), limit=3)
    assert 3 == len(closest)
    assert "Near 1 Truck" == closest[0].name
    assert "Near 2 Truck" == closest[1].name
    assert "Near 4 Truck" == closest[2].name
