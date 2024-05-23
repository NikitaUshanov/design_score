import json
import pytest
import os

import requests


host = os.getenv("HOST", "http://localhost:8000/")


@pytest.mark.integration_test
def test_evaluate_success():
    body = json.dumps(
        {
            "url": "https://github.com/"
        }
    )
    response = requests.post(host + "websites/evaluate/", data=body)
    assert response.status_code == 200
    response_body = json.loads(response.text)
    assert "score" in response_body
    assert "url" in response_body
    assert "image" in response_body


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "url",
    ("foobar", "https://never_exists_site_for_tests/"),
)
def test_evaluate_error(url):
    body = json.dumps(
        {
            "url": url
        }
    )
    response = requests.post(host + "websites/evaluate/", data=body)
    assert response.status_code == 400
