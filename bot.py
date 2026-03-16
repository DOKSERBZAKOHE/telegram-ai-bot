import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен из переменных окружения
TOKEN = os.environ.get('TELEGRAM_TOKEN')

if not TOKEN:
    print("❌ ОШИБКА: TELEGRAM_TOKEN не найден!")
    exit(1)

# Включаем логирование
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text("✅ Бот работает! Отправь мне любое сообщение.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отвечает тем же сообщением"""
    await update.message.reply_text(f"Вы написали: {update.message.text}")

def main():
    print("🚀 Запуск бота...")
    
    # Создаем приложение
    app = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
