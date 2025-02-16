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
    response = requests.post(
        "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill",
        headers=headers,
        json=payload,
    )
    result = response.json()
    return result.get("generated_text", "متوجه نشدم، دوباره بپرسید.")

# تست اتصال به تلگرام
async def test_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        bot = await context.bot.get_me()
        await update.message.reply_text(f"اتصال به تلگرام برقرار است. نام بات: {bot.first_name}")
    except Exception as e:
        await update.message.reply_text(f"خطا در اتصال به تلگرام: {e}")

# تست اتصال به Hugging Face
async def test_huggingface(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = query_huggingface("test")
        if "generated_text" in response:
            await update.message.reply_text("اتصال به Hugging Face برقرار است.")
        else:
            await update.message.reply_text("خطا در اتصال به Hugging Face.")
    except Exception as e:
        await update.message.reply_text(f"خطا در اتصال به Hugging Face: {e}")

# تست عملکرد مدل Hugging Face
async def test_huggingface_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # ارسال یک درخواست ساده به مدل
        response = query_huggingface("Hello, how are you?")
        await update.message.reply_text(f"پاسخ مدل: {response}")
    except Exception as e:
        await update.message.reply_text(f"خطا در اجرای مدل Hugging Face: {e}")

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

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # اضافه کردن دستورات جدید
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("article", save_article))
    application.add_handler(CommandHandler("test_telegram", test_telegram))
    application.add_handler(CommandHandler("test_huggingface", test_huggingface))
    application.add_handler(CommandHandler("test_huggingface_model", test_huggingface_model))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
