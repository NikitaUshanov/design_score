import base64

import pytest
import unittest


from backend.src.app import get_webpage_image, decode_image_and_save


class BackendTest(unittest.TestCase):
    @pytest.mark.unit_test
    @pytest.mark.parametrize(
        "url",
            (
                "https://github.com",
                "https://google.com",
            )
    )
    def test_get_webpage_image_success(self, url):
        result, encoded_string = get_webpage_image(url)
        base64.b64decode(encoded_string)

    @pytest.mark.unit_test
    @pytest.mark.parametrize(
        "url",
            (
                "tttt",
                "foobar"
            )
    )
    def test_get_webpage_image_error(self, url):
        with self.assertRaises(Exception) as _:
            get_webpage_image(url)

    @pytest.mark.unit_test
    @pytest.mark.parametrize(
        "encoded_string",
        (
                "YW5ub3VuY2VkaGVjdXJ2ZXF1ZXN0aW9ucmVwcmVzZW50bWFjaGluZW1haW5iZWxpZXY=",
                "c2Vhc29udHViZXJlcG9ydHJvbGx0b2JhY2Nvc3RvcHBlZGdsYXNzc2ltaWxhcnNwZWM="
        )
    )
    def test_decode_image_and_save_success(self, encoded_string):
        assert isinstance(decode_image_and_save(encoded_string), str)

    @pytest.mark.unit_test
    @pytest.mark.parametrize(
        "encoded_string",
        (
                "tttt",
                "foobar"
        )
    )
    def test_decode_image_and_save_success(self, encoded_string):
        with self.assertRaises(Exception) as _:
            decode_image_and_save(encoded_string)

