import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging

# TOKEN faqat Environment Variables orqali olinadi
TOKEN = os.getenv("BOT_TOKEN")

# Logging sozlamasi
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    keyboard = [["Post yasash"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        "🚗 Assalomu alaykum! Post yaratish uchun menyudan foydalaning.",
        reply_markup=reply_markup
    )

def echo(update: Update, context: CallbackContext):
    update.message.reply_text("Siz yuborgan xabar: " + update.message.text)

def main():
    if not TOKEN:
        print("❌ [XATO] BOT_TOKEN topilmadi. Railway Environment Variables ichida BOT_TOKEN ni qo‘shing!")
        exit()

    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    print("✅ Bot muvaffaqiyatli ishga tushdi...")
    updater.idle()

if __name__ == '__main__':
    main()
