import asyncio
from datetime import datetime
import logging
import os
import random
import sys
import time
from injector import Injector
from handlers import router
from aiogram.client.default import DefaultBotProperties
from aiogram import F, Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import Config
from db_context import DbContext
from handlers import UserCommandHandler
from repositories import ScheduledMessageRepository
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ContentType
from filters import GoodMorningFilter, GoodNightFilter
from aiogram.fsm.context import FSMContext
from keyboards import admin_panel, main_panel
from setup import ServiceCollection
from states import DeleteMessageStates, ScheduleMessageStates, UserStates
from aiogram.client.session.aiohttp import AiohttpSession

injector = Injector([ServiceCollection()])
usersCommandHandler = injector.get(UserCommandHandler)
scheduledMessageRepository = injector.get(ScheduledMessageRepository)
config = Config() 
session = AiohttpSession(proxy='http://proxy.server:3128')
bot = Bot(config.get_telegram_token(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

db = injector.get(DbContext)
if not db.table_exists("users") and not db.table_exists("scheduled_messages"):
    db.create_all_tables()

@router.message(F.text == "помощь")
async def handler_help(message : Message):
    await usersCommandHandler.handle_help(message)

@router.message(F.text == "запланировать сообщение")
async def schedule_message_start(message: Message, state: FSMContext):
    if str(message.chat.id) == Config().get_telegram_members()[0]:
        await message.answer("✏️ введите *id получателя*:", parse_mode="Markdown")
        await state.set_state(ScheduleMessageStates.waiting_for_recipient_id)

@router.message(ScheduleMessageStates.waiting_for_recipient_id)
async def enter_recipient_id(message: Message, state: FSMContext):
    if str(message.chat.id) == Config().get_telegram_members()[0]:
        recipient_id = message.text
        await state.update_data(recipient_id=recipient_id)
        await message.answer("✏️ теперь введите *текст сообщения*:", parse_mode="Markdown")
        await state.set_state(ScheduleMessageStates.waiting_for_message_content)

@router.message(ScheduleMessageStates.waiting_for_message_content)
async def enter_message_content(message: Message, state: FSMContext):
    if str(message.chat.id) == Config().get_telegram_members()[0]:
        message_content = message.text
        await state.update_data(message_content=message_content)
        await message.answer(
            "📅 укажите *дату и время отправки* (в формате `YYYY-MM-DD HH:MM:SS`):",
            parse_mode="Markdown"
        )
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
            
            await message.answer(
                f"✅ сообщение успешно запланировано!\n\n"
                f"*дата и время отправки:* `{scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}`\n"
                f"*получатель ID:* `{recipient_id}`\n"
                f"*сообщение:* {message_content}",
                parse_mode="Markdown"
            )
        except ValueError:
            await message.answer("❌ неверный формат даты. пожалуйста, используйте формат: `YYYY-MM-DD HH:MM:SS`", parse_mode="Markdown")
        finally:
            await state.clear()

@router.message(F.text == "удалить запланированное сообщение")
async def delete_scheduled_message(message: Message, state: FSMContext):
    if str(message.chat.id) == Config().get_telegram_members()[0]:
        await message.answer("✏️ введите *id* сообщения, которое нужно удалить:", parse_mode="Markdown")
        await state.set_state(DeleteMessageStates.waiting_for_message_id)

@router.message(DeleteMessageStates.waiting_for_message_id)
async def delete_message_by_id(message: Message, state: FSMContext):
    try:
        message_id = int(message.text)
        scheduledMessageRepository.delete_message_by_id(message_id)
        await message.answer(f"✅ сообщение с *id {message_id}* успешно удалено.", parse_mode="Markdown")
    except ValueError:
        await message.answer("❌ неверный формат id. Пожалуйста, введите числовой id.", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"⚠️ ошибка при удалении сообщения: {str(e)}", parse_mode="Markdown")
    finally:
        await state.clear()

@router.message(F.text == "показать все запланированные сообщения")
async def show_all_scheduled_messages(message: Message):
    if str(message.chat.id) == Config().get_telegram_members()[0]:
        try:
            messages = scheduledMessageRepository.get_all_messages()
            
            if messages:
                response = "\n\n".join(
                    f"📨 *id:* `{msg.id}`\n"
                    f"👤 *получатель id:* `{msg.recipient_id}`\n"
                    f"💬 *сообщение:* {msg.message}\n"
                    f"⏰ *запланированное время:* `{msg.scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}`"
                    for msg in messages
                )
                await message.answer(f"📋 *все запланированные сообщения:*\n\n{response}", parse_mode="Markdown")
            else:
                await message.answer("📭 *запланированных сообщений нет.*", parse_mode="Markdown")
        except Exception as e:
            await message.answer(f"⚠️ *ошибка при получении сообщений:* {str(e)}", parse_mode="Markdown")

@router.message(CommandStart())
async def start(message : Message, state: FSMContext):
    if str(message.chat.id) == Config().get_telegram_members()[1]:
        await bot.send_message(message.chat.id, f"привет.", reply_markup=admin_panel)
    elif str(message.chat.id) == Config().get_telegram_members()[0]:
        hello_answers = ["привет котенок", "ну что ты, мелочь моя", "приветик, котик"]
        first_message = ["ну что ты ?", "как настроение?", "хочешь поговоришь?", "как ты там?", "у тебя все хорошо?", 
                         "о чем хочешь поговорить?"]
        await bot.send_message(message.chat.id, random.choice(hello_answers), reply_markup=main_panel)
        time.sleep(random.randint(1, 4))
        await bot.send_message(message.chat.id, random.choice(first_message))
    else:
        await bot.send_message(message.chat.id, f"привет.")
    await state.set_state(UserStates.Start)

@router.message(F.text == 'мне грустно, я хочу тепла')
async def sad_handler(message: Message, state: FSMContext):
    if str(message.chat.id) == Config().get_telegram_members()[0]:
        await usersCommandHandler.sad_handler(message)
        await state.set_state(UserStates.Sad)
    
@router.message(F.text == 'я очень зла, хочу выговориться')
async def angry_handler(message: Message, state: FSMContext):
    if str(message.chat.id) == Config().get_telegram_members()[0]:
        await usersCommandHandler.angry_handler(message)
        await state.set_state(UserStates.Angry)
   
@router.message(F.text.contains('я хочу поговорить с тобой'))
async def chat_handler(message: Message, state: FSMContext):
    if str(message.chat.id) == Config().get_telegram_members()[0]:
        await usersCommandHandler.handle_talk(message)
        await state.set_state(UserStates.Chat)

async def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)
    
@router.message(F.text == "перезагрузить")
async def geto_start(message: Message):
      await message.answer("перезагрузка ...")
      await restart_bot()

@router.message(F.text == "старт")
async def geto_start(message: Message, state : FSMContext):
    await start(message, state)

@router.message(F.text == "показать текущий контекст")
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

@router.message(F.sticker)
async def handle_sticker_message(message: Message):
    if str(message.chat.id) in Config().get_telegram_members():
        await usersCommandHandler.handle_sticker_message(message)


@router.message(GoodNightFilter())
async def handle_good_night(message : Message):
    if str(message.chat.id) in Config().get_telegram_members():
        await usersCommandHandler.handle_good_night(message)

@router.message(GoodMorningFilter())
async def handle_good_morning(message : Message):
     if str(message.chat.id) in Config().get_telegram_members():
        await usersCommandHandler.handle_good_morning(message)
        
@router.message(F.text.contains("как настроение"))
async def handle_how_are_you(message : Message):
    if str(message.chat.id) in Config().get_telegram_members():
        answers = ["все хорошо, котик, а ты как?", "все хорошооо", "все нормально, а ты там как?", "у меня все хорошо, а ты что там?", "все хорошо котик, а ты что там?"]
        await message.reply(random.choice(answers))
        
@router.message(F.text.contains("что делаешь"))
async def handle_what_are_you_doing(message : Message):
    if str(message.chat.id) in Config().get_telegram_members():
        answers = ["сижуу, котик", "сижуу", "жду когда напишет моя прекрасная женщина", "откисаю, а ты что там?", "сижу котик, а ты что там?"]
        await message.reply(random.choice(answers))
        
@router.message(F.text.contains("я устала"))
async def handle_what_are_you_doing(message : Message):
    if str(message.chat.id) in Config().get_telegram_members():
        await message.reply(random.choice("все хорошо котик, отдохни и снова в бой, ты у меня сильная мордочка!!!"))
        
@router.message(F.text.contains("умер"))
async def handle_what_are_you_doing(message : Message):
    if str(message.chat.id) in Config().get_telegram_members():
        await message.reply(random.choice("мы поговорим об этом лично, потерпи немного котик"))
        
@router.message()
async def handle_random_message(message : Message):
    if str(message.chat.id) in Config().get_telegram_members():
        positive_keywords = ["да", "все хорошо", "все нормально", "отлично", "конечно"]
        if any(word in message.text.lower() for word in positive_keywords):
            await usersCommandHandler.hande_forced_response(message)
        await usersCommandHandler.handle_random_behavior(message)


async def main() -> None:
    asyncio.create_task(usersCommandHandler.send_scheduled_messages(bot))
    asyncio.create_task(usersCommandHandler.update_context_background())
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
