# config.py

import os
import sys

def get_env_variable(name, default=None):
    """ Получить переменную окружения или завершить работу при её отсутствии, если default не указан """
    value = os.environ.get(name, default)
    if value is None:
        print(f"Ошибка: не найдена переменная окружения {name}")
        sys.exit(1)
    return value

# Переменные для Telegram бота и веб-сервера
BOT_TOKEN = get_env_variable("BOT_TOKEN")
WEB_SERVER_HOST = get_env_variable("WEB_SERVER_HOST", "127.0.0.1")
WEB_SERVER_PORT = get_env_variable("WEB_SERVER_PORT", 8080)
WEBHOOK_PATH = get_env_variable("WEBHOOK_PATH", "/webhook")
WEBHOOK_SECRET = get_env_variable("WEBHOOK_SECRET", "my-secret")
BASE_WEBHOOK_URL = get_env_variable("BASE_WEBHOOK_URL", "https://yourdomain.com")

# Переменные для API поиска
YOUR_API_KEY = get_env_variable("YOUR_API_KEY")
YOUR_SEARCH_ENGINE_ID = get_env_variable("YOUR_SEARCH_ENGINE_ID")

# Переменные для доступа к API OpenAI
OPENAI_API_KEY = get_env_variable("OPENAI_API_KEY")

# Добавляйте дополнительные переменные по аналогии

def load_domains(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

domains_file = 'domains.txt'
DOMAINS = load_domains(domains_file)
