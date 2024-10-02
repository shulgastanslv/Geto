import asyncio
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
from repositories import ScheduledMessageRepository, UserRepository
from sticker_loader import StickerLoader

router = Router()

class UserCommandHandler:
    
    @inject
    def __init__ (self, userRepository : UserRepository, behaviorTree : BehaviorTree, 
                  scheduledMessageRepository : ScheduledMessageRepository) -> None:
        self.behaviorTree = behaviorTree
        self.userRepository = userRepository
        self.scheduledMessageRepository = scheduledMessageRepository
        self.emojies = ["💞", "❤️", "🤍", "🖤"]
        self.nicknames = ["солнышко", "котенок", "буська", "котик", "жопка", "госпожа", "вредина", "прекрасная морда", "дорогая", "милая", "самая лучшая женщина в мире", 
                    "солнце", "котеночек", "пупс"]
        self.first_message_questions = ["хочешь поговорить, ", "ну что ты, ", "как ты там, ", "я тут, ", "скучаешь там, ", "ну чтоо ты, "]
        self.sticker_loader = StickerLoader('stickers.txt')
        self.stickers = self.sticker_loader._load_stickers()
        
    def __handle_sleep(self, time_sleep) -> bool:
        time.sleep(time_sleep)
        return True
    
    async def __send_message(self, message: Message, text: str) -> bool:
        await message.answer(text)
        return True
    
    async def __reply(self, message: Message, text: str) -> bool:
        await message.reply(text)
        return True
    
    async def __send_sticker(self, message: Message, sticker: str) -> bool:
        await message.answer_sticker(sticker)
        return True
    
    async def handle_sticker_message(self, message : Message):
        condition_node = ConditionNode('message_is_not_none', lambda: message is not None)
        sleep_duration = ActionNode('sleep_duration', lambda : self.__handle_sleep(random.randint(1, 5)))
        send_sticker = ActionNode('send_sticker', lambda : self.__send_sticker(message, random.choice(self.stickers)))
        self.behaviorTree.update(SequenceNode([condition_node, 
                                               sleep_duration, send_sticker]))
        await self.behaviorTree.run()
        
    async def angry_handler(self,  message : Message):
        time = datetime.now()
        
        condition_node = ConditionNode('angry_message_is_not_none', lambda: message is not None)
        sleep_duration = ActionNode('sleep_angry_duration', lambda : self.__handle_sleep(random.randint(1, 5)))
        
        first_answers = ["что случилось, злюка ты моя?", 
                         "не злись мордочка моя, я рядом, помни что я тебя очень сильно люблю!!❤️", 
                         "ну что ты котик, чего злишься там?",
                         "что случилось морда? давай поговорим",
                         "моя ты злюка, был бы я рядом, я бы тебя спокойно обнял и поцеловал, расскажи что случилось котик!!❤️",
                         "морда ты моя, что случилось?",
                         "что случилось жопка, ну ка рассказывай давай",
                         "мой ты котик, что у моего самого прекрасного котика случилось?",
                         "ну что ты там, чего ты злюкаешься, помни что я тебя очень сильно люблю❤️❤️",
                         "что случилось котик? давай выслушаю тебя, расскажи мне все то что тебя злит. ты моя душенька"]
        
        second_answers = [
            "помни, что ты моя самая-самая любимая женщина, я очень сильно люблю тебя. никогда не расстраивайся котик, можешь позлиться, отдохнуть, но потом обязательно в строй!",
            "помни котик, я рядом, ты моя прелестная морда, самая сильная и независимая женщина",
            "ты бы знала как я тебя люблююю!❤️❤️",
            "ты ж мой котенок, я тебя очень люблю",
            "я тебя очень-очень люблю, ты мой пушин, хехехе",
            "моя ты злюка, белка-люка, помни, я всегда рядом, ты со всем справишься, ты очень сильная!",
            "помни, я ментально рядом с тобой котик, позлись, отвлекись и давай дальше в бой. я скоро буду орядом и возьму все твои проблемы на себя. я твой мужчина, который всю жизнь будет рядом с тобой!! обещаю!!❤️❤️",
            "ну ка, белка-злюка, давай там, вдох-выдох, хехехех, люблююю тебя❤️❤️"
        ]
        
        not_action = ActionNode('not_angry_action', lambda: True, execute_once=True)
        actions_first = ActionNode('send_angry_first_message', lambda : self.__send_message(message, random.choice(first_answers)), execute_once=True)
        action_second = ActionNode('send_angry_second_message', lambda : self.__send_message(message, random.choice(second_answers)), execute_once=True)
        local_nicknames = ["буська мооя", "мордаа моя", "морда моя", "любовь моя", "котенок мой"]
        send_time_message = not_action
        c = ["случилось", "произошло", "такое"]
        if time.hour > 6 and time.hour < 12:
            send_time_message = ActionNode('send_angry_morning_time_message', lambda : self.__send_message(message, "что " + random.choice(c) + " с самого утра " + random.choice(local_nicknames) + " ?"), execute_once=True)
        elif time.hour > 12 and time.hour < 18:
            day_answers = ["что случилоось котик?", "что случилось котик?", "что случилось морда моя", "что случилось моя принцесса?", "что произошло котенок, все хорошо у тебя?"]
            send_time_message = ActionNode('send_angry_day_time_message', lambda : self.__send_message(message, random.choice(day_answers)), execute_once=True)
        elif time.hour > 18 and time.hour < 24:
            send_time_message = not_action
            
        self.behaviorTree.update(SequenceNode([condition_node, 
                                               send_time_message,
                                               actions_first,
                                               sleep_duration,
                                               action_second
                                               ]))
        await self.behaviorTree.run()
    
    async def sad_handler(self, message : Message):
        
        time = datetime.now()
        
        condition_node = ConditionNode('sad_message_is_not_none', lambda: message is not None)
        sleep_duration = ActionNode('sleep_sad_duration', lambda : self.__handle_sleep(random.randint(1, 5)))
        
        first_answers = ["ну что ты котенок? хочешь чтобы я тебя выслушал ?", 
                         "не грусти там, морда моя, и помни, я тебя очень сильно люблю!!❤️", 
                         "давай поговорим котенок, расскажи мне в чем дело? что у тебя на душе",
                         "что у тебя на душе, котик, расскажи мне",
                         "я рядом котенок, помни это, ты моя самая прекрасная женщина, самая красивая и самая милая, я тебя очень сильно люблю!!❤️",
                         "котик, я не знаю что у тебя случилось, и к сожалению в связи с тем что я в армию пока что не смогу узнать, но помни, мысленно я рядом с тобой. расскажи все что тебя гложит! я тебя выслушаю. ты у меня сильная и все пройдешь",
                         "у тебя что-то на душе котик? давай поговорим и все решим",
                         "ну чтооо ты, морда моя. давай рассказывай как ты",
                         "ну что ты там, морда моя, я тебя очень сильно люблю❤️❤️",
                         "что случилось котик? давай выслушаю тебя, расскажи мне все то что у тебя на душе. мне очень важно !!! я хочу чтобы моя любимая женщина никогда не грустила"]
        second_answers = [
            "помни, что ты моя самая любимая женщина, самая прекрасная и лучшая в мире, я бесконечно люблю тебя. я желаю видеть только улыбку на твоем прекрасном лице",
            "помни, котик, что ты мне очень дорога, я тебя просто обожаю",
            "ты моя душа котик, я тебя очень-очень люблю, не расстраивайся там, я рядом",
            "ты ж мой котенок, я тебя очень люблю",
            "я тебя безумно люблю, ты мой пушин",
            "ты ж моя морда, помни, я всегда рядом котик, ты со всем справишься, ты очень сильная котик!",
            "моя ты морда, ну что ты там раскисла, давай, не расстраивайся и попробуй отвлечься, я тебя очень люблю!!❤️❤️",
            "мелочь ты моя, ну что ты там, давай-ка, помни, я рядом котик!❤️❤️"
        ]
        
        stickers = [
            'CAACAgIAAxkBAAEIUGZm3D61crSZqtuWV5Wnn1Z0DHHFgAACjTMAAppSmUqAw97Qywn_WzYE',
            'CAACAgIAAxkBAAEIUGhm3D65bJnDJWF-64uLtVw4k_2gWAAC3DYAAnCdoUqltb72CIoNezYE',
            'CAACAgIAAxkBAAEIUGxm3D7D5cpCLK8UitFyN26kwhug9AACty4AAnNUoEogkXDX8UWQmjYE',
            'CAACAgIAAxkBAAEIUG5m3D7MQj65w3-ndC9IW6kXtLRgYQACyTEAAlHTmUotgShkPd2bszYE',
            'CAACAgIAAxkBAAEIUHBm3D7SGtxq9qzpUloRVwsv6Zpx-wACYy4AAszNmEq5GKHgl5dmMjYE',
            'CAACAgIAAxkBAAEIT89m3C0Eaf4Hhad27iXNyeg4r4FeBgACYzQAAuYXmErAFHbsE6_CUzYE',
            'CAACAgIAAxkBAAEIUHRm3D7dMPeUDgil_QPJeAhxsbiingACIjIAAq0soEpyQRPhKVTRIzYE',
            'CAACAgIAAxkBAAEIUHZm3D7oqOW5QeCqHL0jJ5LK86mukQAChiYAAn3bKUkYHIsndCL4LTYE',
            'CAACAgIAAxkBAAEIUHhm3D7tcnU3D2MFfbGoOBn3UkdqqwACxxwAAojnKEnWs7o3shbfVjYE',
            'CAACAgIAAxkBAAEIUHpm3D71q8v76X5a7rI0D-RLN28tOgAC3SIAAn3bKEl786kPFUfnUTYE',
            'CAACAgIAAxkBAAEIUHxm3D76ZX4oanAkdIqmvrCoHJ4YfQACLi0AAjs0KEnAfFgYHyWj6jYE',
            'CAACAgIAAxkBAAEIUH5m3D7_HWeRsoRyP8TTGMnG1R40HwACoyoAAuEiKEkiz35I0tRCJzYE',
            'CAACAgIAAxkBAAEIUIBm3D8D5lVnTRSnn8g82N-siUCfhwACHSgAAvfJKUkETvNifE_DazYE',
            'CAACAgIAAxkBAAEIUIJm3D8HPT0sY9yAavIUJEgOcSdi-AACNB0AAggGKElkgjaID_b3cTYE'
        ]        
        local_nicknames = ["котик", "морда моя", "мелочь моя", "котенок"]
        not_actions_answers = ["ну что ты ", "чего грустишь ", "не грусти ", "чего грустишь "]
        not_action_message = random.choice(not_actions_answers) + random.choice(local_nicknames)
        not_action = ActionNode('not_sad_action', lambda: self.__send_message(message, not_action_message), execute_once=True)
        send_first_message = [ActionNode('send_sad_first_message', lambda : self.__send_message(message, random.choice(first_answers)), execute_once=True), ActionNode('send_sad_second_message', lambda : self.__send_message(message, random.choice(second_answers)), execute_once=True)]
        send_sticker = [ActionNode('send_sad_sticker', lambda: self.__send_sticker(message, random.choice(stickers))), not_action]
        send_time_message = not_action
        
        c = ["случилось", "произошло", "такое"]
        
        if time.hour > 6 and time.hour < 12:
            send_time_message = ActionNode('send_sad_morning_time_message', lambda : self.__send_message(message, "что " + random.choice(c) + " с самого утра " + random.choice(local_nicknames) + " ?"), execute_once=True)
        elif time.hour > 12 and time.hour < 18:
            day_answers = ["что случилоось котик?", "что произошло котик? все хорошо у тебя там?", "что случилось морда моя", "как ты там, котик?", "что произошло котенок, все хорошо у тебя?"]
            send_time_message = ActionNode('send_sad_day_time_message', lambda : self.__send_message(message, random.choice(day_answers)), execute_once=True)
        elif time.hour > 18 and time.hour < 24:
            send_time_message = not_action
            
        last_random_sad_message = [
            
                                    """ты моя самая лучшая, самая красивая, самая милая, удивительная, добрая, прекрасная, сексуальная, умная, очаровательная, изящная. ты — буквально воплощение изящества и очарования. твоя прекрасная улыбка каждый раз наполняет меня своей любовью, радостью, нежностью этот прекрасный запах, успокаивающие нежные обьятия с такой любовью!!! обожаю❤️❤️❤️❤️❤️❤️❤️❤️""",
                                   """
                                   ты мой самый близкий и прекрасный человек! я очень рад что ты рядом, я безумно тебя люблю и ценю. мне грустно когда у тебя плохое настроение, и поэтому я искренне желаю чтобы у тебя всегда все было нормально/хорошо. помни, твоя улыбка прекрасна!! как и ты сама 
                                   """,
                                   """
                                   я очень сильно дорожу тобой и благодарен что ты присутствуешь в моей жизни, являясь ее огромной частью. честно не представляю что я бы делал без тебя, ты по истине прекрасный человек я верю что у нас все будет хорошо, мы пройдем через многие трудности которые нас ждут/будут ждать. я так же верю что ты тот человек которого я желаю видеть рядом с собой на своем жизненном пути и без которого мне будет/было бы сложно!!!
                                   """,
                                   """
                                   я всегда буду рядом когда нужно, всегда постараюсь позаботиться о тебе и сделать все что в моих силах чтобы моя девочка была счастлива . потому что я очень люблю тебя. ты моя душа и мое солнышко, мой самый дорогой партнер. ты прекрасна котенок, во всех аспектах. начиная от твоих внутренних переживаний насчет окружающих тебя людей, заканчивая заботой об мне. я ценю все черты твоего характера. ценю всю тебя. пусть ты и бываешь порой строга к себе, к своему телу, к своим поступкам. от себя могу сказать что я все люблю. буквально все. люблю твое прекрасное тело, и я не перестану это напоминать. хочу чтобы моя девочка запомнила это. я очень сильно люблю обниматься с тобой, целовать такую буську как ты и жмакать мои любимые ляшечки!!! 
                                   """,
                                   ]
        
        last_message = ActionNode('last_sad_message_not_action', lambda: True)
        
        if random.randint(1, 3) == 1:
            last_message = ActionNode('last_action_sad', lambda: self.__send_message(message, random.choice(last_random_sad_message)), execute_once=True)
        
        self.behaviorTree.update(SequenceNode([condition_node, 
                                               send_time_message,
                                               random.choice(send_first_message),
                                               sleep_duration,
                                               random.choice(send_sticker),
                                               last_message
                                               ]))
        await self.behaviorTree.run()
    
    async def handle_random_behavior(self, message : Message):
        
        condition_node = ConditionNode('random_message_is_not_none', lambda: message is not None)
        random_nickname = random.choice(self.nicknames)
        final_first_message = f"{random.choice(self.first_message_questions)} {random_nickname} ?"
        
        actions = [
        lambda: self.__send_message(message, final_first_message), 
        lambda: self.__send_message(message, "ну что ты, кит ты мой?"),
        lambda: self.__send_sticker(message, random.choice(self.stickers))]
        
        self.behaviorTree.update(SequenceNode([condition_node, 
                                               ActionNode('handle_random_behavior', random.choice(actions), execute_once=True)]))
        await self.behaviorTree.run()

    async def handle_good_night(self, message : Message):
        
        now = datetime.now().hour
        condition_node = ConditionNode('good_night_message_is_not_none', lambda: message is not None)
        if now < 21:
            answers = ["рано спатки, ты что", "уже спатки?", "пойдешь уже что ли", "устала там?", "чудо ты, уже пойдешь?"]
            self.behaviorTree.update(SequenceNode([
                condition_node,
                ActionNode('handle_good_night<21', lambda: self.__send_message(message, random.choice(answers)), execute_once=True),
                ActionNode('good_night_sticker', lambda: self.__send_sticker(message, random.choice(self.stickers)))
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
        condition_node = ConditionNode('morning_message_is_not_none', lambda: message is not None)
        
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
                                    ActionNode('not_morning', lambda : self.__send_message(message, random.choice(answers)), execute_once=True), 
                                    ActionNode('morning_send_sticker', lambda : self.__send_sticker(message, random.choice(self.stickers)))]))
            
            await self.behaviorTree.run()
            
    def handle_sleep(self, time_sleep) -> bool:
        time.sleep(time_sleep)
        return True

    async def handle_voice(self, message: Message):
        condition_node = ConditionNode('voice_message_is_not_none', lambda: message is not None)
        
        first_answers = ["ура, хахаха, голосовое сообщение от моей госпожи", "сейчас послушаю котенок", "урааа, подскаст от моей любимой женщины!!"]
        second_answers = ["ууу, хехехе", "ты ж мой котик", "хехех, мелочь ты моя"]
        third_answers = ["пока что я не смогу тебе ответить, но когда я выйду, я все обязательно прослушаю!!", 
                         "я обязательно все послушаю котик, записывай гс почаще", "хехе, морда ты моя, если бы я мог сейчас услышать твой голос.."]
        
        send_first_message = ActionNode('send_voice_first_message', lambda : self.__send_message(message, random.choice(first_answers)), execute_once=True)
        send_second_message =  ActionNode('send_voice_second_message', lambda : self.__send_message(message, random.choice(second_answers)))
        send_third_message =  ActionNode('send_voice_third_message', lambda : self.__send_message(message, random.choice(third_answers)), execute_once=True)
        sleep_duration = ActionNode('sleep_duration', lambda : self.__handle_sleep(message.voice.duration))
        send_sticker = ActionNode('send_sticker', lambda : self.__send_sticker(message, random.choice(self.stickers)))
        
        self.behaviorTree.update(SequenceNode([condition_node, 
                                               send_first_message, 
                                               sleep_duration, 
                                               send_second_message, 
                                               sleep_duration, send_third_message, send_sticker]))
        await self.behaviorTree.run()
        
    async def hande_forced_response(self, message: Message):
        positive_keywords = ["да", "все хорошо", "все нормально", "отлично", "конечно"]
        condition_contains_keywords = ConditionNode('message_contains_keywords', 
                                                lambda: any(word in message.text.lower() for word in positive_keywords))
        keyword_answers = ["ууу", "хехе", "уу, хехехехе", "хехехех", "уууу", "ураа", "ххехе", "уу, хехех", "хехех, уу"]
        sleep_duration = ActionNode('sleep_duration', lambda: self.__handle_sleep(message.text.__len__()))
        send_keyword_message = ActionNode('send_keyword_message', lambda: self.__reply(message, random.choice(keyword_answers)))
        keyword_sequence = SequenceNode([condition_contains_keywords, sleep_duration, send_keyword_message])
        self.behaviorTree.update(keyword_sequence)
        await self.behaviorTree.run()

    async def handle_photo(self, message: Message):
        condition_node = ConditionNode('message_is_not_none', lambda: message is not None)
        
        first_answers = ["уу, хехехех", "ууу, хехехе", "уууу"]
        second_answers = ["если бы я мог оценить фоточки 😭😭😭", "к сожалению мой создатель не предусмотрел возможность оценки фоточек", "если бы я видел что на фоточке.."]
        third_answers = ["я обязательно все потом посмотрю, шли побольше фоточек!!", 
                         "я обязательно все посмотрю котик, присылай фотки почаще", "хехе, морда ты моя, если бы я мог сейчас посмотреть на тебя"]
        
        send_first_message = ActionNode('send_photo_first_message', lambda : self.__send_message(message, random.choice(first_answers)), execute_once=True)
        send_second_message =  ActionNode('send_photo_second_message', lambda : self.__send_message(message, random.choice(second_answers)))
        send_third_message =  ActionNode('send_photo_third_message', lambda : self.__send_message(message, random.choice(third_answers)), execute_once=True)
        sleep_duration = ActionNode('sleep_duration', lambda : self.__handle_sleep(random.randint(1, 10)))
        send_sticker = ActionNode('send_sticker', lambda : self.__send_sticker(message, random.choice(self.stickers)))
        
        self.behaviorTree.update(SequenceNode([condition_node, 
                                               send_first_message, 
                                               sleep_duration, 
                                               send_second_message, 
                                               sleep_duration, send_third_message, send_sticker]))
        await self.behaviorTree.run()
        
    async def handle_behavior_tree_context(self, message: Message):
        actions = self.behaviorTree.context.get_completed_actions()
        
        if actions:
            text = "*✅ выполненные действия:*\n\n"
            for index, (func_id, name) in enumerate(actions, start=1):
                name = name.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')
                text += f"{index}. *id функции:* `{func_id}`\t*название:* {name}\n\n"
        else:
            text = "⚠️ *выполненные действия отсутствуют.*"

        await message.answer(text, parse_mode="Markdown")
        
    async def reset_context(self):
        self.behaviorTree.update_context(BehaviorTreeContext())
        print(f"контекст успешно обновлен в {datetime.now()}")
    
    async def handle_talk(self, message: Message):
        condition_node = ConditionNode('handle_talk_message_is_not_none', lambda: message is not None)
        
        first_answers = ["ну что ты котик", "как ты там, котенок", "мелочь ты моя"]
        second_answers = ["хочешь поговорить?", "давай поговорим", "хехех, хочешь поболтать?"]
        third_answers = ["пока что мы не можем поболтать много, но ты рассказывай обязательно все что пожелаешь, я тебя выслушаю", 
                         "хехехе", "ууу, хехехех"]
        
        send_first_message = ActionNode('send_talk_first_message', lambda : self.__send_message(message, random.choice(first_answers)), execute_once=True)
        send_second_message =  ActionNode('send_talk_second_message', lambda : self.__send_message(message, random.choice(second_answers)), execute_once=True)
        send_third_message =  ActionNode('send_talk_third_message', lambda : self.__send_message(message, random.choice(third_answers)), execute_once=True)
        sleep_duration = ActionNode('sleep_talk_duration', lambda : self.__handle_sleep(message.voice.duration))
        send_sticker = ActionNode('send_talk_sticker', lambda : self.__send_sticker(message, random.choice(self.stickers)))
        actions = [
        condition_node, 
        random.choice([send_first_message, sleep_duration, send_second_message, sleep_duration, send_third_message, send_sticker])
        ]
        self.behaviorTree.update(SequenceNode(actions))
        await self.behaviorTree.run()
        
    async def handle_help(self, message: Message):
        if str(message.chat.id) in Config().get_telegram_members():
            stickers = [
                'CAACAgIAAxkBAAEIUERm3DooRydEbEto64sdl0UV0AYzSwACyVkAAsSAEUpbQbYgbpD3kDYE',
                'CAACAgIAAxkBAAEIUEZm3Dowumy385k_SUMGQA5FycrbKwACfVMAAusoGUrMdZ-hSotszjYE',
                'CAACAgIAAxkBAAEIUEhm3Do2VseNg1QwCD-6SdQhdPbFtgACilMAApwTGEqShO-Z34bWXjYE',
                'CAACAgIAAxkBAAEIUEpm3Do8a930jrgOkArciCe_SdkTxwAC0lUAAoUUGUrdMauGQGNuMjYE',
                'CAACAgIAAxkBAAEIUExm3DpATaB1_nmwWOVkkvt1mE9PKwACzVYAAitrEEoYZXRed1LcEzYE',
                'CAACAgIAAxkBAAEIUE5m3DpH7rPqY-xwGc0I05eVovjQpQAC1lYAApw9EUqsTarNviAZnDYE',
                'CAACAgIAAxkBAAEIUFBm3DpMQ5wn6XAVoya9p1k6eZkzAAMNXwACx0wQSvIl1WxCVZsPNgQ',
                'CAACAgIAAxkBAAEIUFJm3DpTzyfOuwYKu9RP15-nnYt4kAACyVQAAtV-EEq6VHw_FMwj9zYE',
                'CAACAgIAAxkBAAEIUFZm3DpaRfbH1bd7HVYReFCwe72ysgACdFoAAqSWEEq_BPH28wLbEjYE',
                'CAACAgIAAxkBAAEIUFhm3DpfOPAhjpFf9eJKFpaW05y5rwAC3F8AApsJEUppZ6fPRfuTBDYE'
            ]
            text = (
                "привет, меня зовут гето, и моя главная цель — быть рядом, поддерживать тебя и поднимать твоё настроение в трудные моменты.\n\n"
                "чтобы начать наше общение, просто нажми на кнопку *старт*. если вдруг что-то пошло не так, не переживай: "
                "нажми на кнопку *перезагрузка*, и я постараюсь исправить ситуацию после перезапуска.\n\n"
                "P.S. порой я могу повторяться или немного сбиваться с темы. прошу прощения за это — я только учусь и был создан всего за несколько недель.\n\n"
                "и помни — я всегда здесь, чтобы поддержать тебя❤️❤️"
            )
            await message.answer(text, parse_mode="Markdown")
            if random.randint(0, 4) == 3:
                await message.answer_sticker(random.choice(stickers))

    async def send_scheduled_messages(self, bot : Bot):
        while True:
            current_time = datetime.now()
            messages = self.scheduledMessageRepository.get_scheduled_messages_for_sending(current_time)
            for message in messages:
                try:
                    await bot.send_message(message.recipient_id, message.message)
                    self.scheduledMessageRepository.delete_message_by_id(message.id)
                except Exception as e:
                    print(f"не удалось отправить сообщение {message.id}: {e}")
            await asyncio.sleep(1000)

    async def update_context_background(self):
        while True:
            try:
                await self.reset_context()
            except Exception as e:
                print(f"не удалось переопределить контекст: {e}")
            
            await asyncio.sleep(random.randint(1200, 1500))
            
            
    