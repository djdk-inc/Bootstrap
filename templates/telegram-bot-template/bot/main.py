import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers import start, echo

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.run_polling()


if __name__ == "__main__":
    main()
