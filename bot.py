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

# ===== 3. Load Google credentials =====
creds_json = os.environ.get("GOOGLE_CREDENTIALS")
if not creds_json:
    print("❌ GOOGLE_CREDENTIALS env var not found!")
    exit(1)
creds_info = json.loads(creds_json)

# ===== 4. Define scopes =====
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)

# ===== 5. Authorize gspread =====
client = gspread.authorize(creds)
sheet = client.open_by_key("12H87uDfhvYDyfuCMEHZJ4WDdcIvHpjn1xp2luvrbLaM").worksheet("realauto")

# ===== 6. Setup logging =====
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== Conversation states =====
CHOOSE_ROW, GET_IMAGES, GET_INITIAL, GET_3, GET_4, GET_5 = range(6)

# ===== /start handler =====
def start(update: Update, context: CallbackContext):
    keyboard = [["Post yasash"]]
    update.message.reply_text(
        "🚗 Assalomu alaykum! Menyudan 'Post yasash' ni tanlang.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ===== Entry to post creation =====
def post_yasash(update: Update, context: CallbackContext):
    update.message.reply_text("📌 Qaysi qatordagi mashinadan post tayyorlaymiz? Raqamni kiriting (masalan: 4)")
    return CHOOSE_ROW

# ===== Handle row choice =====
def choose_row(update: Update, context: CallbackContext):
    try:
        row = int(update.message.text)
        data = sheet.row_values(row)
        context.user_data['car'] = {
            'model': data[1] if len(data)>1 else 'NOMA’LUM',
            'year': data[2] if len(data)>2 else 'NOMA’LUM',
            'kraska': data[3] if len(data)>3 else 'NOMA’LUM',
            'probeg': data[4] if len(data)>4 else 'NOMA’LUM',
            'narx': data[5] if len(data)>5 else 'NOMA’LUM'
        }
        context.user_data['photos'] = []
        update.message.reply_text("📸 Iltimos, mashina rasmlarini yuboring. Tayyor bo‘lgach, 'Finish' deb yozing.")
        return GET_IMAGES
    except Exception as e:
        logger.error(f"Row error: {e}")
        update.message.reply_text("❌ To‘g‘ri qator raqamini kiriting.")
        return CHOOSE_ROW

# ===== Collect images =====
def get_images(update: Update, context: CallbackContext):
    text = update.message.text
    if text and text.lower() == 'finish':
        update.message.reply_text("💵 Boshlang‘ich to‘lov summasini kiriting (so‘m bilan raqam):")
        return GET_INITIAL
    if update.message.photo:
        context.user_data['photos'].append(update.message.photo[-1].file_id)
        return GET_IMAGES
    update.message.reply_text("❗ Iltimos, foto yuboring yoki 'Finish' deb yozing.")
    return GET_IMAGES

# ===== Get initial payment =====
def get_initial(update: Update, context: CallbackContext):
    context.user_data['initial'] = update.message.text
    update.message.reply_text("💰 3 yillik oylik to‘lovni kiriting (so‘m):")
    return GET_3

# ===== Get 3-year payment =====
def get_3(update: Update, context: CallbackContext):
    context.user_data['pay3'] = update.message.text
    update.message.reply_text("💰 4 yillik oylik to‘lovni kiriting (so‘m):")
    return GET_4

# ===== Get 4-year payment =====
def get_4(update: Update, context: CallbackContext):
    context.user_data['pay4'] = update.message.text
    update.message.reply_text("💰 5 yillik oylik to‘lovni kiriting (so‘m):")
    return GET_5

# ===== Finalize and post =====
def get_5(update: Update, context: CallbackContext):
    context.user_data['pay5'] = update.message.text
    c = context.user_data['car']
    photos = context.user_data['photos']
    # Agar 1 ta rasm bo‘lsa, oddiy reply_photo ishlatamiz
    if len(photos) == 1:
        update.message.reply_photo(photos[0])
    elif len(photos) > 1:
        media = [InputMediaPhoto(fid) for fid in photos]
        update.message.reply_media_group(media)

    # build text
    post = (f"🚗 #{c['model']}\n"
            f"📆 {c['year']} yil\n"
            f"💎 {c['kraska']}\n"
            f"🏎 {c['probeg']} km\n"
            f"💰 {c['narx']}$\n\n"
            f"Kapital bank\n"
            f"Boshlang‘ich to‘lov: {context.user_data['initial']} so‘m\n\n"
            f"3 yil: {context.user_data['pay3']} so‘m\n"
            f"4 yil: {context.user_data['pay4']} so‘m\n"
            f"5 yil: {context.user_data['pay5']} so‘m")

    update.message.reply_text(post)
    return ConversationHandler.END

# ===== Fallback echo =====
def echo(update: Update, context: CallbackContext):
    update.message.reply_text("❗Menyu bo‘yicha davom eting yoki /start yozing.")

# ===== Main =====
def main():
    updater = Updater(bot=bot, use_context=True)
    dp = updater.dispatcher

    conv = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Post yasash$'), post_yasash)],
        states={
            CHOOSE_ROW: [MessageHandler(Filters.text & ~Filters.command, choose_row)],
            GET_IMAGES: [MessageHandler((Filters.photo | Filters.text) & ~Filters.command, get_images)],
            GET_INITIAL: [MessageHandler(Filters.text & ~Filters.command, get_initial)],
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
    logger.info("✅ BOT ISHLAYAPTI")
    updater.idle()

if __name__ == '__main__':
    main()
