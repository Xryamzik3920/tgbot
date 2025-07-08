import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
load_dotenv('enviroment.env')
TOKEN = os.getenv("BOT_TOKEN")

# SMTP‑настройки (добавьте в enviroment.env)
EMAIL_HOST = os.getenv('EMAIL_HOST')         # например, smtp.gmail.com
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')         # ваш email-логин
EMAIL_PASS = os.getenv('EMAIL_PASS')         # пароль или app password
EMAIL_TO   = os.getenv('EMAIL_TO')           # куда слать письма

# Основное меню — три варианта
action_buttons = [['Обо мне', 'Проекты', 'Связаться со мной']]
action_pick = ReplyKeyboardMarkup(
    keyboard=action_buttons,
    resize_keyboard=True,
    one_time_keyboard=True
)

# Кнопка «Назад»
back_buttons = [['Назад']]
back_keyboard = ReplyKeyboardMarkup(
    keyboard=back_buttons,
    resize_keyboard=True,
    one_time_keyboard=True
)

# Словарь с картинками и подписями
media_map = {
    'Обо мне': {
        'photo': 'void sky.jpg',
        'caption': 'Описание для варианта 1'
    },
    'Проекты': {
        'photo': 'void.jpg',
        'caption': 'Описание для варианта 2'
    },
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Приветствие и главное меню
    await update.message.reply_text('Приветствую! Этот бот создан для того, чтобы облегчить мой процесс найма. Тут вы сможете найти более полную информацию обо мне, а так же связаться со мной')
    await update.message.reply_text(
        'Пожалуйста, выберите одно из действий ниже:',
        reply_markup=action_pick
    )
    # Сбросим флаг ожидания ввода email‑сообщения
    context.user_data.pop('awaiting_email', None)

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Если ждем от пользователя текст для отправки на почту
    if context.user_data.get('awaiting_email'):
        # Обработка отмены
        if text == 'Отменить':
            await update.message.reply_text(
                'Отправка сообщения отменена.',
                reply_markup=action_pick
            )
            context.user_data.pop('awaiting_email', None)
            return

        # Иначе — отправляем email
        user_msg = text
        msg = EmailMessage()
        msg['Subject'] = 'Сообщение из Telegram‑бота'
        msg['From']    = EMAIL_USER
        msg['To']      = EMAIL_TO
        msg.set_content(user_msg)

        try:
            with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASS)
                server.send_message(msg)
            await update.message.reply_text(
                'Ваше сообщение отправлено на почту!',
                reply_markup=action_pick
            )
        except Exception as e:
            await update.message.reply_text(
                f'Ошибка при отправке письма: {e}',
                reply_markup=action_pick
            )

        # Сбросим флаг ожидания
        context.user_data.pop('awaiting_email', None)
        return

    # Обработка «Назад»
    if text == 'Назад':
        await update.message.reply_text(
            'Пожалуйста, выберите одно из действий ниже:',
            reply_markup=action_pick
        )
        return

    # Вариант 1 и 2
    if text in media_map:
        media = media_map[text]
        with open(media['photo'], 'rb') as img:
            await update.message.reply_photo(img, caption=media['caption'])
        await update.message.reply_text(
            'Чтобы вернуться в меню, нажмите «Назад»',
            reply_markup=back_keyboard
        )
        return

    # Вариант 3: переходим в режим ввода e‑mail текста
    if text == 'Связаться со мной':
        await update.message.reply_text(
            'Введите, пожалуйста, текст сообщения для отправки на почту:',
            reply_markup=ReplyKeyboardMarkup(
                [['Отменить']], resize_keyboard=True, one_time_keyboard=True
            )
        )
        context.user_data['awaiting_email'] = True
        return

    # Любой другой ввод
    await update.message.reply_text(
        'Пожалуйста, используйте кнопки ниже:',
        reply_markup=action_pick
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice))
    app.run_polling()