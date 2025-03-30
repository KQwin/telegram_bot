## main.py
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
import openai
from utils import is_premium, add_premium

TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if is_premium(user_id):
        update.message.reply_text("Xush kelibsiz, obuna foydalanuvchi! So‘rov yuboring:")
    else:
        buttons = [
            [InlineKeyboardButton("30 kun - $2", callback_data='pay_30')],
            [InlineKeyboardButton("1 yil - $10", callback_data='pay_365')],
        ]
        update.message.reply_text("Obuna bo‘lish uchun tanlang:", reply_markup=InlineKeyboardMarkup(buttons))


def handle_query(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not is_premium(user_id):
        update.message.reply_text("Ushbu xizmat faqat obunachilar uchun.")
        return
    question = update.message.text
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}]
    )
    answer = response.choices[0].message.content
    update.message.reply_text(answer)


def payment_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data.startswith("pay_"):
        add_premium(user_id)
        query.edit_message_text("Obuna faollashtirildi! Endi xizmatdan foydalanishingiz mumkin ✅")


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_query))
    dp.add_handler(CallbackQueryHandler(payment_handler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()


## utils.py
import json

def is_premium(user_id):
    try:
        with open("premium_users.json", "r") as f:
            data = json.load(f)
        return user_id in data.get("premium", [])
    except FileNotFoundError:
        return False

def add_premium(user_id):
    try:
        with open("premium_users.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"premium": []}
    if user_id not in data["premium"]:
        data["premium"].append(user_id)
        with open("premium_users.json", "w") as f:
            json.dump(data, f, indent=2)
