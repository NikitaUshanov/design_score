import base64
import csv
import logging
import os
import random
from datetime import datetime
from io import BytesIO
from typing import Optional

import requests
from PIL import Image
from random_word import RandomWords
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from telegram import Update
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters,
)
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


r = RandomWords()
screenshots_folder = "screenshots"
if not os.path.exists(screenshots_folder):
    os.makedirs(screenshots_folder)


class GoogleSearchException(Exception):
    pass


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
    chrome_options.page_load_strategy = "eager"
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(options=chrome_options, service=service)
    driver.set_page_load_timeout(15.0)
    return driver


def decode_image(encoded_string: str) -> Image:
    image_data = base64.b64decode(encoded_string)
    return Image.open(BytesIO(image_data))


def get_random_website() -> str:
    random_word = r.get_random_word()

    params = {"key": os.getenv("G_TOKEN"), "q": random_word}
    response = requests.get("https://serpapi.com/search", params=params)

    if str(response.status_code).startswith("4"):
        logger.error(response.text)
        raise GoogleSearchException(response.text)
    search_results = response.json()
    if "organic_results" in search_results:
        first_result = search_results["organic_results"][
            random.randint(1, len(search_results["organic_results"]) - 1)
        ]["link"]
        return first_result
    return get_random_website()


def take_screenshot() -> str:
    driver = get_browser()
    try:
        driver.get(get_random_website())
    except WebDriverException:
        driver.quit()
        return take_screenshot()
    except GoogleSearchException as err:
        driver.quit()
        return "ERROR: " + str(err)
    screenshot_path = (
        f"{screenshots_folder}/{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    )
    image_encode = driver.get_screenshot_as_base64()
    driver.quit()
    return image_encode


def save_evaluation(image_encode: str, rating: Optional[int]) -> None:
    with open("ratings.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), image_encode, rating])


########################
####   TELEGRAM    #####
########################


async def start(update: Update, context: CallbackContext) -> None:
    await send_screenshot(update, context)


async def send_screenshot(update: Update, context: CallbackContext) -> None:
    image_encode = take_screenshot()
    if image_encode.startswith("ERROR"):
        await update.message.reply_text(image_encode)
    else:
        await update.message.reply_photo(
            photo=decode_image(image_encode),
            caption="Пожалуйста, оцените дизайн сайта от 1 до 9.",
        )
        context.user_data["last_screenshot"] = image_encode


async def bot_logic(update: Update, context: CallbackContext) -> None:
    rating = update.message.text
    if rating.isdigit() and 1 <= int(rating) <= 9:
        image_encode = os.path.basename(
            context.user_data.get("last_screenshot", "unknown.png")
        )
        save_evaluation(image_encode, rating)
        await update.message.reply_text("Спасибо за вашу оценку!")
        await send_screenshot(update, context)
    else:
        await update.message.reply_text("Пожалуйста, введите число от 1 до 9.")


def main():
    token = os.getenv("TG_TOKEN")
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_logic))

    application.run_polling()


if __name__ == "__main__":
    main()
