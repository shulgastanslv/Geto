from datetime import datetime
import time
import random
from typing import List, Optional
from aiogram import Bot, Router
from aiogram.types import Message
from injector import inject, provider, singleton
from behavior_tree import BehaviorTree, BehaviorTreeContext, ConditionNode, ActionNode, SequenceNode
from config import Config
from keyboards import *
from repositories import UserRepository

router = Router()

class UserCommandHandler:
    
    @inject
    def __init__ (self, userRepository : UserRepository, behaviorTree : BehaviorTree) -> None:
        self.behaviorTree = behaviorTree
        self.userRepository = userRepository
        self.emojies = ["💞", "❤️", "🤍", "🖤"]
        self.nicknames = ["солнышко", "котенок", "буська", "котик", "жопка", "госпожа", "вредина", "прекрасная морда", "дорогая", "милая", "самая лучшая женщина в мире", 
                    "солнце", "котеночек", "пупс"]
        self.first_message_questions = ["хочешь поговорить, ", "ну что ты, ", "как ты там, ", "я тут, ", "скучаешь там, ", "ну чтоо ты, "]
        self.stickers = [
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
            'CAACAgIAAxkBAAEIEP1mz31k5IQKFTdCjDttAAErfxoS4nUAAjgUAALRTMhLzAQ6pNA-xiA1BA',
            'CAACAgIAAxkBAAEIGIJm0Moou0mW3lAdBgSNyj2J_ZpKzgACJysAAp26IUlgaofnkUC5GDUE',
            'CAACAgIAAxkBAAEIGIRm0MouPHmEKxjQ8HseGxQqkg_7PAAC7CkAAh9BKUk3P5pqWUQQYTUE',
            'CAACAgIAAxkBAAEIGIZm0MozyBK_bgrmKzIX3usS7YPlawACxx8AAvqTKEkQdpZ9DFhQZTUE',
            'CAACAgIAAxkBAAEIGIhm0Mo5KaE9p0JZ6yHqAAGaW972N9EAAuMpAAKPXiBJfnGFvkC-PNg1BA',
            'CAACAgIAAxkBAAEIGIpm0MpAMN2AM3EX9jXJu0hIYSOMGwAClCQAAr5KIEmkjFtuaVoK3jUE',
            'CAACAgIAAxkBAAEIGIxm0MpF7cLpq_l1LKMzqUAEEylS5wACyx0AAgVrKUn_KQPL15mTdTUE',
            'CAACAgIAAxkBAAEIGI5m0MpKyHnVkKSAkVHg1XF7Rtak7QACaicAAl1nIUkzOlrxGXS_WjUE',
            'CAACAgIAAxkBAAEIGJBm0MpQR7NhSryV44SigmK4DeuooAAC3iwAAo60KUkkJTbYjlVE1jUE',
            'CAACAgIAAxkBAAEIGJJm0MpVzk8m3s3mugg2kmTTVeyDqgACyx0AAgVrKUn_KQPL15mTdTUE',
            'CAACAgIAAxkBAAEIGJRm0MpbsNS3gbHdo5t-Ile_vSqMvQACWSgAAmsoKUkpA0mygqBUBjUE',
            'CAACAgIAAxkBAAEIGJZm0Mv_Pi5IENtSyLz5KVz-S-QxZwACKFEAAu3HEUr2bVYxwf_tmDUE',
            'CAACAgIAAxkBAAEIGJpm0MwOoUn1JJDanDaP_1nuvBOYcAAC91cAAmfnGUpNSeTPG1OK9TUE',
            'CAACAgIAAxkBAAEIGJxm0MwWDPYr5-pqyFGJCIzVAa6Q3wACs0wAAu5aGUpUoZfJsCcwQDUE',
            'CAACAgIAAxkBAAEIGJ5m0MwccsDKjJJDhPK8Ibsx3YBRdQACel8AAsplEUqzvuiPXkNP1zUE',
            'CAACAgIAAxkBAAEIGKRm0Mwm85h3NtQZPNKr4ZJq4MiFXwACilMAApwTGEqShO-Z34bWXjUE',
            'CAACAgIAAxkBAAEIGKZm0MwtuMGfOGBZUSYtlCd3UTrOTwACplIAAuAFGEqGPvIsy8SQzjUE',
            'CAACAgIAAxkBAAEIGLBm0Mw7XityUjvY7M3r3kl6KzFIsAACikwAAmFVGUpxDzfdgL1cRjUE'
        ]
        
    def __handle_sleep(self, time_sleep) -> bool:
        time.sleep(time_sleep)
        return True
    
    async def __send_message(self, message: Message, text: str) -> bool:
        await message.answer(text)
        return True

    async def __send_sticker(self, message: Message, sticker: str) -> bool:
        await message.answer_sticker(sticker)
        return True
    
    async def handle_random_behavior(self, message : Message):
        
        condition_node = ConditionNode('message_is_not_none', lambda: message is not None)
        random_nickname = random.choice(self.nicknames)
        final_first_message = f"{random.choice(self.first_message_questions)} {random_nickname} ?"
        
        actions = [
        lambda: self.__send_message(message, final_first_message), 
        lambda: self.__send_message(message, "ну что ты, кит ты мой?"),
        lambda: self.__send_sticker(message, random.choice(self.stickers))]
        
        self.behaviorTree.update(SequenceNode([condition_node, ActionNode('handle_random_behavior', random.choice(actions))]))
        await self.behaviorTree.run()

    async def handle_good_night(self, message : Message):
        
        now = datetime.now().hour
        condition_node = ConditionNode('message_is_not_none', lambda: message is not None)
        if now < 21:
            answers = ["рано спатки, ты что", "уже спатки?", "пойдешь уже что ли", "устала там?", "чудо ты, уже пойдешь?"]
            self.behaviorTree.update(SequenceNode([
                condition_node,
                ActionNode('handle_good_night<21', lambda: self.__send_message(message, random.choice(answers)))
            ]))
            await self.behaviorTree.run()
            return True
        
        number_of_emojies = random.randint(1, 3)
        random_emojies = ''.join(random.choices(self.emojies, k=number_of_emojies))
        random_nickname = random.choice(self.nicknames)
            
        night_greetings = ["cпокойной ночи, ", 
                                "доброй ночи, ",
                                "сладких снов, ", 
                                "уже? ну хорошо, спокойной ночи, "]
            
        final_night_message = f"{random.choice(night_greetings)} {random_nickname} {random_emojies}"
        good_night_message = ActionNode('good_night_message', lambda: self.__send_message(message, final_night_message))
        good_night_sticker = ActionNode('good_night_sticker', lambda: self.__send_sticker(message, random.choice(self.stickers)))
            
        i_love_you_entries = [", я тебя очень сильно люблю!", 
                                ", я тебя очень-очень сильно люблю!!!", 
                                ", ты мой самый драгоценный алмаз",
                                ", я очень рад что ты у меня есть!", 
                                ", ты моя прелесть!"
                                ", ты настолько прекрасна, как туман в дождливый день",
                                ", знай, я всегда рядом!", 
                                ", помни что ты только моя, я тебя никогда и никому не отдам!!"]
            
        first_sequence = SequenceNode([condition_node, 
                                                                good_night_message, 
                                                                good_night_sticker])
            
        second_final_night_message = f"{random.choice(night_greetings)} {random_nickname}{random.choice(i_love_you_entries)} {random_emojies}"
        second_night_message = ActionNode('second_night_message', lambda: self.__send_message(message, second_final_night_message))
            
        kiss_messages = ["целую!!", "целуюю!", "целуюююю!!", "целую!!!"]
            
        second_night_message = ActionNode('second_night_message', lambda: self.__send_message(message, second_final_night_message))
        third_night_message = ActionNode('third_night_message', lambda: self.__send_message(message, random.choice(kiss_messages)))

        last_message = random.choice([
                ActionNode('dont_sit_long', lambda: self.__send_message(message, "не сиди долго!")),
                good_night_sticker
        ])
            
        second_sequence = SequenceNode([condition_node, 
                                                                second_night_message, 
                                                                good_night_sticker,
                                                                third_night_message,
                                                                last_message])
            
        night_sequence_node = random.choice([first_sequence, second_sequence])
            
        self.behaviorTree.update(night_sequence_node)
        await self.behaviorTree.run()
        
    async def handle_good_morning(self, message: Message):
        
        now = datetime.now().hour
        condition_node = ConditionNode('message_is_not_none', lambda: message is not None)
        
        if now > 5 and now < 12:
            morning_greetings = ["доброе утро, ", 
                                "доброе утрооо, ", 
                                "дооброе утроо, ", 
                                "утречко доброе, "]
            moods = ["как настроение котенок?", "как настроение, морда?", "как настроение?", "как настроение, жопка?"]
            introductory_questions = ["ну что ты котенок?", "ну что ты ?", "вредничаешь там?"]
            
            introductory = ActionNode('introductory_morning', random.choice([lambda: self.__send_message(message, random.choice(introductory_questions)),
                                            lambda: self.__send_message(message, random.choice(moods))]))
            
            final_morning_message = f"{random.choice(morning_greetings)} {random.choice(self.nicknames)} {random.choice(self.emojies)}"
            
            send_morning = ActionNode('send_morning', lambda : self.__send_message(message, final_morning_message))
            
            
            self.behaviorTree.update(SequenceNode([condition_node, 
                                                                send_morning, 
                                                                introductory]))
            await self.behaviorTree.run()
        else:
            answers = ["какое утро, мелочь ты", "сейчас день, какое утро", "только встала что ли? соня ты моя", "сейчас день, лыжа ты сонная",
                       "ты моя булка, какое утро"]
            self.behaviorTree.update(SequenceNode([condition_node, 
                                    ActionNode('not_morning', lambda : self.__send_message(message, random.choice(answers)))]))
            await self.behaviorTree.run()
            
    def handle_sleep(self, time_sleep) -> bool:
        time.sleep(time_sleep)
        return True

    async def handle_voice(self, message: Message):
        condition_node = ConditionNode('message_is_not_none', lambda: message is not None)
        
        first_answers = ["ура, хахаха, голосовое сообщение от моей госпожи", "сейчас послушаю котенок", "урааа, подскаст от моей любимой женщины!!"]
        second_answers = ["ууу, хехехе", "ты ж мой котик", "хехех, мелочь ты моя"]
        third_answers = ["пока что я не смогу тебе ответить, но когда я выйду, я все обязательно прослушаю!!", 
                         "я обязательно все послушаю котик, записывай гс почаще", "хехе, морда ты моя, если бы я мог сейчас услышать твой голос.."]
        
        send_first_message = ActionNode('send_voice_first_message', lambda : self.__send_message(message, random.choice(first_answers)), execute_once=True)
        send_second_message =  ActionNode('send_voice_second_message', lambda : self.__send_message(message, random.choice(second_answers)))
        send_third_message =  ActionNode('send_voice_third_message', lambda : self.__send_message(message, random.choice(third_answers)), execute_once=True)
        sleep_duration = ActionNode('sleep_duration', lambda : self.__handle_sleep(message.voice.duration))
        
        self.behaviorTree.update(SequenceNode([condition_node, 
                                               send_first_message, 
                                               sleep_duration, 
                                               send_second_message, 
                                               sleep_duration, send_third_message]))
        await self.behaviorTree.run()

    async def handle_photo(self, message: Message):
        await message.answer("ты ж мой милашик!")
        
    async def handle_behavior_tree_context(self, message: Message):
        actions = self.behaviorTree.context.get_completed_actions()
        print(str(actions))
        