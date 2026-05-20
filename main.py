import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from config import TOKEN
import parsing
from parsing import reload_parsing_data
import logging
import datetime

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WEBHOOK_HOST = "https://qwebot--fresikk.replit.app"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEB_PORT = 8080


async def periodic_parsing_update():
    while True:
        try:
            await asyncio.sleep(3600)
            now = datetime.datetime.now()
            logger.info(f"🔄 Обновляю расписание в {now.strftime('%H:%M:%S')}")
            await asyncio.to_thread(reload_parsing_data)
            logger.info(f"✅ Расписание обновлено в {now.strftime('%H:%M:%S')}")
        except Exception as e:
            logger.error(f"❌ Ошибка обновления: {e}")


@dp.startup()
async def on_startup():
    logger.info("🤖 Бот запускается...")
    asyncio.create_task(periodic_parsing_update())
    logger.info("✅ Периодическое обновление запущено")


@dp.message(Command("start", "help"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! В один момент нам стало лень искать ссылку на диск и спрашивать расписание в чате. А вот делать бота 2 недели лень не было, поэтому наслаждайтесь)"
    )
    await message.answer("Наш тгк - t.me/qweplus")
    await message.answer(
        'Как пользоваться?\n/help - помощь\n/timetable - расписание уроков(сегодня и завтра)\n/bells - расписание звонков\n\nВы можете добавить qwerty в группу и он будет реагировать на слово "расписание" в вашем сообщении!'
    )
    with open("users.txt", "a", encoding="utf-8") as file:
        file.write(f"{message.from_user.username}, help\n")
    logger.info(f"User: {message.from_user.username}")


async def send_timetable(message: Message):
    with parsing._lock:
        images = list(parsing.cached_images[:2])

    if not images:
        await message.answer("Расписания на сегодня и завтра нет")
        return

    media_group = MediaGroupBuilder()
    for i, data in enumerate(images):
        media_group.add_photo(media=BufferedInputFile(data, filename=f"timetable_{i}.jpg"))
    await message.reply_media_group(media=media_group.build())


@dp.message(F.text.lower().contains("расписание"))
async def main_handler(message: Message):
    with open("users.txt", "a", encoding="utf-8") as file:
        file.write(f"{message.from_user.username} расписание\n")
    await send_timetable(message)


@dp.message(Command("bells", "zvonok", "zvonki", "z", "zov"))
async def handle_bells(message: Message):
    logger.info(f"🚨 /bells от @{message.from_user.username}")
    bells_file = "bells.jpg"
    if not os.path.exists(bells_file):
        await message.answer("❌ Файл расписания звонков не найден. Загрузите файл bells.jpg в проект.")
        return
    photo = FSInputFile(bells_file)
    await message.reply_photo(photo=photo)
    logger.info("✅ Фото отправлено успешно!")


@dp.message(Command("timetable"))
async def timetable_handler(message: Message):
    with open("users.txt", "a", encoding="utf-8") as file:
        file.write(f"{message.from_user.username} расписание\n")
    await send_timetable(message)


async def main():
    is_deployed = os.environ.get("REPLIT_DEPLOYMENT") == "1"

    if is_deployed:
        # Webhook режим для production
        await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
        logger.info(f"✅ Webhook установлен: {WEBHOOK_URL}")

        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", WEB_PORT)
        await site.start()
        logger.info(f"✅ Веб-сервер запущен на порту {WEB_PORT}")

        await asyncio.Event().wait()
    else:
        # Polling режим для разработки
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
