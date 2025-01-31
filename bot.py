import telebot
import openai

# توکن‌ها
TELEGRAM_TOKEN = "8004548236:AAEysYT6iCQXcl02OiAjb9U346ZxgIKgwZc"
OPENAI_API_KEY = "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"
ALLOWED_USER_ID = 2xqy1251

# تنظیم OpenAI
openai.api_key = OPENAI_API_KEY

# ایجاد ربات تلگرام
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# پایگاه دانش (در حافظه)
knowledge_base = {}

# بررسی کاربر مجاز
def is_allowed_user(user_id):
    return user_id == ALLOWED_USER_ID

# آموزش ربات
@bot.message_handler(commands=['train'])
def train_bot(message):
    if not is_allowed_user(message.from_user.id):
        bot.reply_to(message, "شما اجازه آموزش ربات را ندارید.")
        return

    try:
        data = message.text.split(" ", 1)[1]
        question, answer = data.split("|")
        knowledge_base[question.strip()] = answer.strip()
        bot.reply_to(message, "پرسش و پاسخ ذخیره شد!")
    except Exception:
        bot.reply_to(message, "فرمت صحیح: /train پرسش | پاسخ")

# پاسخ به سوالات
@bot.message_handler(func=lambda message: True)
def respond_to_user(message):
    user_message = message.text.strip()

    # بررسی پایگاه دانش
    if user_message in knowledge_base:
        bot.reply_to(message, knowledge_base[user_message])
        return

    # ارسال به OpenAI
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
    except Exception:
        bot.reply_to(message, "خطایی رخ داده است. دوباره تلاش کنید.")

# راه‌اندازی ربات
bot.polling()
