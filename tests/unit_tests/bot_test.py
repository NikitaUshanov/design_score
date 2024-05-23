import pytest
from PIL.Image import Image
import unittest


from tg_bot.tg_bot import get_random_website, decode_image


class TelegramBotTest(unittest.TestCase):
    @pytest.mark.unit_test
    def test_random_site(self):
        result = get_random_website()
        assert isinstance(result, str)


    @pytest.mark.unit_test
    @pytest.mark.parametrize(
        "encoded_string",
            (
                "YW5ub3VuY2VkaGVjdXJ2ZXF1ZXN0aW9ucmVwcmVzZW50bWFjaGluZW1haW5iZWxpZXY=",
                "c2Vhc29udHViZXJlcG9ydHJvbGx0b2JhY2Nvc3RvcHBlZGdsYXNzc2ltaWxhcnNwZWM="
            )
    )
    def test_decode_image_success(self, encoded_string):
        assert isinstance(decode_image(encoded_string), Image)

    @pytest.mark.unit_test
    @pytest.mark.parametrize(
        "encoded_string",
            (
                "tttt",
                "foobar"
            )
    )
    def test_decode_image_error(self, encoded_string):
        with self.assertRaises(Exception) as _:
            decode_image(encoded_string)
