import os

import time
import requests
import logging
import telegram

from dotenv import load_dotenv

from http import HTTPStatus
from exceptions import (Error, NotListError, StatusCodeUnknown,
                        StatusError, StatusNotInDict)


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
    token_all = [PRACTICUM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_TOKEN]
    return all(token_all)


def send_message(bot, message):
    """Делает запрос к эндпоитну  API-сервиса."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception:
        logger.error('Сбой при отправке сообщения')
    else:
        logger.info(f'Бот отправил сообщение: {message}')


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    timestamp = timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            logger.error(f'Ошибка при запросе к API: {response.status_code}')
            raise StatusError(f'Ошибка при запросе к API: '
                              f'{response.status_code}')
        if not response.json():
            logger.error('Ошибка в получении json')
            raise ValueError('Ошибка в получении json')
        return response.json()
    except Exception as error:
        logger.error(f'Ошибка: {error}')
        raise Error(f'Ошибка: {error}')


def check_response(response):
    """Проверка ответа API."""
    if not isinstance(response, dict):
        logger.error('Ответ API не словарь')
        raise TypeError('Ответ API не словарь')
    if not response:
        logger.error('Ответ API пустой словарь')
        raise ValueError('Ответ API пустой словарь')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        logger.error('Домашних работ нет')
        raise NotListError('Домашних работ нет')
    return homeworks


def parse_status(homework):
    """Получает статус домашней работы."""
    if 'homework_name' not in homework:
        logger.error('В словаре нет ключа [homework_name]')
        raise KeyError('В словаре нет ключа [homework_name]')
    if 'status' not in homework:
        logger.error('В словаре нет ключа [status]')
        raise StatusNotInDict('В словаре нет ключа [status]')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        logger.error('Статус работы неизвестен')
        raise StatusCodeUnknown('Статус работы неизвестен')
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    return f'Статус проверки работы изменился "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
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
