from pydantic import BaseModel


class FoodTruck(BaseModel):
    name: str
    address: str
    latlong: tuple[float, float]
    permit_approved: bool
