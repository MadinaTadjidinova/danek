import logging
from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_USER_ID

bot = None  # будет подставлен из bot.py

class FeedbackForm(StatesGroup):
    waiting_for_feedback = State()

async def start_feedback(message: Message, state: FSMContext):
    await message.answer("✍️ Пожалуйста, напишите ваш отзыв или предложение.")
    await state.set_state(FeedbackForm.waiting_for_feedback)

async def receive_feedback(message: Message, state: FSMContext):
    feedback = message.text
    try:
        await bot.send_message(
            ADMIN_USER_ID,
            f"📩 Новый отзыв от @{message.from_user.username or 'без ника'}:\n\n{feedback}"
        )
        await message.answer("✅ Спасибо! Ваш отзыв отправлен.")
    except Exception as e:
        logging.error(f"Ошибка при отправке отзыва: {e}")
    await state.clear()

def register_feedback_handlers(dp, bot_instance):
    global bot
    bot = bot_instance
    dp.message.register(start_feedback, F.text == "/feedback")
    dp.message.register(receive_feedback, FeedbackForm.waiting_for_feedback)