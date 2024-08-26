from datetime import datetime
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from states.scheduled_message import DeleteMessageStates, ScheduleMessageStates
from aiogram.types import Message

router = Router()

# @router.message(F.text == "Запланировать сообщение")
# async def schedule_message_start(message: Message, state: FSMContext):
#     await message.answer("Введите ID получателя:")
#     await state.set_state(ScheduleMessageStates.waiting_for_recipient_id)

# @router.message(ScheduleMessageStates.waiting_for_recipient_id)
# async def enter_recipient_id(message: Message, state: FSMContext):
#     recipient_id = message.text
#     await state.update_data(recipient_id=recipient_id)
#     await message.answer("Введите текст сообщения:")
#     await state.set_state(ScheduleMessageStates.waiting_for_message_content)

# @router.message(ScheduleMessageStates.waiting_for_message_content)
# async def enter_message_content(message: Message, state: FSMContext):
#     message_content = message.text
#     await state.update_data(message_content=message_content)
#     await message.answer("Введите дату и время отправки (в формате YYYY-MM-DD HH:MM:SS):")
#     await state.set_state(ScheduleMessageStates.waiting_for_scheduled_time)

# @router.message(ScheduleMessageStates.waiting_for_scheduled_time)
# async def enter_scheduled_time(message: Message, state: FSMContext):
#     try:
#         scheduled_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M:%S")
#         user_data = await state.get_data()
#         recipient_id = int(user_data['recipient_id'])
#         message_content = user_data['message_content']
        
#         scheduledMessageRepository.add_message(
#             scheduler_id=message.from_user.id, 
#             recipient_id=recipient_id, 
#             message=message_content, 
#             scheduled_time=scheduled_time
#         )
        
#         await message.answer(f"Сообщение запланировано на {scheduled_time}.")
#     except ValueError:
#         await message.answer("Неверный формат даты. Пожалуйста, используйте формат YYYY-MM-DD HH:MM:SS")
#     finally:
#         await state.clear()

# @router.message(F.text == "Удалить запланированное сообщение")
# async def delete_scheduled_message(message: Message, state: FSMContext):
#     await message.answer("Введите ID сообщения, которое нужно удалить:")
#     await state.set_state(DeleteMessageStates.waiting_for_message_id)

# @router.message(DeleteMessageStates.waiting_for_message_id)
# async def delete_message_by_id(message: Message, state: FSMContext):
#     try:
#         message_id = int(message.text)
#         scheduledMessageRepository.delete_message_by_id(message_id)
#         await message.answer(f"Сообщение с ID {message_id} удалено.")
#     except ValueError:
#         await message.answer("Неверный формат ID. Пожалуйста, введите числовой ID.")
#     except Exception as e:
#         await message.answer(f"Ошибка при удалении сообщения: {str(e)}")
#     finally:
#         await state.clear()

# @router.message(F.text == "Показать все запланированные сообщения")
# async def show_all_scheduled_messages(message: Message):
#     try:
#         messages = scheduledMessageRepository.get_all_messages()
        
#         if messages:
#             response = "\n\n".join(
#                 f"ID: {msg.id}\n"
#                 f"Recipient ID: {msg.recipient_id}\n"
#                 f"Message: {msg.message}\n"
#                 f"Scheduled Time: {msg.scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}"
#                 for msg in messages
#             )
#             await message.answer(f"Все запланированные сообщения:\n\n{response}")
#         else:
#             await message.answer("Запланированных сообщений нет.")
#     except Exception as e:
#         await message.answer(f"Ошибка при получении сообщений: {str(e)}")

