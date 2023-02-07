from foodtruckapi.models.foodtruck import FoodTruck
from foodtruckapi.providers.in_memory import InMemoryProvider


class DataSFProvider(InMemoryProvider):

    def fetch_data(self, url: str = "https://data.sfgov.org/resource/rqzj-sfat.json"):
        super().fetch_data(url=url)

    @staticmethod
    def _parse_truck(t) -> FoodTruck:
        return FoodTruck(
            name=t["applicant"],
            address=t["address"],
            latlong=(float(t["latitude"]), float(t["longitude"])),
            permit_approved=True if t["status"] == "APPROVED" else False
        )
