import asyncio
import os
import sys
import time
import threading
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InputMediaPhoto, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from config import TOKEN, ZVONKI, PROXY
from parsing import get_yandex_disk_links
import logging
import datetime
print("Bot запущен")


if PROXY:
    from aiogram.client.session.aiohttp import AiohttpSession
    session = AiohttpSession(proxy=PROXY)
    bot = Bot(token=TOKEN, session=session)
else:
    bot = Bot(token=TOKEN)

dp = Dispatcher()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
disk_url = 'https://disk.yandex.ru/d/XxomzufLFsEapQ'


filtered_links = get_yandex_disk_links(disk_url)




@dp.message(Command("start", "help"))
async def cmd_start(message: Message):
    await message.answer("Привет! В один момент нам стало лень искать ссылку на диск и спрашивать расписание в чате. А вот делать бота 2 недели лень не было, поэтому наслаждайтесь)")
    await message.answer("Наш тгк - t.me/qweplus")
    await message.answer('Как пользоваться?\n/help - помощь\n/timetable - расписание уроков(сегодня и завтра)\n/bells - расписание звонков\n\nВы можете добавить qwerty в группу и он будет реагировать на слово "расписание" в вашем сообщении!')
    with open('users.txt', 'a', encoding='utf-8') as file:
        file.write(f"{message.from_user.username}, help\n")
    print(message.from_user.username)


@dp.message(F.text.lower().contains("расписание"))
async def main_handler(message: Message):
    media_group = MediaGroupBuilder()

    with open('users.txt', 'a', encoding='utf-8') as file:
        file.write(f"{message.from_user.username} расписание\n")
    if len(filtered_links) == 0:
        await message.answer("Расписания на сегодня и завтра нет")

    elif len(filtered_links) == 1:
        media_group.add_photo(media=filtered_links[0])
        await message.reply_media_group(media=media_group.build())
    else:
        media_group.add_photo(media=filtered_links[0])
        media_group.add_photo(media=filtered_links[1])
        await message.reply_media_group(media=media_group.build())







@dp.message(Command('zvonok', "z", "zov", "zvonki", "bells"))
async def z(message: Message):
    photo = FSInputFile(ZVONKI)
    with open('users.txt', 'a', encoding='utf-8') as file:
        file.write(f"{message.from_user.username} звонки\n")
    await message.reply_photo(photo=photo)



@dp.message(Command("timetable"))
async def timetable_handler(message: Message):
    media_group = MediaGroupBuilder()


    with open('users.txt', 'a', encoding='utf-8') as file:
        file.write(f"{message.from_user.username} расписание\n")

    if len(filtered_links) == 0:
        await message.answer("Расписания на сегодня и завтра нет")

    elif len(filtered_links) == 1:
        media_group.add_photo(media=filtered_links[0])
        await message.reply_media_group(media=media_group.build())
    else:
        media_group.add_photo(media=filtered_links[0])
        media_group.add_photo(media=filtered_links[1])
        await message.reply_media_group(media=media_group.build())





async def schedule_daily_restart():
    while True:
        now = datetime.datetime.now()
        target_time = now.replace(hour=8, minute=0, second=0, microsecond=0)

        if now > target_time:
            target_time += datetime.timedelta(days=1)

        wait_seconds = (target_time - now).total_seconds()

        logger.info(f"Следующая перезагрузка через {wait_seconds} секунд в 12:00")
        await asyncio.sleep(wait_seconds)

        logger.info("Перезагружаю бота в 12:00...")
        python = sys.executable
        os.execv(python, [python] + sys.argv)

async def main():

    restart_task = asyncio.create_task(schedule_daily_restart())

    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        restart_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())