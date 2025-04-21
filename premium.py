import logging
from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from config import ADMIN_USER_ID, ADMIN_USER_ID_MAIN

bot = None  # будет подставлен из bot.py

ADMINS = [ADMIN_USER_ID, ADMIN_USER_ID_MAIN]  # список админов

class PaymentForm(StatesGroup):
    waiting_for_receipt = State()

async def start_payment(message: Message, state: FSMContext):
    await message.answer(
        "💳 Пожалуйста, отправьте сюда чек (фото, скрин или текст), подтверждающий вашу оплату."
    )
    await state.set_state(PaymentForm.waiting_for_receipt)

async def receive_receipt(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "без ника"

    # форвард чека и отправка сообщения всем админам
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve:{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{user_id}")
        ]
    ])

    for admin in ADMINS:
        await bot.forward_message(
            chat_id=admin,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        sent = await bot.send_message(
            admin,
            f"📥 <b>Новая заявка на Премиум-доступ</b> от @{username} (ID: <code>{user_id}</code>)",
            reply_markup=kb
        )
        if admin == ADMIN_USER_ID:
            bot._admin_msg = sent.message_id  # сохраняем только один для дальнейшего редактирования

    await message.answer("📤 Ваш чек отправлен на проверку. Ожидайте ответа.")
    await state.clear()

async def handle_admin_decision(callback: CallbackQuery):
    action, user_id = callback.data.split(":")
    user_id = int(user_id)

    if action == "approve":
        user_text = (
            "🎉 Ваша оплата подтверждена!\n\n"
            "Добро пожаловать в Премиум-доступ 💎\n"
            "Вы получили доступ к закрытому сообществу.\n\n"
            "👉 Перейдите в группу: https://t.me/your_private_group\n"
            "(Если ссылка не открывается — скопируйте и вставьте вручную)\n\n"
            "📌 Не забудьте включить уведомления, чтобы не пропустить важные материалы!"
        )
        admin_text = "✅ Оплата подтверждена"
    else:
        user_text = "🚫 Ваша оплата отклонена. Пожалуйста, свяжитесь с нами для уточнений."
        admin_text = "❌ Оплата отклонена"

    try:
        await bot.send_message(chat_id=user_id, text=user_text)
        try:
            await bot.edit_message_text(
                chat_id=ADMIN_USER_ID,
                message_id=bot._admin_msg,
                text=f"Статус: {admin_text}"
            )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise
                
    except Exception as e:
        logging.error(f"Ошибка при отправке пользователю или обновлении статуса: {e}")
        await callback.answer("❌ Что-то пошло не так.")
        return

    await callback.answer("Готово.")

def register_premium_handlers(dp, bot_instance):
    global bot
    bot = bot_instance
    dp.message.register(start_payment, F.text == "/pay")
    dp.message.register(receive_receipt, PaymentForm.waiting_for_receipt)
    dp.callback_query.register(handle_admin_decision, F.data.startswith("approve:") | F.data.startswith("reject:"))
