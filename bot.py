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

# --- ارسال درخواست به مدل Hugging Face (مدل سبک‌تر DeepSeek 7B) ---
def query_huggingface(prompt):
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"inputs": prompt, "parameters": {"max_length": 500}}
    
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/deepseek-ai/deepseek-llm-7b",
            headers=headers,
            json=payload,
        )
        result = response.json()
        if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
            return result[0]["generated_text"]
        return result.get("error", "متوجه نشدم، دوباره بپرسید.")
    except Exception as e:
        return f"خطا در ارتباط با مدل: {str(e)}"

# --- تست اتصال به Hugging Face ---
async def test_huggingface(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        test_response = query_huggingface("Hello, can you respond?")
        await update.message.reply_text(f"✅ تست اتصال به Hugging Face موفقیت‌آمیز بود:\n{test_response}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در اتصال به Hugging Face:\n{str(e)}")

# --- تست عملکرد مدل Hugging Face با ورودی مشخص ---
async def test_huggingface_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "معماری پایدار چیست؟"
    response = query_huggingface(prompt)
    await update.message.reply_text(
        f"✅ تست مدل Hugging Face با ورودی نمونه:\n"
        f"📝 پرسش: {prompt}\n"
        f"🧠 پاسخ مدل:\n{response}"
    )

# --- دستور شروع (راهنما) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام! من ربات معماری هستم. دستورات تست:\n"
        "🔧 /test_telegram - تست اتصال به تلگرام\n"
        "💡 /test_huggingface - تست اتصال به Hugging Face\n"
        "🧪 /test_huggingface_model - تست عملکرد مدل Hugging Face\n"
        "📚 /article [متن مقاله] - ذخیره مقاله\n"
        "✉️ پیام مستقیم - ارسال به مدل و دریافت پاسخ\n"
    )

# --- ذخیره مقاله در حافظه داخلی ---
async def save_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        article = " ".join(context.args)
        memory.append({"role": "article", "content": article})
        await update.message.reply_text("✅ مقاله ذخیره شد و در پاسخ‌های آینده استفاده خواهد شد.")
    else:
        await update.message.reply_text("⚠️ لطفاً مقاله را پس از دستور /article وارد کنید.")

# --- مدیریت پیام‌های متنی و پاسخ از مدل ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    memory.append({"role": "user", "content": user_message})
    context_str = "\n".join([f"{m['role']}: {m['content']}" for m in memory[-5:]])
    response = query_huggingface(context_str)
    memory.append({"role": "assistant", "content": response})
    await update.message.reply_text(response)

# --- تست اتصال به تلگرام ---
async def test_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ اتصال به تلگرام برقرار است.")

# --- اجرای اصلی برنامه ---
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # افزودن هندلرها برای دستورات و پیام‌ها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("article", save_article))
    application.add_handler(CommandHandler("test_telegram", test_telegram))
    application.add_handler(CommandHandler("test_huggingface", test_huggingface))
    application.add_handler(CommandHandler("test_huggingface_model", test_huggingface_model))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
