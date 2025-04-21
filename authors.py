import asyncio
from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import CHAT_ID, THREAD_ID
from aiogram.exceptions import TelegramBadRequest

bot = None  # будет подставлен из bot.py

async def send_team_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Команда", callback_data="team")],
        [InlineKeyboardButton(text="🤝 Партнёры", callback_data="partners")]
    ])
    await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text="Выберите раздел:",
        reply_markup=kb
    )

async def callback_handler(callback: CallbackQuery):
    if callback.data == "team":
        text = (
            "👤 Ахмет | Сооснователь\n"
            "📍 Каракол\n"
            "🌱 Философия, стратегия\n"
            "📬 @FocusNTiming\n\n"
            "👤 Бекжан | Сооснователь\n"
            "📍 Каракол\n"
            "🔥 Визуал и атмосфера\n"
            "📬 @bekzhandev"
        )
    else:
        text = (
            "🤝 Открыты к партнёрствам!\n"
            "• Совместные проекты\n"
            "• Онлайн инициативы\n"
            "📬 Пиши нам: @FocusNTiming"
        )

    try:
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=text,
            reply_markup=callback.message.reply_markup
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise

    await callback.answer()

def register_authors_handlers(dp, bot_instance):
    global bot
    bot = bot_instance
    dp.callback_query.register(callback_handler, F.data.in_({"team", "partners"}))



