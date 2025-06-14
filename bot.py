from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging
import os
from dotenv import load_dotenv

# .env fayldan o'zgaruvchilarni yuklash
load_dotenv()

# 💬 Tokenni .env dan olish
TOKEN = os.getenv("8183691124:AAEtvKgvuAQwuXdoyJV6x9dJDcwZC6qtJ0U")

# 🔧 Logging sozlamasi
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ▶ /start komandasi funksiyasi
def start(update: Update, context: CallbackContext):
    keyboard = [["Post yasash"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        "Assalomu alaykum! Botga xush kelibsiz.\n\nPost yasash uchun menyudan foydalaning.",
        reply_markup=reply_markup
    )

# 🔁 Matnli xabarlarni qaytarish (sinov uchun)
def echo(update: Update, context: CallbackContext):
    update.message.reply_text(f"Siz yuborgan xabar: {update.message.text}")

# ▶ Botni ishga tushirish
def main():
    if not TOKEN:
        print("[XATO] BOT_TOKEN topilmadi. .env faylni tekshiring!")
        return

    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    # Komandalarni ulash
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Botni ishga tushurish
    updater.start_polling()
    print("✅ Bot ishga tushdi...")
    updater.idle()

if __name__ == "__main__":
    main()
