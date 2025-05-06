import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")

# Лимит длины одного сообщения Telegram
TELEGRAM_MESSAGE_LIMIT = 4096

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Отправь мне сообщение, и я отвечу через OpenRouter!')

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # Сообщаем пользователю, что ответ генерируется
    await update.message.reply_text('Генерирую ответ... 🛠️')

    try:
        reply_text = get_openrouter_reply(user_message)

        # Проверка на длину сообщения
        if len(reply_text) > TELEGRAM_MESSAGE_LIMIT:
            # Делим длинный ответ на части
            for i in range(0, len(reply_text), TELEGRAM_MESSAGE_LIMIT):
                await update.message.reply_text(reply_text[i:i+TELEGRAM_MESSAGE_LIMIT])
        else:
            await update.message.reply_text(reply_text)

    except Exception as e:
        print(f"Ошибка при обращении к OpenRouter: {e}")
        await update.message.reply_text('Произошла ошибка при получении ответа от ИИ. Попробуйте позже. 🚨')

def get_openrouter_reply(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": OPENROUTER_MODEL,  # Теперь модель берётся из .env
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data, timeout=30)  # Таймаут 30 секунд
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка сети или OpenRouter: {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
