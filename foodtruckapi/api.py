from enum import Enum
from fastapi import FastAPI, Path, Query
from foodtruckapi.models.foodtruck import FoodTruck
from foodtruckapi.providers.datasf import DataSFProvider


app = FastAPI(
    title="foodtruckapi",
    description="Foodtruckapi provides a simple web API for searching mobile food facilities.",
    version="0.0.1")


class DataProviderName(str, Enum):
    datasf = "datasf"

    def __call__(self, *args, **kwargs):
        provider = eval(self.name)
        return provider


@app.on_event("startup")
async def startup_event():
    # Configure global persistent provider instance to persist data between requests
    # TODO: Replace this with a mutable cache
    global datasf
    datasf = DataSFProvider()
    datasf.fetch_data()


@app.get("/foodtruckapi/{provider}/search")
def foodtruckapi_search(
        provider: DataProviderName = Path(True, description="Data provider to search."),
        only_approved: bool = Query(True, description="Filter to only trucks with an approved permit."),
        latlong: str = Query(None, description="Sort by closest to latitude,longitude."),
        limit: int = Query(None, description="Limit number of results returned."),
        name: str = Query("", description="Filter to trucks names containing name."),
        address: str = Query("", description="Filter to trucks addresses containing this string.")
) -> list[FoodTruck]:
    """
    Search for food trucks and other facilities. With no query parameters, return full dataset.
    """
    return provider().search(
        only_approved=only_approved,
        latlong=latlong,
        limit=limit,
        name=name,
        address=address
    )
