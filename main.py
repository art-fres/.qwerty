import asyncio
import os
import sys
import time
import threading
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InputMediaPhoto
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from config import TOKEN, ZVONKI, PROXY
from parsing import result
import logging
import datetime
from pathlib import Path
import aiohttp
import aiofiles

if PROXY:
    from aiogram.client.session.aiohttp import AiohttpSession
    session = AiohttpSession(proxy=PROXY)
    bot = Bot(token=TOKEN, session=session)
else:
    bot = Bot(token=TOKEN)

dp = Dispatcher()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dp.message(Command("start", "help"))
async def cmd_start(message: Message):
    await message.answer("Привет! В один момент нам стало лень искать ссылку на диск и спрашивать расписание в чате. А вот делать бота 2 недели лень не было, поэтому наслаждайтесь)")
    await message.answer("Наш тгк - t.me/qweplus")
    await message.answer('Как пользоваться?\n/help - помощь\n/timetable - расписание уроков(сегодня и завтра)\n/bells - расписание звонков\n\nВы можете добавить qwerty в группу и он будет реагировать на слово "расписание" в вашем сообщении!')
    with open('users.txt', 'a', encoding='utf-8') as file:
        file.write(f"{message.from_user.username}, help\n")
    logger.info(f"User: {message.from_user.username}")

@dp.message(F.text.lower().contains("расписание"))
async def main_handler(message: Message):
    media_group = MediaGroupBuilder()



    if len(result) == 0:
        await message.answer("Расписания на сегодня и завтра нет")
    elif len(result) == 1:
        media_group.add_photo(media=result[0])
        await message.reply_media_group(media=media_group.build())
    else:
        media_group.add_photo(media=result[0])
        media_group.add_photo(media=result[1])
        await message.reply_media_group(media=media_group.build())



@dp.message(Command("bells", "zvonok", "zvonki", "z", "zov"))
async def handle_bells(message: Message):
    logger.info(f"🚨 /bells от @{message.from_user.username}")


    file_path = Path("/home/artemfres/bot/bells.jpg")


    if not file_path.exists():
        logger.error(f"ФАЙЛ НЕ НАЙДЕН! Проверьте путь: {file_path}")

        logger.info(f"Текущая директория: {Path.cwd()}")
        logger.info(f"Содержимое текущей директории: {list(Path.cwd().iterdir())}")
        await message.answer("❌ Файл не найден по указанному пути")
        return


    try:
        photo = FSInputFile(str(file_path))  # Преобразуем Path в строку
        await message.reply_photo(
            photo=photo)
        logger.info(f"✅ Фото отправлено успешно!")

    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")






@dp.message(Command("timetable"))
async def timetable_handler(message: Message):
    media_group = MediaGroupBuilder()

    if len(result) == 0:
        await message.answer("Расписания на сегодня и завтра нет")
    elif len(result) == 1:
        media_group.add_photo(media=result[0])
        await message.reply_media_group(media=media_group.build())
    else:
        media_group.add_photo(media=result[0])
        media_group.add_photo(media=result[1])
        await message.reply_media_group(media=media_group.build())

# Функции для вебхука
async def set_webhook_async():

    webhook_url = f"https://artemfres.pythonanywhere.com/webhook"

    try:
        await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True
        )
        logger.info(f"✅ Webhook установлен: {webhook_url}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка установки webhook: {e}")
        return False

def set_webhook_sync():

    return asyncio.run(set_webhook_async())

#