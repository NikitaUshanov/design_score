import random

import flask
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tempfile
import requests
import logging


logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


def get_browser():
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
    return webdriver.Chrome(options=chrome_options)


def process_input_url(url):
    url = url.strip()
    if not (url.lower().startswith('http://') or url.lower().startswith('https://')):
        url = f"http://{url}"
    return url


def get_webpage_image(url):
    browser = get_browser()
    try:
        browser.get(url)
        image_path = f"static/image-tmp/{url.replace('/', '').replace('.', '').replace(':', '')}.png"
        browser.get_screenshot_as_file(image_path)
        logger.info(f'Screenshot saved to {image_path}')
        print(image_path)
        return True, image_path
    except Exception as e:
        logger.error(f'Error capturing webpage screenshot: {e}')
        return False, None
    finally:
        browser.quit()


@app.route('/', methods=['GET'])
def index():
    return flask.render_template("index.html")


@app.route('/loading', methods=['GET'])
def loading():
    return flask.render_template("loading.html", url=request.url)


@app.route('/websites/evaluate', methods=['POST'])
def evaluate_website():
    input_url = request.json.get('url')
    logger.info(f'The url is {input_url}')
    url = process_input_url(input_url)
    logger.info(f'The processed url is {url}')

    succeeded, image_path = get_webpage_image(url)
    if not succeeded:
        return jsonify({'statusCode': 400}), 400

    try:
        response = requests.post('http://cnn:5000/run_cnn', json={'imagePath': image_path})
        response_data = response.json()
        score = response_data.get('score', 0)
        logger.info(f'The score is {score:.2f}')

        return jsonify({
            'score': score,
            'url': url,
            'image': f'{image_path}'
        }), 200
    except Exception as e:
        logger.error(f'Error processing image: {e}')
        return jsonify({'statusCode': 500}), 500


if __name__ == '__main__':
    app.run(port=4000)
