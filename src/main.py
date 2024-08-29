import asyncio
import logging
import random
import sys
from common.behavior_tree import BehaviorTree
from handlers import router
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from injector import Injector, inject, Module, provider, singleton
from config import Config
from db.common.db_context import DbContext
from handlers.users import UsersCommandHandler
from repositories.user_repository import UserRepository
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from filters.good_morning import GoodMorningFilter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
class ServiceCollection(Module):
    
    def configure(self, binder):
        self.db_connection = Config().get_db_connection_string()
        binder.bind(DbContext, to=DbContext(db_connection=self.db_connection), scope=singleton)
    
    @provider
    @singleton
    def provide_db_context(self) -> DbContext:
        return DbContext(self.db_connection)

    @provider
    def provide_user_repository(self, db: DbContext) -> UserRepository:
        return UserRepository(db)
    
    @provider
    def provide_behavior_tree(self) -> BehaviorTree:
        return BehaviorTree()

    @provider
    def provide_users_command_handler(self, userRepository: UserRepository,  behaviorTree :  BehaviorTree) -> UsersCommandHandler:
        return UsersCommandHandler(userRepository, behaviorTree)
        
injector = Injector([ServiceCollection()])
usersCommandHandler = injector.get(UsersCommandHandler)

config = Config()
bot = Bot(config.get_telegram_token(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

async def good_morning():
    message = await bot.send_message(Config().get_telegram_members()[0], '')
    await usersCommandHandler.good_morning(message)
    
# async def send_daily_message():
#     message = await bot.send_message(Config().get_telegram_members()[0], '')
#     await usersCommandHandler.random_behavior(message)

def schedule_good_morning_message():
    scheduler = AsyncIOScheduler()
    hour = random.randint(6, 9)
    minute = random.randint(0, 59)
    scheduler.add_job(
        good_morning,
        CronTrigger(hour=hour, minute=minute),
        id='good_morning_job',
        name='Send good morning message',
        replace_existing=True
    )
    scheduler.start()


async def main() -> None:
    schedule_good_morning_message()
    
    db_context = injector.get(DbContext)
    db_context.show_all_tables()
    dp.include_router(router)
    await dp.start_polling(bot)



if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is disabled")
