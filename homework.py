import os

import time
import requests
import logging
import telegram
import sys

from dotenv import load_dotenv

from http import HTTPStatus
from exceptions import (StatusCodeUnknown, StatusError,
                        StatusNotInDict)
from telegram.error import TelegramError
from telegram import Bot
from typing import Any

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s, %(levelname)s, %(message)s',
    filename='program.log',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def check_tokens():
    """Проверяет доступность переменных."""
    return all([PRACTICUM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_TOKEN])


def send_message(bot: Bot, message: str) -> None:
    """Делает запрос к эндпоитну  API-сервиса."""
    try:
        logger.debug("Начало отправки сообщения.")
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except TelegramError:
        logger.error('Сбой при отправке сообщения')
    else:
        logger.info(f'Бот отправил сообщение: {message}')


def get_api_answer(timestamp: int = None) -> Any:
    """Делает запрос к эндпоинту API-сервиса."""
    timestamp = timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            response_api = f'Ошибка при запросе к API: {response.status_code}'
            logger.error(response_api)
            raise StatusError(response_api)
        return response.json()
    except requests.RequestException as error:
        request_exception = f'Ошибка при запросе к API: {error}'
        logger.error(request_exception)
        raise StatusError(request_exception)


def check_response(response: dict):
    """Проверка ответа API."""
    if not response:
        respone_nothing = 'Ответ API пустой словарь'
        logger.error(respone_nothing)
        raise ValueError(respone_nothing)
    if not isinstance(response, dict):
        response_not_dict = 'Ответ API не словарь'
        logger.error(response_not_dict)
        raise TypeError(response_not_dict)
    homeworks = response.get('homeworks')
    if not homeworks:
        not_homeworks = 'В ответе API нет ключа "homeworks"'
        logger.error(not_homeworks)
        raise ValueError(not_homeworks)
    if not isinstance(homeworks, list):
        not_home_work = 'Домашних работ нет'
        logger.error(not_home_work)
        raise TypeError(not_home_work)
    return homeworks


def parse_status(homework: dict):
    """Получает статус домашней работы."""
    if 'homework_name' not in homework:
        not_key_homework = 'В словаре нет ключа [homework_name]'
        logger.error(not_key_homework)
        raise KeyError(not_key_homework)
    if 'status' not in homework:
        not_key_status = 'В словаре нет ключа [status]'
        logger.error(not_key_status)
        raise StatusNotInDict(not_key_status)
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        status_work_unknown = 'Статус работы неизвестен'
        logger.error(status_work_unknown)
        raise StatusCodeUnknown(status_work_unknown)
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        erorr_text = 'Отсутствуют переменных окружения'
        logging.critical(erorr_text)
        sys.exit(erorr_text)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            for homework in homeworks:
                message = parse_status(homework)
                send_message(bot, message)
            timestamp = response.get('current_date', timestamp)
        except Exception as error:
            logger.error(f'Ошибка: {error}')
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
