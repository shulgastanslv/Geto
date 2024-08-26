import asyncio
import logging
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

@router.message()
async def first_message(message : Message):
    usersCommandHandler = injector.get(UsersCommandHandler)
    await usersCommandHandler.first_message(message)

async def main() -> None:
    db_context = injector.get(DbContext)
    db_context.show_all_tables()
    dp.include_router(router)
    await dp.start_polling(bot)

config = Config()
bot = Bot(config.get_telegram_token(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is disabled")
