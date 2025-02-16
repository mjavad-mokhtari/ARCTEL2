import os
import json
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")

memory = []

MODEL_ENDPOINTS = {
    "deepseek_v3": "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-V3",
    "janus_pro_7b": "https://api-inference.huggingface.co/models/deepseek-ai/Janus-Pro-7B"
}

TEST_COMMANDS = [
    "/test_telegram: تست اتصال به Telegram.",
    "/test_huggingface: تست اتصال به Hugging Face.",
    "/test_huggingface_model: تست عملکرد مدل Hugging Face.",
    "/test_deepseek_v3: تست مدل DeepSeek-V3.",
    "/test_janus_pro: تست مدل Janus-Pro-7B."
]

def query_huggingface(prompt, model_url):
    headers = {"Authorization": f"Bearer {HF_API_KEY}", "Content-Type": "application/json"}
    payload = {"inputs": prompt, "parameters": {"max_length": 500}}
    response = requests.post(model_url, headers=headers, json=payload)
    result = response.json()
    return result.get("generated_text", result.get("error", "خطا در پاسخ مدل"))

async def test_deepseek_v3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = query_huggingface("Hello, test from DeepSeek-V3", MODEL_ENDPOINTS["deepseek_v3"])
    await update.message.reply_text(f"پاسخ مدل DeepSeek-V3:\n{response}")

async def test_janus_pro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = query_huggingface("Hello, test from Janus-Pro-7B", MODEL_ENDPOINTS["janus_pro_7b"])
    await update.message.reply_text(f"پاسخ مدل Janus-Pro-7B:\n{response}")

async def list_tests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tests = '\n'.join(TEST_COMMANDS)
    await update.message.reply_text(f"دستورات تست موجود:\n{tests}")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("test_deepseek_v3", test_deepseek_v3))
    application.add_handler(CommandHandler("test_janus_pro", test_janus_pro))
    application.add_handler(CommandHandler("list_tests", list_tests))

    application.run_polling()

if __name__ == '__main__':
    main()
