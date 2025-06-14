from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# 🔐 Google Sheets API uchun scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# 🔑 creds.json fayldan kirish
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

# ===== 1. Telegram bot token =====
TOKEN = "8183691124:AAEtvKgvuAQwuXdoyJV6x9dJDcwZC6qtJ0U"  # <<< BU YERGA TOKEN QO‘YILADI

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

        model = row_data[1]
        year = row_data[2]
        kraska = row_data[3]
        probeg = row_data[4]
        narx = row_data[5]

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
        update.message.reply_text("❌ Xatolik: Iltimos, to‘g‘ri qator raqamini yuboring.")
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
