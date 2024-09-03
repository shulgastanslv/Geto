import re
from aiogram.types import Message
from aiogram.filters import Filter

class GoodNightFilter(Filter):
    def __init__(self) -> None:
        self.pattern = re.compile(
            r'\bспокойной\s+(ночи|ночки)\b',
            re.IGNORECASE
        )

    async def __call__(self, message: Message) -> bool:
        return bool(self.pattern.search(message.text))

class GoodMorningFilter(Filter):
    def __init__(self) -> None:
        self.pattern = re.compile(r'\bд(?:о|0)бр(?:о|0)(?:е|эй) ут(?:р(?:о|0)|0)\b', re.IGNORECASE)

    async def __call__(self, message: Message) -> bool:
        return bool(self.pattern.search(message.text))