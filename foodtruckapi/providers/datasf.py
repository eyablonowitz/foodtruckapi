from foodtruckapi.models.foodtruck import FoodTruck
from foodtruckapi.providers.in_memory import InMemoryProvider


class DataSFProvider(InMemoryProvider):

    def fetch_data(self, url: str = "https://data.sfgov.org/resource/rqzj-sfat.json"):
        super().fetch_data(url=url)

    @staticmethod
    def _parse_to_food_trucks(obj) -> list[FoodTruck]:
        return [FoodTruck(name=item["applicant"],
                          address=item["address"],
                          latlong=(float(item["latitude"]), float(item["longitude"])),
                          permit_approved=item["status"] == "APPROVED"
                          ) for item in obj]
