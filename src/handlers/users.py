import asyncio
from datetime import datetime
import random
from typing import List, Optional
from aiogram import Bot, Router
from aiogram.types import Message
from injector import inject, provider, singleton
from common.behavior_tree import BehaviorTree
from config import Config
from misc.keyboards import *
from repositories.user_repository import UserRepository

router = Router()

class UsersCommandHandler:
    
    @inject
    def __init__ (self, userRepository : UserRepository, behaviorTree : BehaviorTree) -> None:
        self.behaviorTree = behaviorTree
        self.userRepository = userRepository
        
    def __message_is_not_null(self, message) -> bool:
       return message is not None
   
    async def __good_morning(self, message : Message) -> bool:
        emojies = ["💞", "❤️", "🤍", "🖤"]
        number_of_emojies = random.randint(1, 3)
        random_emojies = ''.join(random.choices(emojies, k=number_of_emojies))
        nicknames = ["солнышко", "котенок", "буська", "котик", "жопка", "госпожа", "вредина", "прекрасная морда", "дорогая", "милая", "самая лучшая женщина в мире", 
                    "солнце", "котеночек", "пупс"]
        random_nickname = random.choice(nicknames)
        morning_greetings = ["доброе утро, ", 
                            "доброе утрооо, ", 
                            "дооброе утроо, ", 
                            "утречко доброе, "]
        final_morning_message = f"{random.choice(morning_greetings)} {random_nickname} {random_emojies}"
        await message.answer(final_morning_message)
        return True
   
    async def __send_message(self, message : Message, text, messages : Optional[List] = None):
        if messages is not None:
            await message.answer(random.choice(messages))
        else:
            await message.answer(text)
        return True
    
    async def __send_sticker(self, message : Message, sticker, stickers : Optional[List] = None):
        if stickers is not None:
            await message.answer_sticker(random.choice(stickers))
        else:
            await message.answer_sticker(sticker)
        return True
    
    async def good_morning(self, message : Message):
        
        condition_node = self.behaviorTree.add_condition(lambda: self.__message_is_not_null(message))
        message_text = message.text
        morning = self.behaviorTree.add_action(lambda: self.__good_morning(message_text))
        moods = ["как настроение котенок?", "как настроение, морда?", "как настроение?", "как настроение, жопка?"]
        introductory_questions = ["ну что ты котенок?", "ну что ты ?", "вредничаешь там?"]
        introductory = self.behaviorTree.add_action(random.choice([lambda: self.__send_message(message, "ну как ты там?", introductory_questions),
                                          lambda: self.__send_message(message, "как твое настроение?", moods)]))
        morning_sequence_node = self.behaviorTree.add_sequence([condition_node, 
                                                            morning, 
                                                            introductory])
        self.behaviorTree.update(morning_sequence_node)
        await self.behaviorTree.run()
        
    async def random_behavior(self, message : Message):
        
        message_text = message.text
        condition_node = self.behaviorTree.add_condition(lambda: self.__message_is_not_null(message_text))
        nicknames = ["солнышко", "котенок", "буська", "котик", "жопка", "госпожа", "вредина", "прекрасная морда", "дорогая", "милая", "самая лучшая женщина в мире", 
                    "солнце", "котеночек", "пупс"]
        random_nickname = random.choice(nicknames)
        first_message_questions = ["хочешь поговорить, ", "ну что ты, ", "как ты там, ", "я тут, ", "скучаешь там, ", "ну чтоо ты, "]
        
        first_message_ramdom_sticker = [
            'CAACAgIAAxkBAAEH7qRmyFo8FUWljxFcnpFw_IKXeWMNdgACChoAAojy0EtnWpcq_Ye04TUE',
            'CAACAgIAAxkBAAEH7p1myForICfvo5q5J4tqimgLxciOhQACjhYAAvcayUvqMHys4N1qTDUE',
            'CAACAgIAAxkBAAEH7pVmyFobEwf8gDUNh-BP_V7WT3AKyQACpBwAAp6NSUrsxt4FJ3d2eDUE',
            'CAACAgIAAxkBAAEH7pFmyFoVxQLtrUTAhu-yPd4IJzvzAwACjhwAAklRSUq8mKapt5umCzUE',
            'CAACAgIAAxkBAAEH7o1myFoQmtnU7qVIRLtcFg8BVPTLeQACriMAApGnQEq7EH8rWyMSOjUE',
            'CAACAgIAAxkBAAEIEO9mz3022xILcVbrFCeHVG5UTrtalQACfxMAAkfO2UuxS5hlg2Vr4zUE',
            'CAACAgIAAxkBAAEIEPFmz30-EhyIyEBM9Dx1lXU85XAbrAACNBIAAhPX2EsAAbFTK7Zm0XQ1BA',
            'CAACAgIAAxkBAAEIEPNmz31F0nrD227SaFcyQbwnUMZDcQACFxQAAlXX2Es_ehiLlrWrKDUE',
            'CAACAgIAAxkBAAEIEPVmz31O09B7kByzRUT7sEp0t0GgPgACxhMAAtGkSUjUeWvO3nGgcjUE',
            'CAACAgIAAxkBAAEIEPdmz31XUGbtZBuca_2Emxg7qaVrwAACkBUAArTlyUvP28AHDr-D6TUE',
            'CAACAgIAAxkBAAEIEP1mz31k5IQKFTdCjDttAAErfxoS4nUAAjgUAALRTMhLzAQ6pNA-xiA1BA'
        ]
        final_first_message = f"{random.choice(first_message_questions)} {random_nickname} ?"
        
        actions = [
        lambda: self.__send_message(message, final_first_message), 
        lambda: self.__send_message(message, "ты мой пупс, как ты там?"),
        lambda: self.__send_sticker(message, random.choice(first_message_ramdom_sticker))]
        
        first_message = self.behaviorTree.add_action(random.choice(actions))
        random_behavior_sequence_node = self.behaviorTree.add_sequence([condition_node, 
                                                            first_message])
        self.behaviorTree.update(random_behavior_sequence_node)
        await self.behaviorTree.run()
        
        
        


        

# @router.message(Command("help"))
# async def get_help(message : Message):
#     help_text = (
#         f"Привет, котенок, меня зовут Гето. Моя главная цель - быть рядом и оберегать тебя.\n"
        
#         f"Я запрограммирован присылать тебе сообщения и стараться поддерживать тебя в трудную минуту. Всё, что от тебя требуется - это нажать кнопку /start и начать диалог, если тебе хочется поговорить или тебе грустно.\n\n"
       
#         f"В меню ты найдешь следующие кнопки: \n"
#         f"1.Мне грустно, я хочу тепла\n"
#         f"2.Я очень зла, хочу выговориться\n"
#         f"3.Я хочу поговорить с тобой\n"
#         f"4.Перезагрузить\n"
        
#         f"\nЕсли произошел какой то глюк, нажимай 4 кнопочку и перезагрузи меня, я постараюсь работать нормально после перезагрузки)\n\n"
        
#         f"P.S Я могу повторять свои фразы и иногда путать контекст, но не злюкайся, пожалуйста. Я был создан всего за пару недель, и помни, что я тебя очень сильно люблю! ❤️❤️ (Твой котенок)!\n\n"
#     )
#     await message.answer(help_text)

# @router.message(Command("delete_user"))
# async def delete_user_handler(message: Message):
#     try:
#         # Пример команды: /delete_user <name>
#         text = message.text.split(maxsplit=1)
#         if len(text) < 2:
#             await message.answer("Usage: /delete_user <name>")
#             return

#         name = text[1]
#         user = userRepository.get_user_by_name(name)
#         if user:
#             userRepository.delete_user_by_id(user.id)
#             await message.answer(f"User {name} deleted.")
#         else:
#             await message.answer("User not found.")
#     except Exception as e:
#         await message.answer(f"Error: {str(e)}")
        
# @router.message(Command("get_user"))
# async def get_user_handler(message: Message):
#     try:
#         # Пример команды: /get_user <name>
#         text = message.text.split(maxsplit=1)
#         if len(text) < 2:
#             await message.answer("Usage: /get_user <name>")
#             return

#         name = text[1]
#         user = userRepository.get_user_by_name(name)
#         if user:
#             await message.answer(f"User found: ID {user.id}, Name {user.name}")
#         else:
#             await message.answer("User not found.")
#     except Exception as e:
#         await message.answer(f"Error: {str(e)}")

# @router.message(Command("get_all_users"))
# async def get_all_users_handler(message: Message):
#     try:
#         users = userRepository.get_all_users()
#         if users:
#             response = "\n".join(f"ID: {user.id}, Name: {user.name}" for user in users)
#             await message.answer(f"All users:\n{response}")
#         else:
#             await message.answer("No users found.")
#     except Exception as e:
#         await message.answer(f"Error: {str(e)}")   


# def get_time_based_answer(morning, afternoon, evening_night) -> str:
#             current_hour = datetime.now().hour
#             if 5 <= current_hour < 12:
#                 return random.choice(morning)
#             elif 12 <= current_hour < 21:
#                 return random.choice(afternoon)
#             else:
#                 return random.choice(evening_night)


#         emojies = ["💞", "❤️", "🤍", "🖤", "💗", "💓", "❣", "❤️‍🔥"]

        
#         evening_night_greetings = [
#             "Чего не спишь? ", "Ну что, ", "Что такое, ", "О чем думаешь? ", 
#             "Как провела день? ", "Что нового, ", "Скучаешь? ", "Приветик, ", "Как настроение, "
#         ]
        
#         afternoon_greetings = [
#             "Ну что ты, ", "Что такое, ", "Как дела, ", "Как ты там, ", 
#             "Что нового, ", "Что планируешь делать, ", "Что замышляешь, "
#         ]
        
#         greeting = get_time_based_answer(
#             morning_greetings, 
#             afternoon_greetings, 
#             evening_night_greetings
#         )
        
#         final_morning_message = f"{greeting} {random_nickname} {random_emojies}"
        
#         user_id = message.from_user.id
#         user = self.userRepository.get_user_by_id(user_id)
        
#         if user is None:
#             self.userRepository.add_user(user_id, message.from_user.full_name)
        
#         admin = Config().get_telegram_members()[0]
#         reply_markup = admin_panel if user_id == int(admin) else main