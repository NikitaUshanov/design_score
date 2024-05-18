from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
import csv
import requests
from datetime import datetime
import os
import random
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from random_word import RandomWords


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


r = RandomWords()
screenshots_folder = "screenshots"
if not os.path.exists(screenshots_folder):
    os.makedirs(screenshots_folder)


# Функция для старта бота
async def start(update: Update, context: CallbackContext) -> None:
    await send_screenshot(update, context)


r = RandomWords()

# Функция для получения url случайного сайта
def get_random_website() -> str:
    random_word = r.get_random_word()

    params = {
        "key": os.getenv("G_TOKEN"),
        "q": random_word
    }
    response = requests.get("https://serpapi.com/search", params=params)

    search_results = response.json()
    if 'organic_results' in search_results:
        first_result = search_results['organic_results'][random.randint(1, len(
            search_results['organic_results'])-1)]['link']
        return first_result
    return get_random_website()


# Функция для получения скриншота
def take_screenshot() -> str:
    options = webdriver.ChromeOptions()
    options.headless = True
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(15.0)
    try:
        driver.get(get_random_website())
    except WebDriverException:
        driver.quit()
        return take_screenshot()
    screenshot_path = f"{screenshots_folder}/{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    driver.save_screenshot(screenshot_path)
    driver.quit()
    return screenshot_path


# Функция для отправки случайного скриншота
async def send_screenshot(update: Update, context: CallbackContext) -> None:
    screenshot_path = take_screenshot()
    await update.message.reply_photo(
        photo=open(screenshot_path, 'rb'),
        caption="Пожалуйста, оцените дизайн сайта от 1 до 9."
    )
    context.user_data['last_screenshot'] = screenshot_path


# Функция сохранения оценки в CSV
def save_evaluation(image_name, rating) -> None:
    with open('ratings.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), image_name, rating])


# Логика бота
async def bot_logic(update: Update, context: CallbackContext) -> None:
    rating = update.message.text
    if rating.isdigit() and 1 <= int(rating) <= 9:
        image_name = os.path.basename(context.user_data.get('last_screenshot', 'unknown.png'))
        save_evaluation(image_name, rating)
        await update.message.reply_text('Спасибо за вашу оценку!')
        await send_screenshot(update, context)
    else:
        await update.message.reply_text('Пожалуйста, введите число от 1 до 9.')


# Основная функция для запуска бота
def main():
    token = os.getenv("TG_TOKEN")
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_logic))

    application.run_polling()


if __name__ == '__main__':
    main()
