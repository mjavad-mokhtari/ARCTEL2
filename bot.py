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
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill",
            headers=headers,
            json=payload,
        )
        
        # چاپ وضعیت HTTP و محتوای پاسخ دریافتی برای بررسی ساختار داده
        print(f"HTTP Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        # بررسی اینکه آیا پاسخ از نوع لیست است یا دیکشنری
        try:
            result = response.json()
            if isinstance(result, list):
                # اگر پاسخ از نوع لیست باشد، باید به عنصر اول آن دسترسی پیدا کنیم
                print(f"Received list: {result}")
                return result[0].get("generated_text", "متوجه نشدم، دوباره بپرسید.")
            elif isinstance(result, dict):
                # اگر پاسخ از نوع دیکشنری باشد، به روش قبلی دسترسی پیدا می‌کنیم
                return result.get("generated_text", "متوجه نشدم، دوباره بپرسید.")
            else:
                return "پاسخ غیرمنتظره از Hugging Face دریافت شد."
        except Exception as e:
            return f"خطا در پردازش پاسخ: {e}"

    except Exception as e:
        return f"خطا در ارسال درخواست به Hugging Face: {e}"

# دستور شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من ربات معماری هستم. سوالات خود را بپرسید یا مقاله ارسال کنید.")

# دستور تست اتصال به Telegram
async def test_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("اتصال به تلگرام برقرار است!")

# دستور تست اتصال به Hugging Face
async def test_huggingface(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hf_test_response = query_huggingface("آیا ارتباط با هاگینگ فیس برقرار است؟")
    await update.message.reply_text(f"نتیجه تست اتصال به Hugging Face: {hf_test_response}")

# دستور تست عملکرد مدل Hugging Face
async def test_huggingface_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    model_test_response = query_huggingface("این یک تست از مدل Hugging Face است.")
    await update.message.reply_text(f"نتیجه تست عملکرد مدل Hugging Face: {model_test_response}")

# مدیریت پیام‌ها
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

# ذخیره مقاله
async def save_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        article = " ".join(context.args)
        memory.append({"role": "article", "content": article})
        await update.message.reply_text("مقاله ذخیره شد و در پاسخ‌های آینده استفاده خواهد شد.")
    else:
        await update.message.reply_text("لطفاً مقاله را پس از دستور /article وارد کنید.")

# راه‌اندازی ربات
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # اضافه کردن دستورات به ربات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test_telegram", test_telegram))  # اضافه کردن دستور تست اتصال به تلگرام
    application.add_handler(CommandHandler("test_huggingface", test_huggingface))  # اضافه کردن دستور تست اتصال به Hugging Face
    application.add_handler(CommandHandler("test_huggingface_model", test_huggingface_model))  # اضافه کردن دستور تست عملکرد مدل
    application.add_handler(CommandHandler("article", save_article))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # راه‌اندازی ربات
    application.run_polling()

if __name__ == '__main__':
    main()
