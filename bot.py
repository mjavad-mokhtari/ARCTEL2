import os
import json
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")

memory = []

def query_huggingface(prompt):
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"inputs": prompt, "parameters": {"max_length": 500}}
    response = requests.post(
        "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-R1",
        headers=headers,
        json=payload,
    )
    return response.json()

async def test_huggingface_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        model_test_response = query_huggingface("این یک تست از مدل DeepSeek-R1 است.")
        await update.message.reply_text(f"پاسخ کامل مدل:\n{json.dumps(model_test_response, indent=2, ensure_ascii=False)}")
    except Exception as e:
        await update.message.reply_text(f"خطای تست مدل: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من ربات معماری هستم. سوالات خود را بپرسید یا مقاله ارسال کنید.")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test_huggingface_model", test_huggingface_model))
    application.run_polling()

if __name__ == '__main__':
    main()
