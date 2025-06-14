from telegram import Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import logging
import os
import json
import gspread
from google.oauth2.service_account import Credentials

# ===== 1. Telegram bot token (shu yerga to'g'ridan yozing) =====
TOKEN = "8183691124:AAEtvKgvuAQwuXdoyJV6x9dJDcwZC6qtJ0U"

# ===== 2. Webhook o'chirish (faqat polling ishlashi uchun) =====
bot = Bot(token=TOKEN)
bot.delete_webhook(drop_pending_updates=True)

# ===== 3. Google Sheets API credential =====
creds_json = os.environ.get("GOOGLE_CREDENTIALS")
if not creds_json:
    logging.error("❌ GOOGLE_CREDENTIALS environment variable topilmadi!")
    exit(1)
creds_info = json.loads(creds_json)

# ===== 4. Scopes va credential yaratish =====
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)

# ===== 5. gspread bilan avtorizatsiya =====
client = gspread.authorize(creds)
sheet = client.open_by_key("12H87uDfhvYDyfuCMEHZJ4WDdcIvHpjn1xp2luvrbLaM").worksheet("realauto")

# ===== 6. Logging sozlamasi =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== 7. Conversation holatlari =====
CHOOSING_ROW = 1

# ===== 8. /start komandasi =====
def start(update: Update, context: CallbackContext):
    keyboard = [["Post yasash"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        "🚗 Assalomu alaykum! Menyudan 'Post yasash' ni tanlang.",
        reply_markup=reply_markup
    )

# ===== 9. Post yasash menyusi =====
def post_yasash(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📌 Qaysi qatordagi mashinadan post tayyorlaymiz? Raqamni kiriting (masalan: 4)"
    )
    return CHOOSING_ROW

# ===== 10. Qator raqamiga qarab post yasash =====
def choose_row(update: Update, context: CallbackContext):
    try:
        row_number = int(update.message.text)
        row_data = sheet.row_values(row_number)

        model = row_data[1] if len(row_data) > 1 else "NOMA’LUM"
        year = row_data[2] if len(row_data) > 2 else "NOMA’LUM"
        kraska = row_data[3] if len(row_data) > 3 else "NOMA’LUM"
        probeg = row_data[4] if len(row_data) > 4 else "NOMA’LUM"
        narx = row_data[5] if len(row_data) > 5 else "NOMA’LUM"

        post = f"""🚗 #{model}
📆 {year} yil
💎 {kraska}
🏎 {probeg} km
💰 {narx}$

Kapital bank
Boshlang'ich to'lov:
3 yil: ...
4 yil: ...
5 yil: ...

https://t.me/real_auto_uz"""

        update.message.reply_text(
            "✅ Tayyor shablon:\n\n" + post
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Xato choose_row: {e}")
        update.message.reply_text(
            "❌ Iltimos, mavjud qator raqamini kiriting."
        )
        return CHOOSING_ROW

# ===== 11. Echo =====
def echo(update: Update, context: CallbackContext):
    update.message.reply_text("Echo: " + update.message.text)

# ===== 12. Main funksiyasi =====
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    conv = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^(Post yasash)$'), post_yasash)],
        states={CHOOSING_ROW: [MessageHandler(Filters.text & ~Filters.command, choose_row)]},
        fallbacks=[CommandHandler("start", start)]
    )
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(conv)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling(drop_pending_updates=True)
    logger.info("✅ BOT POLLING BOSHLANDI")
    updater.idle()

if __name__ == '__main__':
    main()
