from telegram import Update, Bot, ReplyKeyboardMarkup, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import logging
import os
import json
import gspread
from google.oauth2.service_account import Credentials

# 1. Telegram bot token
TOKEN = "8183691124:AAH-YtPHqPU9OQ_TrkssXY6EuA4zwUFLq3I"

# 2. Remove webhook to avoid polling conflict
bot = Bot(token=TOKEN)
bot.delete_webhook(drop_pending_updates=True)

# 3. Load Google credentials
creds_json = os.environ.get("GOOGLE_CREDENTIALS")
if not creds_json:
    print("❌ GOOGLE_CREDENTIALS env var not found!")
    exit(1)
creds_info = json.loads(creds_json)

# 4. Define scopes
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)

# 5. Authorize gspread
client = gspread.authorize(creds)
sheet = client.open_by_key("12H87uDfhvYDyfuCMEHZJ4WDdcIvHpjn1xp2luvrbLaM").worksheet("realauto")

# 6. Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation states
ASK_CAR_NUMBER, ASK_CAR_YEAR, GET_IMAGES, GET_INITIAL, GET_3, GET_4, GET_5 = range(7)

def format_summa(summa):
    """Raqamni 6 100 000 ko‘rinishida formatlash uchun"""
    try:
        return "{:,}".format(int(summa)).replace(",", " ")
    except Exception:
        return summa

def start(update: Update, context: CallbackContext):
    keyboard = [["Post yasash"]]
    update.message.reply_text(
        "🚗 Assalomu alaykum! Menyudan 'Post yasash' ni tanlang.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

def post_yasash(update: Update, context: CallbackContext):
    update.message.reply_text("🚘 Avto raqamini kiriting (masalan: 01A123AA):")
    return ASK_CAR_NUMBER

def ask_car_number(update: Update, context: CallbackContext):
    car_number = update.message.text.strip().upper()
    rows = sheet.get_all_values()
    # Shu raqamga mos barcha qatorlarni yig'ing
    matches = [row for row in rows if len(row) > 0 and row[0].replace(" ", "").upper() == car_number.replace(" ", "")]
    if not matches:
        update.message.reply_text("❌ Bunday avto raqami topilmadi. Qaytadan kiriting:")
        return ASK_CAR_NUMBER
    if len(matches) == 1:
        # Faqat 1 ta moslik bo'lsa, to'g'ridan-to'g'ri davom etadi
        selected = matches[0]
        context.user_data['car'] = {
            'number': selected[0] if len(selected) > 0 else 'NOMA’LUM',
            'model': selected[1] if len(selected) > 1 else 'NOMA’LUM',
            'year': selected[2] if len(selected) > 2 else 'NOMA’LUM',
            'kraska': selected[3] if len(selected) > 3 else 'NOMA’LUM',
            'probeg': selected[4] if len(selected) > 4 else 'NOMA’LUM',
            'narx': selected[5] if len(selected) > 5 else 'NOMA’LUM'
        }
        context.user_data['photos'] = []
        update.message.reply_text("📸 Mashina rasmlarini yuboring. Tayyor bo‘lsa, 'Finish' deb yozing.")
        return GET_IMAGES
    else:
        # Bir nechta moslik bo'lsa, yillar ro'yxatini chiqaradi va so'raydi
        years = []
        for row in matches:
            if len(row) > 2 and row[2] not in years:
                years.append(row[2])
        context.user_data['car_number_matches'] = matches
        update.message.reply_text(
            "🔎 Bir nechta shu raqamli mashina topildi. Iltimos, avtomobil yilini kiriting. "
            f"Mavjud yillar: {', '.join(years)}"
        )
        return ASK_CAR_YEAR

def ask_car_year(update: Update, context: CallbackContext):
    car_year = update.message.text.strip()
    matches = context.user_data.get('car_number_matches', [])
    selected = None
    for row in matches:
        if len(row) > 2 and row[2] == car_year:
            selected = row
            break
    if not selected:
        update.message.reply_text("❌ Bunday yil topilmadi. Qaytadan yilni kiriting:")
        return ASK_CAR_YEAR
    context.user_data['car'] = {
        'number': selected[0] if len(selected) > 0 else 'NOMA’LUM',
        'model': selected[1] if len(selected) > 1 else 'NOMA’LUM',
        'year': selected[2] if len(selected) > 2 else 'NOMA’LUM',
        'kraska': selected[3] if len(selected) > 3 else 'NOMA’LUM',
        'probeg': selected[4] if len(selected) > 4 else 'NOMA’LUM',
        'narx': selected[5] if len(selected) > 5 else 'NOMA’LUM'
    }
    context.user_data['photos'] = []
    update.message.reply_text("📸 Mashina rasmlarini yuboring. Tayyor bo‘lsa, 'Finish' deb yozing.")
    return GET_IMAGES

def get_images(update: Update, context: CallbackContext):
    text = update.message.text
    if text and text.lower() == 'finish':
        update.message.reply_text("💵 Boshlang‘ich to‘lov summasini kiriting (so‘m):")
        return GET_INITIAL
    if update.message.photo:
        context.user_data['photos'].append(update.message.photo[-1].file_id)
        return GET_IMAGES
    update.message.reply_text("❗ Foto yuboring yoki 'Finish' deb yozing.")
    return GET_IMAGES

def get_initial(update: Update, context: CallbackContext):
    context.user_data['initial'] = update.message.text
    update.message.reply_text("💰 3 yillik oylik to‘lovni kiriting (so‘m):")
    return GET_3

def get_3(update: Update, context: CallbackContext):
    context.user_data['pay3'] = update.message.text
    update.message.reply_text("💰 4 yillik oylik to‘lovni kiriting (so‘m):")
    return GET_4

def get_4(update: Update, context: CallbackContext):
    context.user_data['pay4'] = update.message.text
    update.message.reply_text("💰 5 yillik oylik to‘lovni kiriting (so‘m):")
    return GET_5

def get_5(update: Update, context: CallbackContext):
    context.user_data['pay5'] = update.message.text
    c = context.user_data['car']
    photos = context.user_data['photos']
    # Format raqamlar
    initial = format_summa(context.user_data['initial'])
    pay3 = format_summa(context.user_data['pay3'])
    pay4 = format_summa(context.user_data['pay4'])
    pay5 = format_summa(context.user_data['pay5'])

    post = (f"🚗 #{c['model']}\n"
            f"Raqami: {c['number']}\n"
            f"📆 {c['year']} yil\n"
            f"💎 {c['kraska']}\n"
            f"🏎 {c['probeg']} km\n"
            f"💰 {c['narx']}$\n\n"
            f"Kapital bank\n"
            f"Boshlang‘ich to‘lov: {initial} so‘m\n"
            f"3 yil: {pay3} so‘m\n"
            f"4 yil: {pay4} so‘m\n"
            f"5 yil: {pay5} so‘m\n"
            f"https://t.me/real_auto_uz")

    # Avval media, keyin text
    if len(photos) == 1:
        update.message.reply_photo(photos[0], caption=post)
    elif len(photos) > 1:
        media = [InputMediaPhoto(fid) for fid in photos]
        media[0].caption = post
        update.message.reply_media_group(media)
    else:
        update.message.reply_text(post)
    return ConversationHandler.END

def echo(update: Update, context: CallbackContext):
    update.message.reply_text("❗Menyu bo‘yicha davom eting yoki /start yozing.")

def main():
    updater = Updater(bot=bot, use_context=True)
    dp = updater.dispatcher

    conv = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Post yasash$'), post_yasash)],
        states={
            ASK_CAR_NUMBER: [MessageHandler(Filters.text & ~Filters.command, ask_car_number)],
            ASK_CAR_YEAR: [MessageHandler(Filters.text & ~Filters.command, ask_car_year)],
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
