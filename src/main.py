import asyncio
from datetime import datetime
import logging
import random
import sys
from behavior_tree import BehaviorTree
from handlers import router
from aiogram.client.default import DefaultBotProperties
from aiogram import F, Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from injector import Injector, inject, Module, provider, singleton
from config import Config
from db_context import DbContext
from handlers import UserCommandHandler
from repositories import ScheduledMessageRepository
from repositories import UserRepository
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ContentType
from filters import GoodMorningFilter, GoodNightFilter
from aiogram.fsm.context import FSMContext
from keyboards import admin_panel, main_panel
from states import DeleteMessageStates, ScheduleMessageStates, UserStates


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
    @singleton
    def provide_behavior_tree(self) -> BehaviorTree:
        return BehaviorTree()

    @provider
    def provide_user_command_handler(self, userRepository: UserRepository,  behaviorTree :  BehaviorTree) -> UserCommandHandler:
        return UserCommandHandler(userRepository, behaviorTree)
        
injector = Injector([ServiceCollection()])
usersCommandHandler = injector.get(UserCommandHandler)
scheduledMessageRepository = injector.get(ScheduledMessageRepository)

config = Config() 
from aiogram.client.session.aiohttp import AiohttpSession
session = AiohttpSession(proxy='http://proxy.server:3128')
bot = Bot(config.get_telegram_token(), default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session)
dp = Dispatcher()

db = injector.get(DbContext)
if not db.table_exists("users") and not db.table_exists("scheduled_messages"):
    db.create_all_tables()

@router.message(F.text == "Кто ты?")
async def get_help(message : Message):
    if str(message.chat.id) == Config().get_telegram_members()[0] or str(message.chat.id) == Config().get_telegram_members()[1]:
        help_text = (
            f"Привет, меня зовут Гето. Моя главная цель - быть рядом и оберегать тебя.\n\n"
            f"Я запрограммирован присылать тебе сообщения и стараться поддерживать тебя в трудную минуту. Всё, что от тебя требуется - это нажать на кнопку `Старт` и начать диалог, если тебе хочется поговорить или тебе грустно.\n\n"
            f"Если произошел какой то баг, нажимай 5 кнопочку и перезагрузи меня, я постараюсь работать нормально после перезагрузки)\n\n"
            f"P.S Я могу повторять свои фразы и иногда путать контекст, но не злюкайся, пожалуйста. Я был создан всего за пару недель, и помни, что я тебя очень сильно люблю ❤️❤️\n"
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
    if str(message.chat.id) == Config().get_telegram_members()[0]:
        await message.answer("Введите ID получателя:")
        await state.set_state(ScheduleMessageStates.waiting_for_recipient_id)

@router.message(ScheduleMessageStates.waiting_for_recipient_id)
async def enter_recipient_id(message: Message, state: FSMContext):
    if str(message.chat.id) == Config().get_telegram_members()[0]:
        recipient_id = message.text
        await state.update_data(recipient_id=recipient_id)
        await message.answer("Введите текст сообщения:")
        await state.set_state(ScheduleMessageStates.waiting_for_message_content)

@router.message(ScheduleMessageStates.waiting_for_message_content)
async def enter_message_content(message: Message, state: FSMContext):
    if str(message.chat.id) == Config().get_telegram_members()[0]:
        message_content = message.text
        await state.update_data(message_content=message_content)
        await message.answer("Введите дату и время отправки (в формате YYYY-MM-DD HH:MM:SS):")
        await state.set_state(ScheduleMessageStates.waiting_for_scheduled_time)

@router.message(ScheduleMessageStates.waiting_for_scheduled_time)
async def enter_scheduled_time(message: Message, state: FSMContext):
    if str(message.chat.id) == Config().get_telegram_members()[0]:
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
    if str(message.chat.id) == Config().get_telegram_members()[0]:
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
    if str(message.chat.id) == Config().get_telegram_members()[0]:
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
async def start(message : Message, state: FSMContext):
    if str(message.chat.id) == Config().get_telegram_members()[0]:
        await bot.send_message(message.chat.id, f"привет, {message.chat.first_name}", reply_markup=admin_panel)
    elif str(message.chat.id) == Config().get_telegram_members()[1]:
        hello_answers = ["привет котенок!", "ну что ты, мелочь моя", "приветик, котик"]
        await bot.send_message(message.chat.id, random.choice(hello_answers), reply_markup=main_panel)
    else:
        await bot.send_message(message.chat.id, f"привет, {message.chat.first_name}")
    await state.set_state(UserStates.Start)
   
@router.message(F.text == 'Мне грустно, я хочу тепла')
async def sad_handler(message: Message, state: FSMContext):
    await message.answer("не грусти котенок, я с тобой! вот тебе немного тепла ❤️")
    await state.set_state(UserStates.Sad)
    
@router.message(F.text == 'Я очень зла, хочу выговориться')
async def angry_handler(message: Message, state: FSMContext):
    await message.answer("расскажи мне, что случилось, и я постараюсь помочь")
    await state.set_state(UserStates.Angry)
   
@router.message(F.text == 'Я хочу поговорить с тобой')
async def chat_handler(message: Message, state: FSMContext):
    await message.answer("конечно, я всегда готов поговорить с тобой, булка ты моя")
    await state.set_state(UserStates.Chat)

@router.message(F.text == "Старт")
async def geto_start(message: Message, state : FSMContext):
    await start(message, state)
    
@router.message(F.text.contains("ну что ты"))
async def how_are_you(message: Message):
    await message.answer("у меня все хорошо котик, а ты там как?")
    
@router.message(F.text.contains("что делаешь?"))
async def how_are_you(message: Message):
    await message.answer("сижу, котик, а ты что там?")
    
@router.message(F.text.contains("когда спать?"))
async def how_are_you(message: Message):
    await message.answer("скорооо уже")
    
@router.message(F.text.contains("как ты там?"))
async def how_are_you(message: Message):
    await message.answer("все хорошооо, котик, а ты чтоо? как настроение?")
    
@router.message(F.text.contains("как настроение?"))
async def how_are_you(message: Message):
    await message.answer("все хорошооо, котик ❤️")
    
@router.message(F.text.contains("чего молчишь"))
async def how_are_you(message: Message):
    await message.answer("не молчу, это ты чего не пишешь!")
    
@router.message(Command("/bht_context"))
async def context_bh(message: Message):
    if str(message.chat.id) == Config().get_telegram_members()[0]:
        await usersCommandHandler.handle_behavior_tree_context(message)

@router.message(F.voice)
async def handle_voice_message(message: Message):
    if str(message.chat.id) in Config().get_telegram_members():
        await usersCommandHandler.handle_voice(message)

@router.message(F.photo)
async def handle_photo_message(message: Message):
    if str(message.chat.id) in Config().get_telegram_members():
        await usersCommandHandler.handle_photo(message)

@router.message(GoodNightFilter())
async def good_night(message : Message):
    if str(message.chat.id) in Config().get_telegram_members():
        await usersCommandHandler.handle_good_night(message)

@router.message(GoodMorningFilter())
async def good_morning(message : Message):
     if str(message.chat.id) in Config().get_telegram_members():
        await usersCommandHandler.handle_good_morning(message)
    
@router.message()
async def random_message(message : Message):
    if str(message.chat.id) in Config().get_telegram_members():
        await usersCommandHandler.handle_random_behavior(message)


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
