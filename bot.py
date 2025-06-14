from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging

# 🔐 Bot tokenni shu yerga to‘g‘ridan-to‘g‘ri yozing
TOKEN = "8183691124:AAEtvKgvuAQwuXdoyJV6x9dJDcwZC6qtJ0U"

# Logging sozlamasi
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# /start komandasi
def start(update: Update, context: CallbackContext):
    keyboard = [["Post yasash"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        "🚗 Assalomu alaykum! Bot ishlayapti. Menyudan 'Post yasash' ni tanlang.",
        reply_markup=reply_markup
    )

# Oddiy matnga javob
def echo(update: Update, context: CallbackContext):
    update.message.reply_text("Siz yuborgan xabar: " + update.message.text)

# Asosiy ishga tushirish funktsiyasi
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    print("✅ BOT ISHLAYAPTI")
    updater.idle()

if __name__ == '__main__':
    main()
