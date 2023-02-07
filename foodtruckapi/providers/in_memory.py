import requests
from geopy.distance import distance
from foodtruckapi.models.foodtruck import FoodTruck


class InMemoryProvider:
    """
    A generic FoodTruck data provider for fetching lists of FoodTruck from HTTP sources into memory for search.
    Sub-class and override the fetch_data and _parse_truck methods as needed to create usable providers.
    """

    def __init__(self, trucks: list[FoodTruck] = None):
        self.trucks = trucks if trucks else []

    def fetch_data(self, url: str):
        r = requests.get(url)
        r.raise_for_status()
        self.trucks = []
        for item in r.json():
            food_truck = self._parse_truck(item)
            self.trucks.append(food_truck)

    @staticmethod
    def _parse_truck(t) -> FoodTruck:
        return FoodTruck(**t)

    def search(self,
               only_approved: bool = True,
               latlong: tuple[float, float] = None,
               limit: int = None,
               name: str = "",
               address: str = ""
               ) -> list[FoodTruck]:

        def filter_f(truck: FoodTruck):
            if any([
                only_approved and not truck.permit_approved,
                name.lower() not in truck.name.lower(),
                address.lower() not in truck.address.lower()
            ]):
                return False
            return True
        filtered = list(filter(filter_f, [truck for truck in self.trucks]))

        if latlong:
            filtered.sort(key=lambda truck: distance(latlong, truck.latlong))

        return list(filtered[:limit])
