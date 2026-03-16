"""
🤖 SUPER AI BOT - Мощный ассистент с искусственным интеллектом
Исправленная версия
"""

import logging
import os
import random
import asyncio
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from telegram.constants import ChatAction

# ================ НАСТРОЙКИ ================
TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TOKEN:
    print("❌ ОШИБКА: TELEGRAM_TOKEN не найден!")
    print("Добавьте переменную окружения на Render")
    exit(1)

BOT_NAME = "Super AI"
BOT_VERSION = "3.0"
MAX_HISTORY = 50

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================ БАЗА ДАННЫХ ================
class Database:
    def __init__(self):
        self.users: Dict[int, dict] = defaultdict(lambda: {
            'first_seen': datetime.now(),
            'messages_count': 0,
            'history': [],
            'rating': 0
        })
        self.stats = {
            'total_messages': 0,
            'total_users': 0,
            'start_time': datetime.now()
        }
    
    def get_user(self, user_id: int) -> dict:
        return self.users[user_id]
    
    def add_message(self, user_id: int, message: str, response: str):
        user = self.get_user(user_id)
        user['messages_count'] += 1
        user['history'].append({
            'time': datetime.now(),
            'message': message[:100],
            'response': response[:100]
        })
        if len(user['history']) > MAX_HISTORY:
            user['history'].pop(0)
        self.stats['total_messages'] += 1

db = Database()

# ================ AI ЯДРО ================
class AIEngine:
    def __init__(self):
        self.topics = {
            'привет': ['привет', 'здравствуй', 'хай', 'добрый'],
            'пока': ['пока', 'до свидания', 'увидимся'],
            'как дела': ['как дела', 'как жизнь', 'что делаешь'],
            'кто ты': ['кто ты', 'ты кто', 'как тебя зовут'],
            'спасибо': ['спасибо', 'благодарю'],
            'шутка': ['шутка', 'анекдот', 'рассмеши'],
            'факт': ['факт', 'интересно', 'знаешь ли ты'],
        }
    
    def get_response(self, user_id: int, message: str) -> str:
        message = message.lower()
        user = db.get_user(user_id)
        
        # Приветствия
        if any(word in message for word in ['привет', 'хай', 'здравствуй']):
            return random.choice([
                f"👋 Привет! Как твои дела?",
                f"🌟 Здравствуй! Рад тебя видеть!",
                f"✨ Привет-привет! Чем могу помочь?"
            ])
        
        # Прощания
        elif any(word in message for word in ['пока', 'до свидания', 'чао']):
            return random.choice([
                f"👋 До встречи! Заходи ещё!",
                f"💝 Пока-пока! Буду ждать!",
                f"✨ Увидимся! Хорошего дня!"
            ])
        
        # Как дела
        elif any(word in message for word in ['как дела', 'как жизнь']):
            return random.choice([
                f"😊 Отлично! Спасибо, что спросил!",
                f"🌟 У меня всё прекрасно! А у тебя?",
                f"✨ Работаю, общаюсь, расту!"
            ])
        
        # Кто ты
        elif any(word in message for word in ['кто ты', 'ты кто']):
            return f"🤖 Я {BOT_NAME} - твой AI помощник! Могу общаться на разные темы."
        
        # Спасибо
        elif any(word in message for word in ['спасибо', 'благодарю']):
            return random.choice([
                f"🙏 Пожалуйста! Рад помочь!",
                f"❤️ Обращайся ещё!",
                f"🌟 Для меня это удовольствие!"
            ])
        
        # Шутки
        elif any(word in message for word in ['шутка', 'анекдот', 'рассмеши']):
            jokes = [
                "Почему программисты путают Хэллоуин и Рождество? Oct 31 == Dec 25! 🎃➡️🎄",
                "— Дорогой, ты меня любишь?\n— Конечно!\n— А докажи!\n— sudo prove love 👨‍💻",
                "Студент на экзамене:\n— Что такое цикл?\n— Это когда одно и то же повторяется много раз... как мои попытки сдать этот экзамен! 😅"
            ]
            return random.choice(jokes)
        
        # Факты
        elif any(word in message for word in ['факт', 'интересно']):
            facts = [
                "🧠 Осьминоги имеют ТРИ сердца!",
                "🌍 В Антарктиде есть реки подо льдом!",
                "🦒 Жирафы спят всего 30 минут в день!",
                "🍌 Бананы - это ягоды, а не фрукты!"
            ]
            return random.choice(facts)
        
        # Общие ответы
        general = [
            "🌟 Интересно! Расскажи подробнее...",
            "🤔 Хм, я понял. А что еще?",
            "✨ Продолжай, я слушаю!",
            "💫 Ух ты! А как ты к этому пришел?",
            "📝 Понял тебя. Есть что добавить?"
        ]
        
        # Иногда добавляем статистику
        if random.random() < 0.1:
            return random.choice(general) + f"\n\n📊 Мы уже отправили {user['messages_count']} сообщений!"
        
        return random.choice(general)

ai_engine = AIEngine()

# ================ КОМАНДЫ ================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    first_name = user.first_name or "друг"
    
    db.get_user(user.id)
    db.stats['total_users'] = len(db.users)
    
    keyboard = [
        [InlineKeyboardButton("🤖 Обо мне", callback_data='about'),
         InlineKeyboardButton("📊 Статистика", callback_data='stats')],
        [InlineKeyboardButton("🎲 Факт", callback_data='fact'),
         InlineKeyboardButton("😄 Шутка", callback_data='joke')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome = f"""
🌟 **Привет, {first_name}!** Я **{BOT_NAME}**!

📊 Пользователей: {db.stats['total_users']}
💬 Сообщений: {db.stats['total_messages']}

👇 **Просто напиши мне что-нибудь!**
    """
    
    await update.message.reply_text(welcome, reply_markup=reply_markup, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    text = f"""
📊 **Твоя статистика:**
• Сообщений: {user['messages_count']}
• В истории: {len(user['history'])}
• Рейтинг: {user['rating']} ⭐️
    """
    await update.message.reply_text(text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = f"""
🤖 **{BOT_NAME} v{BOT_VERSION}**

✅ Понимает разные темы
✅ Помнит историю
✅ Рассказывает шутки
✅ Делится фактами

Создан с ❤️
    """
    await update.message.reply_text(text, parse_mode='Markdown')

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = ai_engine.get_response(update.effective_user.id, "шутка")
    await update.message.reply_text(response)

async def fact_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = ai_engine.get_response(update.effective_user.id, "факт")
    await update.message.reply_text(response)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message = update.message.text
    
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )
    
    response = ai_engine.get_response(user.id, message)
    db.add_message(user.id, message, response)
    
    await update.message.reply_text(response)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'about':
        await about_command(update, context)
    elif query.data == 'stats':
        await stats_command(update, context)
    elif query.data == 'fact':
        await fact_command(update, context)
    elif query.data == 'joke':
        await joke_command(update, context)

# ================ ЗАПУСК ================

def main():
    print(f"""
    ╔════════════════════════════╗
    ║  🤖 {BOT_NAME} v{BOT_VERSION}  ║
    ║      ЗАПУСК НА RENDER      ║
    ╚════════════════════════════╝
    """)
    
    # ВАЖНО: Правильный способ создания приложения
    app = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("joke", joke_command))
    app.add_handler(CommandHandler("fact", fact_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ Бот запускается...")
    app.run_polling()

if __name__ == "__main__":
    main()
