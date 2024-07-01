import os
from aiogram import Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    from bot_lambda.functions import fetch_and_filter_results, nice_process_results, process_results, osint_process_result
    from bot.config import WELCOME_MESSAGE
else:
    from functions import fetch_and_filter_results, nice_process_results, process_results, osint_process_result
    from config import WELCOME_MESSAGE
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio


router = Router()

class CheckCompanyStates(StatesGroup):
    awaiting_company = State()
    awaiting_position = State()

state = {
    "debug": False
}


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(WELCOME_MESSAGE, parse_mode='MarkdownV2')

@router.message(Command(commands=['parol']))
async def parol_handler(message: Message, state: FSMContext) -> None:
    content = message.text.split(maxsplit=1)
    if len(content) < 2:
        await message.answer("Будь ласка, введіть пароль після команди /parol.")
        return

    password = content[1].strip()
    if password == "putin huilo":
        state_data = await state.get_data()
        state_data["debug"] = True
        await state.update_data(state_data)
        await message.answer(
            "Ла-ла-ла-ла-ла-ла-ла-ла, Ла-ла-ла-ла-ла-ла -ла-ла. Тепер ви будете отримувати розширену інформацію про джерело даних!"
        )
    else:
        state_data["debug"] = False

@router.message(Command(commands=['check']))
async def check_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    content = message.text.split(maxsplit=1)
    if len(content) < 2:
        await message.answer("Будь ласка, надайте назву компанії:")
        await state.set_state(CheckCompanyStates.awaiting_company)
    else:
        input_data = content[1].split(',')
        if len(input_data) != 2:
            await message.answer("Будь ласка, надайте назву компанії та посаду у форматі: \'/check \"Назва компанії\", \"Посада\"\'")
            return
        await process_check(message, state, bot, input_data[0].strip(), input_data[1].strip())

@router.message(CheckCompanyStates.awaiting_company)
async def handle_company(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.update_data(company=message.text.strip())
    await message.answer("Будь ласка, надайте назву посади:")
    await state.set_state(CheckCompanyStates.awaiting_position)

@router.message(CheckCompanyStates.awaiting_position)
async def handle_position(message: Message, state: FSMContext, bot: Bot) -> None:
    user_data = await state.get_data()
    company = user_data.get("company")
    position = message.text.strip()
    await process_check(message, state, bot, company, position)

@router.message(Command(commands=['stop']))
async def stop_handler(message: Message) -> None:
    await message.answer("Бот зупинено. Щоб почати знову, надішліть /start")

async def process_check(message: Message, state: FSMContext, bot: Bot, company: str, job_title: str) -> None:
    try:
        await message.answer("Шукаємо інформацію, будь ласка, зачекайте...")
        # Запуск цикла отправки уведомления о печати
        typing_task = asyncio.create_task(repeat_typing(bot, message.chat.id))
        # Использование run_in_executor для выполнения синхронных функций
        filtered_results = await asyncio.get_running_loop().run_in_executor(None, fetch_and_filter_results, company, job_title)
        response_text = await asyncio.get_running_loop().run_in_executor(None, nice_process_results, filtered_results, company, job_title)
        # Остановка цикла отправки уведомления о печати
        typing_task.cancel()
        await typing_task  # Дождитесь завершения задачи после её отмены
        if response_text:
            await message.answer(response_text)
        else:
            await message.answer("Відповідних результатів не знайдено.")
        
        user_data = await state.get_data()
        if user_data.get("debug"):
            await message.answer("Ще додатково...")
            typing_task = asyncio.create_task(repeat_typing(bot, message.chat.id))
            detailed_results = await asyncio.get_running_loop().run_in_executor(None, osint_process_result, process_results(filtered_results, company, job_title))
            typing_task.cancel()
            await typing_task  # Дождитесь завершения задачи после её отмены
            await message.answer(detailed_results, parse_mode="Markdown", disable_web_page_preview=True)
    except asyncio.CancelledError:
        # Если задача отправки уведомлений отменена, ничего не делаем
        pass
    except Exception as e:
        await message.answer(f"Виникла помилка: {str(e)}")
    finally:
        await state.clear()

async def repeat_typing(bot, chat_id):
    while True:
        try:
            await bot.send_chat_action(chat_id, 'typing')
            await asyncio.sleep(5)  # Повторять каждые 5 секунд
        except asyncio.CancelledError:
            break
