from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

SLEEP_TIME, WAKE_TIME, NAP_QUESTION, NAP_DURATION = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Во сколько ребёнок заснул ночью? (например: 21:30)")
    return SLEEP_TIME

async def sleep_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sleep_time"] = update.message.text
    await update.message.reply_text("Во сколько проснулся утром? (например: 07:30)")
    return WAKE_TIME

async def wake_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wake_time"] = update.message.text
    keyboard = [["Да", "Нет"]]
    await update.message.reply_text("Был ли дневной сон?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return NAP_QUESTION

async def nap_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == "да":
        await update.message.reply_text("Сколько длился дневной сон? (например: 1ч 20м)")
        return NAP_DURATION
    else:
        context.user_data["nap_duration"] = "0"
        return await save_data(update, context)

async def nap_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nap_duration"] = update.message.text
    return await save_data(update, context)

async def save_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    response = (
        "Спасибо! Вот что я сохранил:\n"
        f"🌙 Заснул: {data['sleep_time']}\n"
        f"☀️ Проснулся: {data['wake_time']}\n"
        f"🛌 Дневной сон: {data['nap_duration']}"
    )
    await update.message.reply_text(response)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END

if __name__ == "__main__":
    import os
    TOKEN = os.getenv("TELEGRAM_TOKEN")  # Подключай токен через переменную окружения или вставь прямо

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SLEEP_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, sleep_time)],
            WAKE_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, wake_time)],
            NAP_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, nap_question)],
            NAP_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, nap_duration)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
