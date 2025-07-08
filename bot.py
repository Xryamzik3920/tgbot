from telegram import Update
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext
)

TOKEN = 'ВАШ_ТОКЕН_ЗДЕСЬ'

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Привет! Я — ваш бот.')

def echo(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)

if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()