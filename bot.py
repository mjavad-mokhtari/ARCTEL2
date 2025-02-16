import os
import json
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# دریافت توکن‌ها از متغیرهای محیطی
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")

# حافظه بلندمدت (در حافظه داخلی - برای حالت بلندمدت باید دیتابیس اضافه شود)
memory = []

# ارسال درخواست به Hugging Face
def query_huggingface(prompt):
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"inputs": prompt, "parameters": {"max_length": 500}}
    # تغییر مدل به DeepSeek-R1
    response = requests.post(
        "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-R1",
        headers=headers,
        json=payload,
    )
    result = response.json()
    # بررسی نتایج دریافت شده
    if isinstance(result, list):
        return result[0].get("generated_text", "متوجه نشدم، دوباره بپرسید.")
    return "خطا در ارتباط با مدل."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من ربات معماری هستم. سوالات خود را بپرسید یا مقاله ارسال کنید.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # ذخیره مکالمه در حافظه
    memory.append({"role": "user", "content": user_message})

    # ترکیب پیام‌های قبلی برای حافظه کوتاه‌مدت
    context_str = "\n".join([f"{m['role']}: {m['content']}" for m in memory[-5:]])

    # ارسال به مدل Hugging Face
    response = query_huggingface(context_str)

    # ذخیره پاسخ در حافظه
    memory.append({"role": "assistant", "content": response})

    await update.message.reply_text(response)

async def save_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        article = " ".join(context.args)
        memory.append({"role": "article", "content": article})
        await update.message.reply_text("مقاله ذخیره شد و در پاسخ‌های آینده استفاده خواهد شد.")
    else:
        await update.message.reply_text("لطفاً مقاله را پس از دستور /article وارد کنید.")

# دستور تست عملکرد مدل Hugging Face
async def test_huggingface_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ارسال یک prompt آزمایشی به مدل
    model_test_response = query_huggingface("این یک تست از مدل DeepSeek-R1 است.")
    
    # ارسال پاسخ مدل به کاربر
    await update.message.reply_text(f"نتیجه تست عملکرد مدل DeepSeek-R1: {model_test_response}")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("article", save_article))
    application.add_handler(CommandHandler("test_huggingface_model", test_huggingface_model))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
