import asyncio
import logging
from app.core.config import config
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from app.core.config import config
from app.bot.handlers import router
# 
# импорты роутеров бота 
# 

bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

commands = [
        BotCommand(command="/start", description="Начать работу"),
    ]


async def start():
    await bot.set_my_commands(commands)
    dp.include_router(router)
    # dp.include_router(start_router)
    # dp.include_router(balance_router)
    # dp.include_router(categories_router)
    # dp.include_router(transactions_router)
    # dp.include_router(statistic_router)
    
    # print("Bot started...")
    # print("gawgwa")


async def on_startup():
    logging.info("🚀 Starting application")
    await start()
    if config.DEBUG:
        _ = asyncio.create_task(
            dp.start_polling(
                bot,
                polling_timeout=30,
                handle_signals=False,
                allowed_updates=dp.resolve_used_update_types(),
            )
        )
    # else:
    #     WEBHOOK_PATH = f"webhook/{settings.BOT_TOKEN}"
    #     await bot.set_webhook(
    #         f"https://{settings.DOMAIN}/{WEBHOOK_PATH}",
    #         allowed_updates=dp.resolve_used_update_types(),
    #     )


async def on_shutdown():
    if config.DEBUG:
        await dp.stop_polling()
    # else:
    #     await dp.delete_webhook()
    # logging.info("⛔️ Stop bot")
    # logging.info("⛔️ Stop application"
