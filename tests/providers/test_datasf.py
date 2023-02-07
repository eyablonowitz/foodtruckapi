import json
import os
from foodtruckapi.providers.datasf import DataSFProvider


def test_datasf_load(requests_mock):
    json_fake_data_file = os.path.join(os.path.dirname(__file__), '../test_datasf.json')
    with open(json_fake_data_file, "r") as f:
        json_fake_data = f.read()
    requests_mock.get("https://data.sfgov.org/resource/rqzj-sfat.json", json=json.loads(json_fake_data))
    datasf = DataSFProvider()
    datasf.fetch_data()
    assert 4 == len(datasf.trucks)
    assert "Ziaurehman Amini" == datasf.trucks[0].name
    assert "5 THE EMBARCADERO" == datasf.trucks[0].address
    assert (37.794331003246846, -122.39581105302317) == datasf.trucks[0].latlong
    assert False is datasf.trucks[0].permit_approved
