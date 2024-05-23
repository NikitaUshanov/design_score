import base64
import logging
import os
from io import BytesIO
from typing import Optional, Tuple

import flask
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


########################
####   EXTRA FUNC  #####
########################


def get_browser() -> webdriver.Chrome:
    base_path = os.getcwd()
    cookie_ignore_path = f"{base_path}/src/extensions/cookieconsent"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--disable-extensions-except={cookie_ignore_path}")
    chrome_options.add_argument(f"--load-extension={cookie_ignore_path}")
    chrome_options.add_argument("window-size=1366,694")
    service = Service(executable_path=ChromeDriverManager().install())
    return webdriver.Chrome(options=chrome_options, service=service)


def process_input_url(url: str) -> str:
    url = url.strip()
    if not (url.lower().startswith("http://") or url.lower().startswith("https://")):
        url = f"http://{url}"
    return url


def get_webpage_image(url: str) -> Tuple[bool, Optional[str]]:
    browser = get_browser()
    try:
        browser.get(url)
        image_encode = browser.get_screenshot_as_base64()
        logger.info(f"Screenshot saved")
        return True, image_encode
    except Exception as e:
        logger.error(f"Error capturing webpage screenshot: {e}")
        return False, None
    finally:
        browser.quit()


def decode_image_and_save(encoded_string: str) -> str:
    image_data = base64.b64decode(encoded_string)
    img_path = f"static/image-tmp/{encoded_string[:10]}.png"
    Image.open(BytesIO(image_data)).save(img_path)
    return img_path


########################
#####  FLASK API  ######
########################


@app.route("/", methods=["GET"])
def index():
    return flask.render_template("index.html")


@app.route("/loading", methods=["GET"])
def loading():
    return flask.render_template("loading.html", url=request.url)


@app.route("/websites/evaluate", methods=["POST"])
def evaluate_website():
    input_url = request.json.get("url")
    logger.info(f"The url is {input_url}")
    url = process_input_url(input_url)
    logger.info(f"The processed url is {url}")

    succeeded, image_encode = get_webpage_image(url)
    if not succeeded:
        return jsonify({"statusCode": 400}), 400

    try:
        response = requests.post(
            "http://cnn:7000/run_cnn", json={"image": image_encode}
        )
        response_data = response.json()
        score = response_data.get("score", 0)
        logger.info(f"The score is {score:.2f}")

        return (
            jsonify(
                {
                    "score": score,
                    "url": url,
                    "image": f"{decode_image_and_save(image_encode)}",
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({"statusCode": 500}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
