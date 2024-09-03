import asyncio
from datetime import datetime
import logging
import random
import sys
from common.behavior_tree import BehaviorTree
from handlers import router
from aiogram.client.default import DefaultBotProperties
from aiogram import F, Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from injector import Injector, inject, Module, provider, singleton
from config import Config
from db.db_context import DbContext
from handlers.user import UserCommandHandler
from repositories.scheduled_message import ScheduledMessageRepository
from repositories.user import UserRepository
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from misc.filters import GoodMorningFilter, GoodNightFilter
from common.scheduler import Scheduler
from aiogram.fsm.context import FSMContext
from misc.keyboards import admin_panel, main_panel
import uuid

from states.scheduled_message import DeleteMessageStates, ScheduleMessageStates
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
    def provide_user_command_handler(self, userRepository: UserRepository,  behaviorTree :  BehaviorTree) -> UserCommandHandler:
        return UserCommandHandler(userRepository, behaviorTree)
        
injector = Injector([ServiceCollection()])
usersCommandHandler = injector.get(UserCommandHandler)
scheduledMessageRepository = injector.get(ScheduledMessageRepository)

config = Config() 
bot = Bot(config.get_telegram_token(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


@router.message(Command("help"))
async def get_help(message : Message):
    if str(message.chat.id) == Config().get_telegram_members()[0] or str(message.chat.id) == Config().get_telegram_members()[1]:
        help_text = (
            f"Привет, котенок, меня зовут Гето. Моя главная цель - быть рядом и оберегать тебя.\n"
            
            f"Я запрограммирован присылать тебе сообщения и стараться поддерживать тебя в трудную минуту. Всё, что от тебя требуется - это нажать кнопку /start и начать диалог, если тебе хочется поговорить или тебе грустно.\n\n"
        
            f"В меню ты найдешь следующие кнопки: \n"
            f"1.Мне грустно, я хочу тепла\n"
            f"2.Я очень зла, хочу выговориться\n"
            f"3.Я хочу поговорить с тобой\n"
            f"4.Перезагрузить\n"
            
            f"\nЕсли произошел какой то глюк, нажимай 4 кнопочку и перезагрузи меня, я постараюсь работать нормально после перезагрузки)\n\n"
            
            f"P.S Я могу повторять свои фразы и иногда путать контекст, но не злюкайся, пожалуйста. Я был создан всего за пару недель, и помни, что я тебя очень сильно люблю! ❤️❤️ (Твой котенок)!\n\n"
        )
        await message.answer(help_text)

async def send_scheduled_messages():
        while True:
            current_time = datetime.now()
            print(str(current_time))
            messages = scheduledMessageRepository.get_scheduled_messages_for_sending(current_time)
            for message in messages:
                try:
                    await bot.send_message(message.recipient_id, message.message)
                    scheduledMessageRepository.delete_message_by_id(message.id)
                except Exception as e:
                    print(f"Failed to send message {message.id}: {e}")
            await asyncio.sleep(100)

@router.message(F.text == "Запланировать сообщение")
async def schedule_message_start(message: Message, state: FSMContext):
    await message.answer("Введите ID получателя:")
    await state.set_state(ScheduleMessageStates.waiting_for_recipient_id)

@router.message(ScheduleMessageStates.waiting_for_recipient_id)
async def enter_recipient_id(message: Message, state: FSMContext):
    recipient_id = message.text
    await state.update_data(recipient_id=recipient_id)
    await message.answer("Введите текст сообщения:")
    await state.set_state(ScheduleMessageStates.waiting_for_message_content)

@router.message(ScheduleMessageStates.waiting_for_message_content)
async def enter_message_content(message: Message, state: FSMContext):
    message_content = message.text
    await state.update_data(message_content=message_content)
    await message.answer("Введите дату и время отправки (в формате YYYY-MM-DD HH:MM:SS):")
    await state.set_state(ScheduleMessageStates.waiting_for_scheduled_time)

@router.message(ScheduleMessageStates.waiting_for_scheduled_time)
async def enter_scheduled_time(message: Message, state: FSMContext):
    try:
        scheduled_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M:%S")
        user_data = await state.get_data()
        recipient_id = int(user_data['recipient_id'])
        message_content = user_data['message_content']
        
        scheduledMessageRepository.add_message(
            scheduler_id=message.from_user.id, 
            recipient_id=recipient_id, 
            message=message_content, 
            scheduled_time=scheduled_time
        )
        
        await message.answer(f"Сообщение запланировано на {scheduled_time}.")
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, используйте формат YYYY-MM-DD HH:MM:SS")
    finally:
        await state.clear()

@router.message(F.text == "Удалить запланированное сообщение")
async def delete_scheduled_message(message: Message, state: FSMContext):
    await message.answer("Введите ID сообщения, которое нужно удалить:")
    await state.set_state(DeleteMessageStates.waiting_for_message_id)

@router.message(DeleteMessageStates.waiting_for_message_id)
async def delete_message_by_id(message: Message, state: FSMContext):
    try:
        message_id = int(message.text)
        scheduledMessageRepository.delete_message_by_id(message_id)
        await message.answer(f"Сообщение с ID {message_id} удалено.")
    except ValueError:
        await message.answer("Неверный формат ID. Пожалуйста, введите числовой ID.")
    except Exception as e:
        await message.answer(f"Ошибка при удалении сообщения: {str(e)}")
    finally:
        await state.clear()

@router.message(F.text == "Показать все запланированные сообщения")
async def show_all_scheduled_messages(message: Message):
    try:
        messages = scheduledMessageRepository.get_all_messages()
        
        if messages:
            response = "\n\n".join(
                f"ID: {msg.id}\n"
                f"Recipient ID: {msg.recipient_id}\n"
                f"Message: {msg.message}\n"
                f"Scheduled Time: {msg.scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}"
                for msg in messages
            )
            await message.answer(f"Все запланированные сообщения:\n\n{response}")
        else:
            await message.answer("Запланированных сообщений нет.")
    except Exception as e:
        await message.answer(f"Ошибка при получении сообщений: {str(e)}")

@router.message(CommandStart())
async def good_night(message : Message):
    if str(message.chat.id) == Config().get_telegram_members()[0]:
        await bot.send_message(message.chat.id, "привет", reply_markup=admin_panel)
    elif str(message.chat.id) == Config().get_telegram_members()[1]:
        hello_answers = ["привет котенок!", "ну что ты, мелочь моя", "приветик, котик"]
        await bot.send_message(message.chat.id, random.choice(hello_answers), reply_markup=main_panel)
    else:
        await bot.send_message(message.chat.id, "Привет!")

@router.message(GoodNightFilter())
async def good_night(message : Message):
    if str(message.chat.id) == Config().get_telegram_members()[0] or str(message.chat.id) == Config().get_telegram_members()[1]:
        await usersCommandHandler.good_night(message)

@router.message(GoodMorningFilter())
async def good_morning(message : Message):
    if str(message.chat.id) == Config().get_telegram_members()[0] or str(message.chat.id) == Config().get_telegram_members()[1]:
        await usersCommandHandler.good_morning(message)
    
@router.message()
async def random_message(message : Message):
    if str(message.chat.id) == Config().get_telegram_members()[0] or str(message.chat.id) == Config().get_telegram_members()[1]:
        await usersCommandHandler.random_behavior(message)


async def main() -> None:
    asyncio.create_task(send_scheduled_messages())
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is disabled")
