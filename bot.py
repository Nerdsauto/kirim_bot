from telegram import Update, Bot, ReplyKeyboardMarkup, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import logging
import os
import json
import gspread
from google.oauth2.service_account import Credentials

# ===== 1. Telegram bot token =====
TOKEN = "8183691124:AAH-YtPHqPU9OQ_TrkssXY6EuA4zwUFLq3I"

# ===== 2. Remove webhook to avoid polling conflict =====
bot = Bot(token=TOKEN)
bot.delete_webhook(drop_pending_updates=True)

# ===== 3. Setup Google Sheets credentials from env =====
creds_json = os.environ.get("GOOGLE_CREDENTIALS")
if not creds_json:
    logging.error("❌ GOOGLE_CREDENTIALS environment variable not found!")
    exit(1)
creds_info = json.loads(creds_json)

# ===== 4. Define scopes and create credentials =====
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)

# ===== 5. Authorize gspread client =====
client = gspread.authorize(creds)
sheet = client.open_by_key("12H87uDfhvYDyfuCMEHZJ4WDdcIvHpjn1xp2luvrbLaM").worksheet("realauto")

# ===== 6. Setup logging =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== Conversation states =====
CHOOSING_ROW, GET_IMAGES, GET_3, GET_4, GET_5 = range(1, 6)

# ===== 7. /start command =====
def start(update: Update, context: CallbackContext):
    keyboard = [["Post yasash"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        "🚗 Assalomu alaykum! Menyudan 'Post yasash' ni tanlang.", reply_markup=reply_markup
    )

# ===== 8. Post creation entry =====
def post_yasash(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📌 Qaysi qatordagi mashinadan post tayyorlaymiz? Raqamni kiriting (masalan: 4)"
    )
    return CHOOSING_ROW

# ===== 9. Handle row number =====
def choose_row(update: Update, context: CallbackContext):
    try:
        row = int(update.message.text)
        data = sheet.row_values(row)
        context.user_data['data'] = {
            'model': data[1] if len(data) > 1 else 'NOMA’LUM',
            'year': data[2] if len(data) > 2 else 'NOMA’LUM',
            'kraska': data[3] if len(data) > 3 else 'NOMA’LUM',
            'probeg': data[4] if len(data) > 4 else 'NOMA’LUM',
            'narx': data[5] if len(data) > 5 else 'NOMA’LUM'
        }
        update.message.reply_text("📸 Endi mashina rasmlarini yuboring (bir nechta bo‘lishi mumkin). 'Finish' deb yozsangiz rasm olish tugaydi.")
        context.user_data['photos'] = []
        return GET_IMAGES
    except Exception as e:
        logger.error(f"Row error: {e}")
        update.message.reply_text("❌ Iltimos, faqat mavjud qator raqamini kiriting.")
        return CHOOSING_ROW

# ===== 10. Collect photos =====
def get_images(update: Update, context: CallbackContext):
    if update.message.text and update.message.text.lower() == 'finish':
        update.message.reply_text("💰 Iltimos, 3 yillik to‘lov summasini kiriting (faqat raqam).")
        return GET_3
    elif update.message.photo:
        # take highest resolution
        file_id = update.message.photo[-1].file_id
        context.user_data['photos'].append(file_id)
        update.message.reply_text("✅ Qabul qilindi! Yana rasm yuboring yoki 'Finish' deb yozing.")
        return GET_IMAGES
    else:
        update.message.reply_text("❗ Rasm yuboring yoki 'Finish' deb yozing.")
        return GET_IMAGES

# ===== 11. Get 3-year payment =====
def get_3(update: Update, context: CallbackContext):
    context.user_data['pay3'] = update.message.text
    update.message.reply_text("💰 4 yillik to‘lov summasini kiriting.")
    return GET_4

# ===== 12. Get 4-year payment =====
def get_4(update: Update, context: CallbackContext):
    context.user_data['pay4'] = update.message.text
    update.message.reply_text("💰 5 yillik to‘lov summasini kiriting.")
    return GET_5

# ===== 13. Get 5-year payment and finalize =====
def get_5(update: Update, context: CallbackContext):
    context.user_data['pay5'] = update.message.text
    d = context.user_data['data']
    photos = context.user_data['photos']
    post_text = f"🚗 #{d['model']}\n📆 {d['year']} yil\n💎 {d['kraska']}\n🏎 {d['probeg']} km\n💰 {d['narx']}$\n\n"
    post_text += f"Kapital bank\n3 yil: {context.user_data['pay3']}$\n4 yil: {context.user_data['pay4']}$\n5 yil: {context.user_data['pay5']}$\n"
    post_text += "\nhttps://t.me/real_auto_uz"
    # send media group if there are photos
    if photos:
        media = [InputMediaPhoto(pid) for pid in photos]
        update.message.reply_media_group(media)
    update.message.reply_text(post_text)
    return ConversationHandler.END

# ===== 14. Echo fallback =====
def echo(update: Update, context: CallbackContext):
    update.message.reply_text("❓ Iltimos menyudan foydalaning yoki /start komandasini yuboring.")

# ===== 15. Main function =====
def main():
    updater = Updater(bot=bot, use_context=True)
    dp = updater.dispatcher
    conv = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Post yasash$'), post_yasash)],
        states={
            CHOOSING_ROW: [MessageHandler(Filters.text & ~Filters.command, choose_row)],
            GET_IMAGES: [MessageHandler((Filters.photo | Filters.text) & ~Filters.command, get_images)],
            GET_3: [MessageHandler(Filters.text & ~Filters.command, get_3)],
            GET_4: [MessageHandler(Filters.text & ~Filters.command, get_4)],
            GET_5: [MessageHandler(Filters.text & ~Filters.command, get_5)]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(conv)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling(drop_pending_updates=True)
    logger.info("✅ BOT POLLING BOSHLANDI")
    updater.idle()

if __name__ == '__main__':
    main()
