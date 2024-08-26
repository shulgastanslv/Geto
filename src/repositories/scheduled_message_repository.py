import datetime
from injector import inject
from db.common.db_context import DbContext
from db.models import ScheduledMessage
from sqlalchemy import func

class ScheduledMessageRepository:
    @inject
    def __init__(self, db: DbContext):
        self.db_context = db

    def add_message(self, scheduler_id: int, recipient_id: int, message: str, scheduled_time: datetime):
        session = self.db_context.get_session()
        try:
            new_message = ScheduledMessage(
                scheduler_id=scheduler_id,
                recipient_id=recipient_id,
                message=message,
                scheduled_time=scheduled_time
            )
            session.add(new_message)
            session.commit()
            session.refresh(new_message)
            print(f"Message scheduled with ID: {new_message.id}")
        except Exception as e:
            session.rollback()
            print(f"Failed to schedule message: {e}")
            raise
        finally:
            session.close()
            
    def get_scheduled_messages_for_sending(self, current_time: datetime):
        session = self.db_context.get_session()
        try:
            messages = session.query(ScheduledMessage).filter(
                ScheduledMessage.scheduled_time <= current_time
            ).all()
            return messages
        except Exception as e:
            print(f"Failed to retrieve messages: {e}")
            raise
        finally:
            session.close()

    def get_message_by_id(self, message_id):
        session = self.db_context.get_session()
        try:
            message = session.query(ScheduledMessage).filter_by(id=message_id).first()
            if message:
                return message
            else:
                print("Message not found.")
                return None
        finally:
            self.db_context.close_session(session)

    def delete_message_by_id(self, message_id):
        session = self.db_context.get_session()
        try:
            message = session.query(ScheduledMessage).filter_by(id=message_id).first()
            if message:
                session.delete(message)
                session.commit()
                print(f"Message with ID {message_id} deleted.")
            else:
                print("Message not found.")
        finally:
            self.db_context.close_session(session)

    def get_messages_by_scheduler_id(self, scheduler_id):
        session = self.db_context.get_session()
        try:
            messages = session.query(ScheduledMessage).filter_by(scheduler_id=scheduler_id).all()
            return messages
        finally:
            self.db_context.close_session(session)

    def get_all_messages(self):
        session = self.db_context.get_session()
        try:
            messages = session.query(ScheduledMessage).all()
            return messages
        finally:
            self.db_context.close_session(session)
    
    def get_message_count_for_user_on_date(self, user_id: int, date: datetime.date) -> int:
        session = self.db_context.get_session()
        try:
            start_of_day = datetime.datetime.combine(date, datetime.time.min)
            end_of_day = datetime.datetime.combine(date, datetime.time.max)
            
            count = session.query(func.count(ScheduledMessage.id)).filter(
                ScheduledMessage.recipient_id == user_id,
                ScheduledMessage.scheduled_time >= start_of_day,
                ScheduledMessage.scheduled_time <= end_of_day
            ).scalar()
            
            return count
        except Exception as e:
            print(f"Failed to retrieve message count: {e}")
            raise
        finally:
            session.close()
