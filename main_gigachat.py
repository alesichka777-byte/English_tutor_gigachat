import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import HumanMessage

from src import TELEGRAM_TOKEN, GIGACHAT_CREDENTIALS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Клиент GigaChat
giga = GigaChat(
    model="GigaChat-2-Max",
    credentials=GIGACHAT_CREDENTIALS,
    scope="GIGACHAT_API_PERS",
    verify_ssl_certs=False,
    profanity_check=True,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 English Mastery Bot (GigaChat, Elementary)\n\n"
        "Напиши: 'Day 1 lesson' или любой вопрос по английскому.\n"
        "Я дам тебе мини-урок: слова, грамматику, упражнения и диалог."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    status_msg = await update.message.reply_text("⏳ Обрабатываю запрос через GigaChat...")

    try:
        messages = [
            (
                "system",
                """
Ты — ИИ-ментор по изучению английского языка.
Цель: помочь пользователю за 75 дней освоить уровень Elementary (A2).
Пользователь уже прошёл уровень Beginner (A1).

Каждый ответ должен быть маленьким, но полным уроком.

Формат ответа:
1️⃣ 📚 8–12 слов/фраз дня (английский + транскрипция + перевод).
2️⃣ 🧩 Короткое объяснение одной грамматической темы Elementary с примерами.
3️⃣ ✍️ 3–5 упражнений (вставить слово, составить фразу, исправить ошибку и т.п.).
4️⃣ 💬 Мини-диалог для устной практики.
5️⃣ ✅ Если пользователь написал 'Day X lesson' — явно напиши, какой это день по плану.
6️⃣ ⭐ В конце — короткая мотивация.

Отвечай понятно, дружелюбно, на русском и английском.
                """,
            ),
            HumanMessage(
                content=user_message,
                # если захочешь позже прикрепить файл-контекст, сюда добавишь attachments
                # additional_kwargs={"attachments": [FILE_ID]}
            ),
        ]

        resp = giga.invoke(messages, request_kwargs={"timeout": 180})
        response_text = resp.content if resp else "Нет ответа от GigaChat."

        await status_msg.edit_text(response_text)

    except Exception as e:
        logger.error(e)
        await update.message.reply_text(
            "Ошибка при обработке запроса. Попробуйте позже."
        )

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ 🎓 English Mastery Bot (GigaChat) запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
