import os
import logging
import sys
import json
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.fsm.storage.memory import MemoryStorage

# Проверка среды выполнения
if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    from lambda_bot.routes import router
    from lambda_bot.config import BOT_TOKEN, WEB_SERVER_HOST, WEB_SERVER_PORT, WEBHOOK_PATH, WEBHOOK_SECRET, BASE_WEBHOOK_URL
    # Добавляем роутер в диспетчер только для AWS Lambda
    storage = MemoryStorage()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
else:
    from routes import router
    from config import BOT_TOKEN, WEB_SERVER_HOST, WEB_SERVER_PORT, WEBHOOK_PATH, WEBHOOK_SECRET, BASE_WEBHOOK_URL
    storage = MemoryStorage()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger()

# Получаем значение IS_ENABLED из переменных окружения
IS_ENABLED = os.getenv("IS_ENABLED", "True").lower() == "true"
logger.info(f"IS_ENABLED value: {IS_ENABLED}")

async def handle_event(event):
    if not IS_ENABLED:
        logger.info("Bot is disabled. Ignoring update.")
        return 'Bot is disabled'
    
    update = types.Update.model_validate(json.loads(event['body']))
    logger.info("Serialized json: " + str(update))
    await dp.feed_update(bot=bot, update=update)
    return 'OK'

def lambda_handler(event, context):
    logger.info("Received event: " + str(event))
    loop = asyncio.get_event_loop()
    if loop.is_closed():  # Исправлено здесь
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    result = loop.run_until_complete(handle_event(event))
    return {
        'statusCode': 200,
        'body': json.dumps({'message': result})
    }


async def on_startup(bot: Bot) -> None:
    if IS_ENABLED:
        await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)
        print("Hook Set")

def main() -> None:
    if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return  # Уже добавлен роутер в начале для AWS Lambda

    if IS_ENABLED:
        router.message.middleware()(lambda handler, event, data: handler(event, {**data, 'bot': bot}))
        dp.startup.register(on_startup)
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET)
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
