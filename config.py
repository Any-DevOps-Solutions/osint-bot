# config.py

import os
import sys

#if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
#    # Добавляем путь к нашему проекту в sys.path только в среде Lambda
#    current_dir = os.path.dirname(os.path.abspath(__file__))

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

# Определение списка доменов непосредственно в переменной
DOMAINS = [
    "superjob.ru",
    "rabota.ru",
    "hh.ru",
    "gorodrabot.ru",
    "gkjb.ru",
    "jobfiller.ru",
    "rabota-ipoisk.ru",
    "avito.ru",
    "zarplata.ru",
    "youla.ru",
    "joblab.ru",
    "trudvsem.ru",
    "jobers.ru",
    "wiweb.ru",
    "terdo.ru",
    "xn--80ace9afgbcpx3h.xn--p1ai",
    "1000dosok.ru",
    "jobreg.ru",
    "rb-n.ru",
    "normaljob.ru",
    "kadrovichka.ru",
    "personjob.ru",
    "allix.ru",
    "rjb.ru",
    "upper.ru",
    "jobmens.ru",
    "lookingforjob.ru",
    "rus-work.com",
    "job50.ru",
    "promoz.ru",
    "adsfactory.ru",
    "workdigest.ru",
    "rabota7.ru",
    "novosel.ru",
    "labourex.ru",
    "avelango.com",
    "avada.shop",
    "rabotagrad.ru",
    "findjob.ru",
    "rudos.ru",
    "trudko.ru",
    "w-rabota.ru",
    "resumet.su",
    "rabotunaidu.ru",
    "mjobs.ru",
    "remote-job.ru",
    "miltor.ru",
    "doski.ru",
    "unibo.ru",
    "barahla.net",
    "rydo.ru",
    "careerspace.app",
    "career.habr.com",
    "budu.jobs",
    "vk.com",
    "gossluzhba.gov.ru",
    "vc.ru",
    "careerist.ru",
    "fl.ru",
    "career.avito.com",
    "rabota.meds.ru",
    "maritime-zone.com",
    "rosrabota.ru",
    "tproger.ru",
    "itmozg.ru",
    "yandex.ru",
    "domkadrov.ru",
    "farpost.ru",
    "turboudalenka.ru",
    "vahtav.ru",
    "praca.by",
    "ludi.by",
    "cenotavr.by",
    "belmeta.by",
    "rabota.by"
]

WELCOME_MESSAGE = r"""
    Добридень\! 👋
    Ласкаво просимо до нашого Телеграм\-бота — вашого надійного помічника у виявленні токсичних компаній\-роботодавців на українському ринку вакансій\! 🚀

    Наш бот допомагає вам захистити себе від небезпечних роботодавців, які маскуються під пристойні компанії\. Ми використовуємо найсучасніші аналітичні методи, щоб розкрити приховані зв'язки та неочевидні залежності, які можуть бути пропущені іншими системами\.

    У той час, як інші системи використовують загальнодоступні дані з державних реєстрів, наш бот йде далі\. Ми використовуємо методи аналізу цифрових слідів, включаючи:

    🔍 Пошук і аналіз інформації з  веб\-ресурсів\.
    📈 Алгоритми, які навчаються на великих масивах даних, щоб передбачити та ідентифікувати потенційно небезпечні компанії\.
    🧠 Використання AI для аналізу поведінкових патернів компаній та їхніх представників, що дозволяє швидко виявляти аномалії\.

    Ці методи дозволяють виявляти токсичних роботодавців, які успішно маскуються у іншимх системах\.

    Інструкція:
    Щоб перевірити компанію\-роботодавця, достатньо вказати її назву та ту позицію, яку вона хоче закрити\. Для цього скористайтесь командою:
    `/check "Назва компанії", "Посада" або просто /check`
    Бот проаналізує цифрові сліди в інтернеті, використовуючи передові методи, і видасть шкалу загроз від 0 до 10 — чим вище, тим більше ймовірність, що роботодавець токсичний\!

    Долучайтесь та захищайте себе та свою кар'єру від токсичних роботодавців разом з нами\! 🚀
"""