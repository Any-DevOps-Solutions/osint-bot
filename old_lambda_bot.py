import os
if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
    from bot_lambda.routes import router
    from bot_lambda.config import BOT_TOKEN, WEB_SERVER_HOST, WEB_SERVER_PORT, WEBHOOK_PATH, WEBHOOK_SECRET, BASE_WEBHOOK_URL
    from aws_xray_sdk.core import xray_recorder
    from aws_xray_sdk.core import patch_all
    patch_all()
else:
    from routes import router
    from config import BOT_TOKEN, WEB_SERVER_HOST, WEB_SERVER_PORT, WEBHOOK_PATH, WEBHOOK_SECRET, BASE_WEBHOOK_URL
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
if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
    from bot_lambda.routes import router
    from bot_lambda.config import BOT_TOKEN, WEB_SERVER_HOST, WEB_SERVER_PORT, WEBHOOK_PATH, WEBHOOK_SECRET, BASE_WEBHOOK_URL
    from aws_xray_sdk.core import xray_recorder
    from aws_xray_sdk.core import patch_all
    patch_all()
else:
    from routes import router
    from config import BOT_TOKEN, WEB_SERVER_HOST, WEB_SERVER_PORT, WEBHOOK_PATH, WEBHOOK_SECRET, BASE_WEBHOOK_URL

'''
if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    # Добавляем путь к нашему проекту в sys.path только в среде Lambda
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(current_dir, "bot_lambda"))
    from bot_project.index import lambda_handler
'''
# Объявите переменные в глобальной области видимости

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)

async def handle_event(event):
    update = types.Update.to_object(json.loads(event['body']))
    Bot.set_current(bot)
    await dp.process_update(update)
    return 'OK'

def lambda_handler(event, context):
    logging.info("Received event: " + str(event))
    return asyncio.get_event_loop().run_until_complete(handle_event(event))


def main() -> None:
    if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return

    dp.include_router(router)
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
