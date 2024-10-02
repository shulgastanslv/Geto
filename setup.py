from injector import Injector, inject, Module, provider, singleton

from behavior_tree import BehaviorTree
from config import Config
from db_context import DbContext
from handlers import UserCommandHandler
from repositories import ScheduledMessageRepository, UserRepository


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
    def provide_scheduled_message_repository(self, db: DbContext) -> ScheduledMessageRepository:
        return ScheduledMessageRepository(db)
    
    @provider
    @singleton
    def provide_behavior_tree(self) -> BehaviorTree:
        return BehaviorTree()

    @provider
    def provide_user_command_handler(self, userRepository: UserRepository,  behaviorTree :  BehaviorTree, scheduledMessageRepository : ScheduledMessageRepository) -> UserCommandHandler:
        return UserCommandHandler(userRepository, behaviorTree, scheduledMessageRepository)