from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

router = Router()

# @router.message(F.text == "Имя")
# async def about_bot(message: Message):
#     await message.answer("Ответ")
