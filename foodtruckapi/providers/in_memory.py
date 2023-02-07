import requests
from geopy.distance import distance
from foodtruckapi.models.foodtruck import FoodTruck
from time import time


class InMemoryProvider:
    """
    A generic FoodTruck data provider for fetching lists of FoodTruck from HTTP sources into memory for search.
    Sub-class and override the fetch_data and _parse_truck methods as needed to create usable providers.
    """

    def __init__(self, trucks: list[FoodTruck] = None, data_ttl_secs: int = 3600, disable_fetch: bool = False):
        self.trucks = trucks if trucks else []
        self.data_ttl_secs = data_ttl_secs
        self.last_fetch_time = None
        self.disable_fetch = disable_fetch

    def fetch_data(self, url: str = None):
        if self._do_not_fetch:
            return

        r = requests.get(url)
        r.raise_for_status()
        self.trucks = []
        for item in r.json():
            food_truck = self._parse_truck(item)
            self.trucks.append(food_truck)
        self.last_fetch_time = time()

    @property
    def _do_not_fetch(self) -> bool:
        if self.disable_fetch:
            return True
        if self.data_ttl_secs and self.last_fetch_time:
            secs_since_last_fetch = time() - self.last_fetch_time
            if self.data_ttl_secs > secs_since_last_fetch:
                return True

    @staticmethod
    def _parse_truck(t) -> FoodTruck:
        return FoodTruck.parse_obj(t)

    def search(self,
               only_approved: bool = True,
               latlong: tuple[float, float] = None,
               limit: int = None,
               name: str = "",
               address: str = ""
               ) -> list[FoodTruck]:

        try:
            self.fetch_data()
        except Exception:
            print("Unable to fetch updated data. Continuing search with possibly stale data.")

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
