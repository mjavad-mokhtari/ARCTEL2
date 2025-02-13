import os
import telebot
from transformers import AutoModelForCausalLM, AutoTokenizer

# دریافت توکن‌ها از متغیرهای محیطی
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID"))

# راه‌اندازی مدل Hugging Face
model_name = "deepseek-ai/DeepSeek-R1"
tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=HF_API_KEY)
model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=HF_API_KEY)

# ایجاد ربات تلگرام
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# پایگاه دانش (در حافظه)
knowledge_base = {}

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

    if user_message in knowledge_base:
        bot.reply_to(message, knowledge_base[user_message])
        return

    try:
        inputs = tokenizer(user_message, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=150)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"خطایی رخ داد: {e}")

# راه‌اندازی ربات
bot.polling()
