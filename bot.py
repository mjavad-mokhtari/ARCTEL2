import os
import telebot
import openai

# دریافت متغیرهای محیطی
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ALLOWED_USER_ID = os.getenv("ALLOWED_USER_ID")

# تبدیل `ALLOWED_USER_ID` به عدد صحیح
if ALLOWED_USER_ID and ALLOWED_USER_ID.isdigit():
    ALLOWED_USER_ID = int(ALLOWED_USER_ID)
else:
    ALLOWED_USER_ID = None  # مقدار نامعتبر

# تنظیم کلید OpenAI
openai.api_key = OPENAI_API_KEY

# ایجاد ربات تلگرام
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# پایگاه دانش داخلی (در حافظه)
knowledge_base = {}

# بررسی مجاز بودن کاربر
def is_allowed_user(user_id):
    return ALLOWED_USER_ID is None or user_id == ALLOWED_USER_ID

# آموزش ربات با سوال و جواب‌های جدید
@bot.message_handler(commands=['train'])
def train_bot(message):
    if not is_allowed_user(message.from_user.id):
        bot.reply_to(message, "❌ شما اجازه آموزش ربات را ندارید.")
        return

    try:
        data = message.text.split(" ", 1)[1]
        question, answer = data.split("|")
        knowledge_base[question.strip()] = answer.strip()
        bot.reply_to(message, "✅ پرسش و پاسخ ذخیره شد!")
    except Exception:
        bot.reply_to(message, "❗ فرمت صحیح: /train پرسش | پاسخ")

# پاسخ به سوالات کاربران
@bot.message_handler(func=lambda message: True)
def respond_to_user(message):
    user_message = message.text.strip()

    # بررسی پایگاه دانش
    if user_message in knowledge_base:
        bot.reply_to(message, knowledge_base[user_message])
        return

    # ارسال درخواست به OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in architecture."},
                {"role": "user", "content": user_message},
            ],
        )
        answer = response["choices"][0]["message"]["content"]
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"⚠ خطایی رخ داده است: {str(e)}")

# راه‌اندازی ربات
bot.polling()
