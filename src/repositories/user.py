from injector import inject
from db.db_context import DbContext
from db.models import User

class UserRepository:
    @inject
    def __init__(self, db : DbContext):
        self.db_context = db

    def add_user(self, user_id: str, name: str):
        session = self.db_context.get_session()
        try:
            new_user = User(id=user_id, name=name)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            print(f"User added with ID: {new_user.id}")
            return new_user
        except Exception as e:
            session.rollback()
            print(f"Failed to add user: {e}")
            raise
        finally:
            self.db_context.close_session(session)

    def get_user_by_id(self, user_id: int):
        session = self.db_context.get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                return user
            else:
                print("User not found.")
                return None
        except Exception as e:
            print(f"Failed to retrieve user: {e}")
            raise
        finally:
            self.db_context.close_session(session)

    def get_user_by_name(self, name: str):
        session = self.db_context.get_session()
        try:
            user = session.query(User).filter_by(name=name).first()
            if user:
                return user
            else:
                print("User not found.")
                return None
        except Exception as e:
            print(f"Failed to retrieve user: {e}")
            raise
        finally:
            self.db_context.close_session(session)

    def update_user_name(self, user_id: int, new_name: str):
        session = self.db_context.get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.name = new_name
                session.commit()
                session.refresh(user)
                print(f"User with ID {user_id} updated to name {new_name}.")
                return user
            else:
                print("User not found.")
                return None
        except Exception as e:
            session.rollback()
            print(f"Failed to update user: {e}")
            raise
        finally:
            self.db_context.close_session(session)

    def delete_user_by_id(self, user_id: int):
        session = self.db_context.get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                session.delete(user)
                session.commit()
                print(f"User with ID {user_id} deleted.")
            else:
                print("User not found.")
        except Exception as e:
            session.rollback()
            print(f"Failed to delete user: {e}")
            raise
        finally:
            self.db_context.close_session(session)

    def get_all_users(self):
        session = self.db_context.get_session()
        try:
            users = session.query(User).all()
            return users
        except Exception as e:
            print(f"Failed to retrieve users: {e}")
            raise
        finally:
            self.db_context.close_session(session)