from foodtruckapi.models.foodtruck import FoodTruck

fake_trucks = [
    FoodTruck(
        name="Happy Approved Truck",
        address="123 NOREAL AVE",
        latlong=(30.3442, -176.1234),
        permit_approved=True,
    ),
    FoodTruck(
        name="Sad Unapproved Truck",
        address="321 NEVERMORE RD",
        latlong=(-12.3444, 19.9434),
        permit_approved=False,
    ),
    FoodTruck(
        name="Another Happy Truck",
        address="32 MAIN ST",
        latlong=(29.4563,-139.9434),
        permit_approved=True,
    ),
    FoodTruck(
        name="Hap's Unapproved Truck",
        address="32 MAIN ST",
        latlong=(29.4563,-139.9434),
        permit_approved=False,
    ),
    FoodTruck(
        name="Near 1 Truck",
        address="1 CLOSE DR",
        latlong=(10.1, 10.1),
        permit_approved=True,
    ),
    FoodTruck(
        name="Near 2 Truck",
        address="2 CLOSE DR",
        latlong=(10.2, 10.2),
        permit_approved=True,
    ),
    FoodTruck(
        name="Near 3 Truck",
        address="3 CLOSE DR",
        latlong=(10.3, 10.3),
        permit_approved=False,
    ),
    FoodTruck(
        name="Near 4 Truck",
        address="4 CLOSE DR",
        latlong=(10.4, 10.4),
        permit_approved=True,
    ),
]
