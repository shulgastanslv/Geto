from aiogram.fsm.state import State, StatesGroup

class ScheduleMessageStates(StatesGroup):
    waiting_for_recipient_id = State()
    waiting_for_message_content = State()
    waiting_for_scheduled_time = State()

class DeleteMessageStates(StatesGroup):
    waiting_for_message_id = State()