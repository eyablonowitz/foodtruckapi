# foodtruckapi

Foodtruckapi provides a simple web API for searching food trucks, push carts, and other mobile food facilities.
In its current form it has only one data source - the [San Francisco Mobile Food Facility Permit dataset](https://data.sfgov.org/Economy-and-Community/Mobile-Food-Facility-Permit/rqzj-sfat/data).

## Quick start

### Running locally (Docker)

#### Prerequisites
- Docker
```shell
docker build . -t foodtruckapi
docker run -p 127.0.0.1:8000:80 foodtruckapi
```

### Running locally (non-container)
#### Prerequisites
- Python >=3.10
```shell
pip install -r requirements.txt
uvicorn foodtruckapi.api:app --reload
```

### Exercising the API

You can use`curl` to try out the API. Here we'll search for trucks with "taco" in the `name` and "shore" in
the `address`.
> Note: This example  is piping to `jq` for formatting but this can be omitted.
```shell
curl "http://127.0.0.1:8000/foodtruckapi/datasf/search?name=taco&address=shore" | jq .
```
Which should produce a response like:
```json
[
  {
    "name": "San Pancho's Tacos",
    "address": "491 BAY SHORE BLVD",
    "latlong": [
      0,
      0
    ],
    "permit_approved": true
  }
]

```

### Tests
Execute unit tests with [pytest](https://docs.pytest.org/):
```shell
pip install -r requirements-test.txt
python -m pytest
```

## API Description
You saw an example of exercising the API above. 

See the full [OpenAPI docs](https://app.swaggerhub.com/apis-docs/eric.yablonowitz/foodtruckapi/0.0.1) and the [json
definition produced by FastAPI](./openapi.json) for more details on the request parameters and response schemas.

## Repository layout

```
- foodtruckapi/
  - Dockerfile    builds the service in a container with Uvicorn web server
  - foodtruckapi/ Python source root
      - api.py         FastAPI entrypoint
      - models/        Python modules containing FoodTruck and FoodTruckList generic data model classes
      - providers/     Python modules containing data provider classes (e.g. DataSF)
  - tests              
```

## Problem Statement
This project was created in response to a coding challenge. Here is the original prompt: 

> Given the data about Mobile Food Facilities in San Francisco (https://data.sfgov.org/Economy-and-Community/Mobile-Food-Facility-Permit/rqzj-sfat/data),
build an API to perform the following operations on the data set:
> - Search by name of applicant. Include optional filter on "Status" field.
> - Search by street name. The user should be able to type just part of the address. Example: Searching for "SAN" should return food trucks on "SANSOME ST"
> - Given a latitude and longitude, the API should return the 5 nearest food trucks. By default, this should only return food trucks with status "APPROVED", but the user should be able to override this and search for all statuses.
> - You can use any external services to help with this (e.g., Google Maps API).
  
### Further assumptions:
In developing a solution I made a number of assumptions over-and-above the prompt above:

- While the prompt linked to a human-oriented URL for the datasource, I assumed it was acceptable to consume
  the data from the API endpoint linked from that site.
- As with address, searching by name should also return partial matches ("Betty" should return "Betty's Burgers")
- Searches should be case-insensitive
- The upstream data changes infrequently
- The API should be public
- The underlying dataset is small (hundreds of trucks) and is likely to remain small.

## Design

### Priorities

I had 5-6 hours to spend on this coding challenge. As with any real-world code, given the limited time, I had to make
choices. And my choices here mirrored how I would start a real-world project. In order of relative priority I focused on:

1. Basic functionality with **good test coverage to iterate with confidence** following a **test-driven-design** loop
2. Code **readability**
3. Keeping the model **easy-to-understand** without closing off obvious paths to extension
4. Documentation
5. Input validation


### Anti-priorities

I specifically chose not to spend time on:

1. Performance optimizations
2. Error handling
3. Production readiness
   
See *Critique* below for more discussion.

### Notes on specific choices

#### Python/FastAPI for ease of development/docs
I implemented foodtruckapi in Python with [FastAPI](https://fastapi.tiangolo.com) because I have found it to be
excellent for creating readable and self-documenting APIs. The integration with Python's type-hinting and 
Pydantic is a particularly helpful feature for quickly creating OpenAPI-compliant documentation.

#### Combine all requirements into single API endpoint to maximize client flexibility
API consumers may optionally want to combine searching with sort-by-distance such that they can find the nearest food
truck with "pizza" in the name. They may also want to limit the number of results returned for searches.

#### Separate data models and providers for extensibility
While this API was built as a demonstration and not for real-world use, I still wanted it to be easily pluggable with
additional data providers. This did not significantly increase the complexity or worsen the readability of the project.
And it seemed like a natural plan to enable searching food trucks in cities other than San Francisco.

#### Use local-only geo library for distance to reduce latency and limit external dependencies
Though the prompt hinted that external services like the Google Maps API could be used for distance calculations, I
chose instead to local calculations provided by the [GeoPy](https://geopy.readthedocs.io/en/stable/) library. This
should result in lower latencies than consuming an external service. It also means foodtruckapi's availability is not
dependent on another external service.

#### Pytest with requests mocking for unit testing
Unit tests are built around PyTest with requests to the upsteam datasource mocked enabling offline testing of most code
paths.

#### Cache the full dataset in memory
I assumed data would be small and change  infrequently. Therefore,the API loads the full data on the first request and
caches it for a TTL period - an hour by default. During the TTL, calls to foodtruckapi are served entirely from memory.
This improves latency and reduces worries of rate limiting from upstream sources. It also makes the service more
resilient to disruptions at the datasource.

## Critique

### Next steps

I was asked to time-box this effort to 5-6 hours, and that is approximately the time I spent. This necessitated omitting
some features that would be required for a production API. With more time I would focus on:

#### Additional input validation
A production service will want to thoroughly validate input data from both the API service and while fetching data from
upstream. This is a hard requirement for security reasons. 

#### Error handling
Adding better error handling will improve the user and operator experience and make the service more resilient.

#### CI pipeline
A continuous integration pipeline with configuration resident in the repo would increase confidence in pull requests.

#### Observability
Adding telemetry for metrics, event-logging, and traces would give operators confidence that the API is working as
expected. And it would help them troubleshoot when things aren't quite right.

#### result pagination
While the API does allow you to limit the results returned, it does not offer a way to page through data.

#### externalize data
An external service like Redis could let multiple instances of the service benefit from a shared cache.

#### request retry/timeout/backoff
Fetching data from the upstream datasource has no retry facility. Nor is there a configurable timeout. An intermittent 
problem at app start-time will result in a crashed or unusable service.

#### auth to datasource
Requests to the datasource are anonymous which may increase the chance of being rate-limited.

#### configuration settings including secrets
There is no centralized configuration pattern for configuration data like upstream URLs and credentials.

#### Platform and CD code/config 
For a production service, especially one where the hosting model is known, I would include platform code/config as
well as a continuous deployment pipeline to complement the CI pipeline already mentioned.

### Scaling discussion

The small DataSF Mobile Food Facility dataset means generally scalability is unlikely to be a major concern. Even without
performance optimizations, the service should be able to scale to a very large number of users without a lot of
hardware.

A *much* larger and/or more complex dataset might necessitate reworking the service. Some possible ideas:
- A shared/externalized cache 
- Utilizing upstream datasource filtering/searching instead of doing everything locally
- Indexing data and/or using a network-local external datastore that offers search indexing as a native feature
