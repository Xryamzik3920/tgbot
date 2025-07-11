import os
import csv
import smtplib
from email.message import EmailMessage
from datetime import datetime
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
CSV_PATH = 'events.csv'

EMAIL_HOST = os.getenv('EMAIL_HOST')         
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')         
EMAIL_PASS = os.getenv('EMAIL_PASS')         
EMAIL_TO   = os.getenv('EMAIL_TO')           


action_buttons = [['Обо мне', 'Проекты', 'Связаться со мной']]
action_pick = ReplyKeyboardMarkup(
    keyboard=action_buttons,
    resize_keyboard=True,
    one_time_keyboard=True
)


back_buttons = [['Назад']]
back_keyboard = ReplyKeyboardMarkup(
    keyboard=back_buttons,
    resize_keyboard=True,
    one_time_keyboard=True
)


media_map = {
    'Обо мне': {
        'photo': 'book.png',
        'caption': """\
Студент 1 курса магистратуры ФГБОУ «Московский авиационный институт (национальный исследовательский университет)» (далее – «МАИ»). Специальность – прикладная математика.         Выпускающая кафедра 802 – “Мехатроника и теоретическая механика”. 
Образование – высшее, бакалавр:
1) ГБОУ г. Москвы «Школа № 1158» 1–7 класс (2008–2015).
2) ГБОУ г. Москвы «Бауманская инженерная школа № 1580» 8–11 класс (2015–2019) окончил физико‑математический класс.
3) Бакалавриат МАИ, Институт № 8 “Компьютерные науки и прикладная математика”. Выпускающая кафедра 802 – “Мехатроника и теоретическая механика” (2020–2024). Диплом: «Неявные методы Рунге–Кутты низкого порядка точности: построение численных схем и областей абсолютной устойчивости» — сдан на оценку «Отлично».
4) Магистратура МАИ, Институт № 8 “Компьютерные науки и прикладная математика”, специальность 01.04.04 «Прикладная математика», образовательная программа «Математическое и программное обеспечение мехатронных систем» (2024).
"""},
    'Проекты': {
        'photo': 'shesterenka.png',
        'caption': (
            '1) По данным цен на акции из индексов S&P-500, NASDAQ-100, DJI в течение последних 10 лет подсчитаны доходности, построены гистограммы, boxplot. Объединив доходности по секторам экономики построена диаграмма рассеивания, также были посчитаны метрики, такие как Value-at-Risk и Expected shortfall. Посмотреть проект в <a href="https://colab.research.google.com/drive/1-LlCYVhVXPQVtuLV4wqcGTIVbv89us54?usp=sharing">Colab</a>.\n\
2) Обсчет AB теста. Посмотреть проект в <a href="https://colab.research.google.com/drive/1P43gNgNH6G82LQiEdvQGscyCuDa8CxcA?usp=sharing">Colab</a>.\n\
3) Проверка различных гипотез с помощью подобранных для задачи критериев, таких как: точный t - тест, асимптотический z-тест, тест Фишера и другие. Посмотреть проект в <a href="https://colab.research.google.com/drive/1zd6b2jpKm_D82eis8U8Gcmm6NHs_t8iW?usp=sharing">Colab</a>.\n\
4) Телеграм бот для сбора данных и проверки гипотезы о долях.'
        ),
        'parse_mode': 'HTML'
    },
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_event(update.effective_user.id, False)
    
    await update.message.reply_text('Приветствую! Этот бот создан для того, чтобы облегчить процесс найма. Тут вы сможете найти более полную информацию, а так же связаться со мной')
    await update.message.reply_text(
        'Пожалуйста, выберите одно из действий ниже:',
        reply_markup=action_pick
    )
    
    context.user_data.pop('awaiting_email', None)

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if context.user_data.get('awaiting_email'):
        # 1.1) Обработка отмены
        if text == 'Отменить':
            await update.message.reply_text(
                'Отправка сообщения отменена.',
                reply_markup=action_pick
            )
            
        else:
            
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

                
                log_event(update.effective_user.id, True)

                await update.message.reply_text(
                    'Ваше сообщение отправлено на почту!',
                    reply_markup=action_pick
                )
            except Exception as e:
                await update.message.reply_text(
                    f'Ошибка при отправке письма: {e}',
                    reply_markup=action_pick
                )
                

        
        context.user_data.pop('awaiting_email', None)
        return

    
    if text == 'Назад':
        await update.message.reply_text(
            'Пожалуйста, выберите одно из действий ниже:',
            reply_markup=action_pick
        )
        return

    
    if text in media_map:
        media = media_map[text]
        photo_path = media['photo']
        caption = media['caption']
        parse_mode = media.get('parse_mode')  

     
        with open(photo_path, 'rb') as img:
            if parse_mode:
                await update.message.reply_photo(img, caption=caption, parse_mode=parse_mode)
            else:
                await update.message.reply_photo(img, caption=caption)

        
        await update.message.reply_text(
            'Чтобы вернуться в меню, нажмите «Назад»',
            reply_markup=back_keyboard
        )
        return

    
    if text == 'Связаться со мной':
        await update.message.reply_text(
            'Введите, пожалуйста, текст сообщения для отправки на почту:',
            reply_markup=ReplyKeyboardMarkup(
                [['Отменить']], resize_keyboard=True, one_time_keyboard=True
            )
        )
        context.user_data['awaiting_email'] = True
        return

    
    await update.message.reply_text(
        'Пожалуйста, используйте кнопки ниже:',
        reply_markup=action_pick
    )

def log_event(telegram_id: int, event: bool):
    
    write_header = not os.path.exists(CSV_PATH) or os.stat(CSV_PATH).st_size == 0

    with open(CSV_PATH, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['telegram_id', 'event', 'timestamp'])
        
        timestamp = datetime.utcnow().isoformat()
        writer.writerow([telegram_id, event, timestamp])

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice))
    app.run_polling()