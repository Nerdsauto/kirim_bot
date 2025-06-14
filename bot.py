from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import logging
import gspread
from google.oauth2.service_account  import Credentials

# ===== 1. Telegram bot token =====
TOKEN = "8183691124:AAEtvKgvuAQwuXdoyJV6x9dJDcwZC6qtJ0U"  # TOKEN ni bu yerga to‘liq joylang

# ===== 2. Google Sheets API ulanish =====
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("12H87uDfhvYDyfuCMEHZJ4WDdcIvHpjn1xp2luvrbLaM").worksheet("realauto")

# ===== 3. Logging =====
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

CHOOSING_ROW = 1

# ===== 4. /start komandasi =====
def start(update: Update, context: CallbackContext):
    keyboard = [["Post yasash"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        "🚗 Assalomu alaykum! Menyudan 'Post yasash' ni tanlang.",
        reply_markup=reply_markup
    )

# ===== 5. Post yasash menyusi =====
def post_yasash(update: Update, context: CallbackContext):
    update.message.reply_text("📌 Qaysi qatordagi mashinadan post tayyorlaymiz? Raqamni kiriting (masalan: 4)")
    return CHOOSING_ROW

# ===== 6. Qator raqamiga qarab post yasash =====
def choose_row(update: Update, context: CallbackContext):
    try:
        row_number = int(update.message.text)
        row_data = sheet.row_values(row_number)

        # Ma’lumotlarni to‘g‘ri formatlash
        model = row_data[1] if len(row_data) > 1 else "NOMA’LUM"
        year = row_data[2] if len(row_data) > 2 else "NOMA’LUM"
        kraska = row_data[3] if len(row_data) > 3 else "NOMA’LUM"
        probeg = row_data[4] if len(row_data) > 4 else "NOMA’LUM"
        narx = row_data[5] if len(row_data) > 5 else "NOMA’LUM"

        post = f"""🚗 #{model}
📆 {year} yil
💎 {kraska}
🏎 {probeg}
💰 {narx}

Kapital bank
Boshlang'ich to'lov:
3 yil: ...
4 yil: ...
5 yil: ...

https://t.me/real_auto_uz"""

        update.message.reply_text("✅ Ma'lumotlar olindi. Tayyor shablon:\n\n" + post)
        return ConversationHandler.END

    except Exception as e:
        logging.error(f"Xato: {e}")
        update.message.reply_text("❌ Xatolik: Iltimos, faqat mavjud qator raqamini kiriting.")
        return CHOOSING_ROW

# ===== 7. Echo =====
def echo(update: Update, context: CallbackContext):
    update.message.reply_text("Siz yubordingiz: " + update.message.text)

# ===== 8. Main funktsiya =====
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^(Post yasash)$'), post_yasash)],
        states={CHOOSING_ROW: [MessageHandler(Filters.text & ~Filters.command, choose_row)]},
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    print("✅ BOT ISHLAYAPTI")
    updater.idle()

if __name__ == '__main__':
    main()
