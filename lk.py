import operator
import nest_asyncio
nest_asyncio.apply()
#🔵
import asyncio
import logging
import configparser
import os
import shutil
import string
import random
import time
import httpx
import locale  # Импорт библиотеки locale
import configparser
import pytz
from babel.numbers import format_number
from telegram.error import BadRequest
from datetime import datetime, timedelta  
from uuid import uuid4

# Removed requests, csv, StringIO imports
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# Токен бота (замените на актуальный перед запуском)
TOKEN = '8108534662:AAGITJNoOW2VQotLETnJAuJjVoOkpX2VzHA'  # ПЕРЕД запуском бота ОБНОВИТЬ токен

#ОСНОВНОЙ - 7738679454:AAE2dk7dlT58sWlxS0J6eicWTVJsUoHULNs
#ТЕСТОВЫЙ - 8108534662:AAGITJNoOW2VQotLETnJAuJjVoOkpX2VzHA

# Файл .ini для хранения всех данных бота

ACCOUNTS_FILE = "accounts.ini"
REPORTS_FILE = "reports.ini"
WITHDRAWALS_FILE = "withdrawals.ini"
REGISTRATIONS_FILE = "registrations.ini"
SETTINGS_FILE = "settings.ini"
PROMO_FILE = "promo.ini"
PROMO_ACTIVATIONS_FILE = "promo_activations.ini"
REG_NAME, REG_REALNAME, REG_BIRTHDATE, REG_POSITION_MANUAL = range(4)
CHARACTERISTICS_FILE = "characteristics.ini"
PRICE_MIN = 475_000
PRICE_MAX = 525_000

async def price_updater(application):
    while True:
        sell_price = random.randint(PRICE_MIN, PRICE_MAX)
        buy_price = int(sell_price * 0.9)
        application.bot_data['sell_price'] = sell_price
        application.bot_data['buy_price'] = buy_price
        print(f"Цены обновлены! Продажа: {sell_price}, Покупка: {buy_price}")
        await asyncio.sleep(3600)  # или 3600 для часа
        
async def unknown_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Пожалуйста, используйте доступные команды или введите корректные данные.")

# Функция загрузки данных из .ini-файла (с отключенной интерполяцией для символа '%')

def load_settings():
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE, encoding="utf-8")
    return config

def save_settings(config):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as configfile:
        config.write(configfile)

def get_rd():
    config = load_settings()
    if config.has_section("settings") and "rd" in config["settings"]:
        return datetime.strptime(config["settings"]["rd"], "%Y-%m-%d")
    return None

def set_rd(rd):
    config = load_settings()
    if not config.has_section("settings"):
        config.add_section("settings")
    config["settings"]["rd"] = rd.strftime("%Y-%m-%d")
    save_settings(config)

def load_config(file_path):
    config = configparser.ConfigParser(interpolation=None)
    config.read(file_path, encoding="utf-8")
    return config

def load_accounts():
    return load_config(ACCOUNTS_FILE)

def load_reports():
    return load_config(REPORTS_FILE)

def load_withdrawals():
    return load_config(WITHDRAWALS_FILE)

def load_registrations():
    return load_config(REGISTRATIONS_FILE)

def save_accounts(config):
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as configfile:
        config.write(configfile)
        
async def send_technical_exit_to_all_users(context: ContextTypes.DEFAULT_TYPE):
    config = load_accounts()
    keyboard = get_login_keyboard()
    message = "ℹ️ Технический выход из системы, просьба пройти авторизацию."

    for user_id in config.sections():
        if user_id.isdigit():
            try:
                with open("techres.png", "rb") as photo:
                    await context.bot.send_photo(
                        chat_id=int(user_id),
                        photo=photo,
                        caption=message,
                        reply_markup=keyboard
                    )
            except Exception as e:
                logging.error(f"Ошибка при отправке фото пользователю {user_id}: {e}")


async def force_technical_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_technical_exit_to_all_users(context)
    await update.effective_message.reply_text("🅰 Технический рестарт завершен успешно. Пользователи перекинуты на экран авторизации.")
    
# Система плана (получение пользователей)
def get_top_players():
    config = load_accounts()
    players = []
    for section in config.sections():
        if section.isdigit():
            try:
                ball = int(config[section].get('ball', 0))
                nick = config[section].get('nick', 'Неизвестный')
                level = int(config[section].get('level', 0))
                position = config[section].get('position', 'Гость')
                players.append((nick, ball, level, position))
            except ValueError:
                continue
    top_players = sorted(players, key=lambda p: p[1], reverse=True)[:3]
    return top_players

# Система расчета ЗП при закрытии недели.
def calculate_salary(ball, level, warnings):
    """
    Функция calculate_salary рассчитывает зарплату по формуле:
      salary = ball * daily_rate * (1 - 0.25 * warnings)
    При этом результат приводится к целому числу.
    """
    daily_rate = get_daily_rate_by_level(level)
    reduction_factor = 1 - (0.25 * warnings)
    salary = ball * daily_rate * reduction_factor
    # Приводим результат к целому
    return int(salary)

# Генерация случайного ID из заданного числа символов (для идентификаторов отчётов)
def generate_random_id(length=5):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Получение информации о пользователе по Telegram ID из .ini-файла
def get_user_info(user_id):
    config = load_accounts()
    sec_name = str(user_id)
    if config.has_section(sec_name):
        sec = config[sec_name]
        level = int(sec.get('level', '0'))  # Уровень пользователя, по умолчанию 0
        exp = int(sec.get('exp', '0'))  # Получение опыта
        daily_rate = get_daily_rate_by_level(level)  # Используем исправленную функцию  
        ball = int(sec.get('ball', '0')) if 'ball' in sec else 0
        warnings = int(sec.get('warnings', '0'))
        predicted_payment = calculate_predicted_payment(ball=ball, daily_rate=daily_rate, warnings=warnings)
        return {
            'nick': sec.get('nick', ''), 
            'position': sec.get('position', ''), 
            'level': level,  # Добавлено извлечение уровня
            'exp': exp,
            'daily_rate': daily_rate, 
            'warnings': sec.get('warnings', '0'), 
            'predicted_payment': predicted_payment, 
            'personal_account': sec.get('personal_account', '0'), 
            'rating': sec.get('rating', '0'), 
            'ball': ball, 
            'is_admin': sec.get('is_admin', '-1'),
            'realname': sec.get('realname', ''), 
            'daterod': sec.get('daterod', ''),
            'pop': sec.get('pop', '0'),
            'osk': sec.get('osk', '0'),
            'lvlconf': sec.get('lvlconf', '0'),
        }
    return None

def get_daily_rate_by_level(level):
    """
    Рассчитывает ставку для заместителя на основе уровня.
    
    :param level: Уровень заместителя (от 0 до 100)
    :return: Ежедневная ставка в рублях
    """
    if level < 0 or level > 100:
        raise ValueError("Уровень должен быть в диапазоне от 0 до 100.")
    
    base_rate = 250_000  # Базовая ставка для уровня 0
    rate_increment = 3_000  # Увеличение ставки за каждый уровень
    return base_rate + (level * rate_increment)

# Функция для расчета predicted_payment
def calculate_predicted_payment(ball, daily_rate, warnings):
    reduction_factor = 1 - (0.25 * warnings)
    return ball * daily_rate * reduction_factor

def update_balls():
    config = load_accounts()
    updated = False
    for section in config.sections():
        if section.isdigit():  
            ball = int(config[section].get('ball', 0))
            
            if config[section].get('ball') != str(ball):
                config[section]['ball'] = str(ball)
                updated = True
                logging.info(f"Updated ball for user {section}: ball={ball}")
    
    if updated:
        save_accounts(config)
        logging.info("All updates saved to accounts.ini")
    else:
        logging.info("No updates needed")

# Клавиатура главного меню
def get_main_keyboard(user_id):
    user_info = get_user_info(user_id)
    admin_level = int(user_info.get('is_admin', 0)) if user_info else 0

    keyboard = [
        [KeyboardButton("Статистика"), KeyboardButton("Рейтинг")],
        [KeyboardButton("Отчёт"), KeyboardButton("Активность")],
        [KeyboardButton("Центр обмена"), KeyboardButton("Вывод средств")]
    ]

    if admin_level >= 1:
        keyboard.append([KeyboardButton("Панель администратора")])

    # Добавляем кнопку "Выйти" в конец для всех
    keyboard.append([KeyboardButton("Выйти")])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# Клавиатура для кнопки "Назад"
def get_back_keyboard():
    keyboard = [[KeyboardButton("Назад")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

# Стартовое приветствие (/start)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context):
        return  # блокируем доступ
    with open("av.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    await update.message.reply_text(
        "Для входа в систему нажмите кнопку ниже.",
        reply_markup=get_login_keyboard()
    )

# Обработчик кнопки "Войти"
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Авторизация":
        await login(update, context)

# Вход в систему (по нажатию "Войти" или сообщению "войти")
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context):
        return  # блокируем доступ
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    
    if not user_info:
        with open("av.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
        await update.message.reply_text(
            "❌ Авторизация невозможна, пройдите регистрацию и ждите ответа администратора бота."
        )
        return

    admin_level = int(user_info.get('is_admin', 0))
    nick = user_info['nick']


    if admin_level == -2:
        await update.message.reply_text(
            f"🐼‍ Рады приветствовать снова *{nick}*!\n"
            f"🟨 Вы авторизовались как XVIP.",
            parse_mode="Markdown"
        )
    if admin_level == -1:
        await update.message.reply_text(
            f"🐼 Рады приветствовать снова *{nick}*!\n"
            f"⬜ Вы авторизовались как Гость. Для выдачи прав обратитесь к администратору бота.",
            parse_mode="Markdown"
        )
    if admin_level == 0:
        await update.message.reply_text(
            f"🐼 Рады приветствовать снова *{nick}*!\n"
            f"🔳 Вы авторизовались как Заместитель.",
            parse_mode="Markdown"
        )
    elif admin_level == 1:
        await update.message.reply_text(
            f"🐼 Рады приветствовать снова *{nick}*!\n"
            f"🟫 Вы авторизовались как Хранитель.",
            parse_mode="Markdown"
        )
    elif admin_level == 2:
        await update.message.reply_text(
            f"🐼 Рады приветствовать снова *{nick}*!\n"
            f"🟥 Вы авторизовались как Старший заместитель.",
            parse_mode="Markdown"
        )
    elif admin_level == 3:
        await update.message.reply_text(
            f"🐼 Рады приветствовать снова *{nick}*!\n"
            f"🟥 Вы авторизовались как Лидер семьи.",
            parse_mode="Markdown"
        )
    
    await update.message.reply_text("Ниже представлено главное меню. Выберите нужный вариант.", reply_markup=get_main_keyboard(user_id))


# Клавиатура для входа (кнопка "Войти")
def get_login_keyboard():
    keyboard = [
        [KeyboardButton("Авторизация"), KeyboardButton("Регистрация")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

# Возврат в главное меню (/menu)
# Возврат в главное меню (/menu)
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context):
        return  # блокируем доступ
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)

    # Проверка: зарегистрирован ли пользователь
    if not user_info:
        await update.message.reply_text(
            "❌ Вы не зарегистрированы. Авторизуйтесь или пройдите регистрацию.",
            reply_markup=get_login_keyboard()
        )
        return

    admin_level = int(user_info.get('is_admin', 0))

    await update.message.reply_text(
        "Ниже представлено главное меню. Выберите нужный вариант.",
        reply_markup=get_main_keyboard(user_id)  # Передаем user_id
    )


# Статистика
# Функция personal_account
async def personal_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    if user_info:
        current_level = int(user_info.get('level', '0'))
        current_exp = int(user_info.get('exp', '0'))
        required_exp = 200 + (current_level * 3)
        predicted_payment_formatted = locale.format_string("%d", user_info['predicted_payment'], grouping=True).replace('\xa0', '.')
        daily_rate_formatted = locale.format_string("%d", user_info['daily_rate'], grouping=True).replace('\xa0', '.')
        personal_account_formatted = locale.format_string("%d", int(user_info['personal_account']), grouping=True).replace('\xa0', '.')
        message = (
            f"👤 Никнейм: {user_info['nick']}\n"
            f"🔮 Реальное имя: {user_info['realname']}\n"
            f"🎂 Дата рождения: {user_info['daterod']}\n"
            f"💼 Должность: {user_info['position']}\n"
            f"🧗 Уровень: {current_level}\n"
            f"⚡ Очки опыта: {current_exp} из {required_exp}\n"
            f"💰 Ставка за монету: {daily_rate_formatted} RUB\n"
            f"⚠︎ Предупреждения: {user_info['warnings']}\n"
            f"🧿 Монеты активности: {user_info['ball']}\n"
            f"💈 Бусты: {user_info['osk']}\n"
            f"💸 Зарплата: {predicted_payment_formatted} RUB\n"
            f"💳 Личный счет: {personal_account_formatted} RUB\n"
        )
        with open("stats.png", "rb") as photo:
             await update.message.reply_photo(photo=photo)
        await update.message.reply_text(message, reply_markup=get_back_keyboard())
    else:
        await update.message.reply_text("Информация о пользователе не найдена.", reply_markup=get_back_keyboard())


# Рейтинг (команда "Рейтинг")
async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_players = get_top_players()
    if not top_players:
        await update.message.reply_text("На данный момент нет пользователей в рейтинге.", reply_markup=get_back_keyboard())
        return

    # Словарь соответствия уровней и эмодзи
    level_emojis = [
        (range(0, 10), "🧸"),
        (range(10, 20), "🎓"),
        (range(20, 30), "🦾"),
        (range(30, 40), "🕶️"),
        (range(40, 50), "🍹"),
        (range(50, 60), "🚬"),
        (range(60, 70), "💼"),
        (range(70, 80), "⭐"),
        (range(80, 90), "🌟"),
        (range(90, 100), "💎"),
        (range(100, 101), "👑")
    ]

    # Словарь соответствия ранга и эмодзи
    rank_emojis = {
        "Старший заместитель": "🟥 Старший заместитель",
        "Лидер семьи": "🟥 Лидер семьи",
        "Хранитель": "🟫 Хранитель",
        "Заместитель": "🔳 Заместитель",
        "XVIP": "🟨 XVIP",
        "Гость": "⬜ Гость"
    }

    def get_activity_level(ball):
        if ball >= 625:
            return "🟣 Превосходная активность"
        elif 500 <= ball < 625:
            return "🟡 Максимальная активность"
        elif 375 <= ball < 500:
            return "🟢 Средняя активность"
        elif 250 <= ball < 375:
            return "🔴 Минимальная активность"
        else:
            return "⚪ Недостаточная активность"

    def get_level_emoji(level):
        for level_range, emoji in level_emojis:
            if level in level_range:
                return emoji
        return "❔"

    def get_rank_emoji(rank):
        return rank_emojis.get(rank, "⬜ Гость")
    
    # Сначала отправляем картинку рейтинга
    with open("rating.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    
    message = "<b>🏆 Лидеры рейтинга за расчётную неделю.</b>\n\n"
    emojis = ["🥇", "🥈", "🥉"]
    for i, (nick, ball, level, position) in enumerate(top_players[:3]):
        level_emoji = get_level_emoji(level)
        activity_str = get_activity_level(ball)
        rank_str = get_rank_emoji(position)

        if i == 0:
            message += f"{emojis[i]} <b>{nick} {level_emoji}</b>\n<b>{rank_str}</b>\n<b>{activity_str}</b>\n<b>🧿 {ball}</b>\n\n"
        else:
            message += f"{emojis[i]} {nick} {level_emoji}\n{rank_str}\n{activity_str}\n🧿 {ball}\n\n"

    quote_message = (
        "ℹ️ Правилами установлены награды расчётного дня:\n\n"
        f"🥇 место - 500 💈 (~250кк 💳), требуется превосходная активность.\n"
        f"🥈 место - 250 💈 (~125кк 💳), требуется максимальная активность.\n"
        f"🥉 место - 100 💈 (~50кк 💳), требуется средняя активность.\n"
    )
    quote_message = f"<blockquote><b>{quote_message}</b></blockquote>"

    message += f"{quote_message}"

    await update.message.reply_text(message, reply_markup=get_back_keyboard(), parse_mode='HTML')

async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    if not user_info:
        await update.message.reply_text("Информация о пользователе не найдена.", reply_markup=get_back_keyboard())
        return

    digit_emojis = {
        '0': '0️⃣',
        '1': '1️⃣',
        '2': '2️⃣',
        '3': '3️⃣',
        '4': '4️⃣',
        '5': '5️⃣',
        '6': '6️⃣',
        '7': '7️⃣',
        '8': '8️⃣',
        '9': '9️⃣'
    }
    level_emojis = [
        (range(0, 10), "🧸"),
        (range(10, 20), "🎓"),
        (range(20, 30), "🦾"),
        (range(30, 40), "🕶️"),
        (range(40, 50), "🍹"),
        (range(50, 60), "🚬"),
        (range(60, 70), "💼"),
        (range(70, 80), "⭐"),
        (range(80, 90), "🌟"),
        (range(90, 100), "💎"),
        (range(100, 101), "👑")
    ]

    def get_level_emoji(level):
        for level_range, emoji in level_emojis:
            if level in level_range:
                return emoji
        return "❔"

    points = int(user_info.get('ball', 0))
    user_level = int(user_info.get('level', 0))
    user_level_emoji = get_level_emoji(user_level)

    if points >= 625:
        user_activity_level = "🟣 Превосходная"
    elif 500 <= points < 625:
        user_activity_level = "🟡 Максимальная"
    elif 375 <= points < 500:
        user_activity_level = "🟢 Средняя"
    elif 250 <= points < 375:
        user_activity_level = "🔴 Минимальная"
    else:
        user_activity_level = "⚪ Недостаточная"

    with open("activ.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)

    # Сообщение с показателями пользователя
    message = (
        "📋 Ваши показатели.\n"
        f"👤 Никнейм: {user_info.get('nick', 'Неизвестный')} {user_level_emoji}\n"
        f"⚖️ Активность: {user_activity_level}\n"
        f"🧿 Монеты активности: {points}\n"
    )

    # Сообщение с правилами
    messagee = (
        "ℹ️ Правилами установлены нормы активности для заместителей за расчётную неделю:\n"
        "⚪ - недостаточная активность (от 0 до 249 монет активности в неделю), в случае получения по итогам недели заместитель снимается с должности и не получает выплат.\n"
        "🔴 - минимальная активность (от 250 до 374 монет активности в неделю), обязательна к выполнению.\n"
        "🟢 - средняя активность (от 375 до 499 монет активности в неделю).\n"
        "🟡 - максимальная активность (от 500 до 624 монет активности в неделю).\n"
        "🟣 – превосходная активность (от 625 монет активности за неделю).\n"
    )
    messagee = f"<blockquote><b>{messagee}</b></blockquote>"

    # Отправляем два отдельных сообщения
    await update.message.reply_text(message, reply_markup=get_back_keyboard())
    await update.message.reply_text(messagee, reply_markup=get_back_keyboard(), parse_mode='HTML')

    # Доп. сообщение только для админов > 1 уровня
    if int(user_info.get("is_admin", "0")) > 1:
        await update.message.reply_text(
            "🅰 Для просмотра глобальной активности по всем должностям используйте команду: <code>/aactive</code>",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )

# Панель администратора (команда "Панель администратора")
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    
    # Проверка наличия информации о пользователе и прав администратора
    if not user_info or int(user_info['is_admin']) == 0:
        if update.message:
            await update.message.reply_text("⛔ У вас нет доступа к этому разделу.")
        elif update.callback_query:
            await update.callback_query.message.edit_text("⛔ У вас нет доступа к этому разделу.")
        return

    admin_level = int(user_info.get('is_admin', 0))

    # Инициализация клавиатуры
    keyboard = []

    # Кнопки для администраторов с уровнем 1 и выше
    if admin_level >= 1:
        keyboard.append([InlineKeyboardButton("👥 Управление пользователями", callback_data="manage_users")])
        
    # Кнопки для администраторов с уровнем 2 и выше
    if admin_level >= 2:
        keyboard.append([InlineKeyboardButton("📊 Отчеты", callback_data="reports")])
        keyboard.append([InlineKeyboardButton("📢 Массовая рассылка", callback_data="mass_message")])
        keyboard.append([InlineKeyboardButton("✉ Одиночная рассылка", callback_data="start_single_message")])
        keyboard.append([InlineKeyboardButton("📅 Расчётный день", callback_data="change_rd")])
        keyboard.append([InlineKeyboardButton("📋 Заявки на регистрацию", callback_data="view_registrations")])
        keyboard.append([InlineKeyboardButton("☢️ Закрытие недели", callback_data="week_close")])
        keyboard.append([InlineKeyboardButton("💰 Заявки на вывод", callback_data="admin_withdrawals")])

    # Кнопка для администраторов с уровнем 3
    if admin_level >= 3:
        keyboard.append([InlineKeyboardButton("🅿 Технический рестарт", callback_data="force_technical_exit")])
        keyboard.append([InlineKeyboardButton("🔧 Технические работы", callback_data="toggle_maintenance")])

    keyboard.append([InlineKeyboardButton("🚪 Выйти", callback_data="exit_admin_panel")])

    # Определение эмодзи для уровня администратора
    level_emoji = '1️⃣' if admin_level == 1 else '2️⃣' if admin_level == 2 else '3️⃣'

    # Отправка клавиатуры с кнопками
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(f"🅰 Вы успешно вошли в панель администратора.\n\nВаш уровень прав: {level_emoji}", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(f"🅰 Вы успешно вошли в панель администратора.\n\nВаш уровень прав: {level_emoji}", reply_markup=reply_markup)
        
async def send_photo_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message:
            with open("admin.png", "rb") as photo:
                await update.message.reply_photo(photo=photo)
            # После отправки фото сразу вызываем admin()
            await admin(update, context)

        elif update.callback_query:
            query = update.callback_query
            await query.answer()
            with open("admin.png", "rb") as photo:
                await query.message.reply_photo(photo=photo)
            # После отправки фото сразу вызываем admin()
            await admin(update, context)

    except FileNotFoundError:
        if update.message:
            await update.message.reply_text("Файл admin.png не найден.")
        elif update.callback_query:
            await update.callback_query.message.reply_text("Файл admin.png не найден.")
        

# Обработчик для кнопки "Выйти"
async def exit_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    
#Функция админ прав
async def set_admin_rights_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("0", callback_data="set_admin_0"),
         InlineKeyboardButton("1", callback_data="set_admin_1")],
        [InlineKeyboardButton("2", callback_data="set_admin_2"),
         InlineKeyboardButton("3", callback_data="set_admin_3")],
        [InlineKeyboardButton("Назад", callback_data="back_to_admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("Выберите уровень админ прав:", reply_markup=reply_markup)

async def choose_admin_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Извлекаем уровень прав из callback_data, например "set_admin_2" -> level "2"
    level = query.data.split("_")[-1]
    # Получаем ID пользователя, для которого меняется уровень админ прав; например, можно сохранить его в context.user_data
    user_id = context.user_data.get('user_id')  # Предполагается, что ID выбранного пользователя уже сохранён
    if not user_id:
        await query.message.edit_text("Ошибка: пользователь не выбран.")
        return
    
    config = load_accounts()
    if config.has_section(user_id):
        config[user_id]['is_admin'] = level
        save_accounts(config)
        await query.message.edit_text(f"Уровень админ прав для пользователя {user_id} изменён на {level}.")
    else:
        await query.message.edit_text(f"Пользователь {user_id} не найден.")

async def back_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Возвращаем пользователя к админ-панели
    await query.message.edit_text("Панель администратора.", reply_markup=admin_keyboard())  
    # Функция admin_keyboard() должна вернуть клавиатуру админ-панели
    
# Команда "Отчёт" (подача нового отчета или проверка статуса существующего)
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    current_level = int(user_info.get('level', 0)) if user_info else 0
    lvlconf_val = int(user_info.get('lvlconf', 0)) if user_info else 0
    try:
        config = load_reports()
    except Exception as e:
        logging.error(f"Error loading report data for user {user_id}: {e}")
        await update.message.reply_text("❌ Ошибка при загрузке данных отчетов.", reply_markup=get_back_keyboard())
        return

    # Если требуется подтверждение уровня, блокируем отчёты
    if lvlconf_val == 1:
        await update.message.reply_text(
            f"❌ Для подачи отчёта требуется подтверждение уровня {current_level}!\n"
            f"Система отчётов заблокирована.\n"
            f"Для подтверждения уровня посетите Центр обмена → Подтверждение уровня и выполните <code>/lvlconf</code>.",
            parse_mode="HTML"
        )
        return

    # Отображение списка отчетов на рассмотрении
    pending_reports = []
    for sec in config.sections():
        if sec.startswith("report_") and config[sec].get("user_id") == str(user_id) and config[sec].get("status", "pending") == "pending":
            pending_reports.append(sec)

    if pending_reports:
        reports_message = "📋 Ваши отчеты на рассмотрении:\n\n"
        for report_id in pending_reports:
            reports_message += f"⏳ Отчет ID: {report_id[len('report_'):]}\n"
        await update.message.reply_text(reports_message, reply_markup=get_back_keyboard())

    # Позволить пользователю создавать новый отчет
    context.user_data['report_state'] = 'await_text'
    logging.info(f"User {user_id} is creating a new report.")
    with open("ot.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    await update.message.reply_text(
        "✏️ Пожалуйста, отправьте текст вашего отчета.",
        reply_markup=get_back_keyboard()
    )

def get_back_to_nabors_keyboard():
    keyboard = [[KeyboardButton("Назад к выбору набора")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Обработчик выбора пункта меню (общий для кнопок главного меню)
async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    admin_level = int(user_info.get('is_admin', 0)) if user_info else 0
    
    if admin_level == -1:
        await update.message.reply_text("Для выдачи прав обратитесь к администратору бота.")
        return

    try:
        text = update.message.text.strip()
        logging.info(f"Обработка команды: {text}")
        if text == "Статистика":
            await personal_account(update, context)
        elif text == "Отчёт":
            await report(update, context)
        elif text == "Вывод средств":
            await request_withdrawal(update, context)
        elif text == "Рейтинг":
            await rating(update, context)
        elif text == "Активность":
            await plan(update, context)
        elif text == "Центр обмена":
            await active(update, context)
        elif text == "Обычные наборы":
            await usual_sets(update, context)
        elif text == "Сезонные наборы":
            await seasonal_sets(update, context)
        elif text == "Лимитированные наборы":
            await limited_sets(update, context)
        elif text == "Характеристики":
            await characteristics(update, context)
        elif text == "Подтверждение уровня":
            await pod(update, context)    
        elif text == "Назад в центр обмена":
            await active(update, context)
        elif text == "Наборы":
            await update.message.reply_text(
                "Выберите тип набора:",
                reply_markup=get_main_nabors_keyboard()
            )
        elif text == "Назад к выбору набора":
            await update.message.reply_text(
                "Выберите тип набора:",
                reply_markup=get_main_nabors_keyboard()
            )
        elif text == "Кейсы":
            await case(update, context)    
        elif text == "Выйти":
            await start(update, context)
        elif text == "Панель администратора":
            if admin_level >= 1:  # Проверяем, есть ли админские права перед вызовом
                await send_photo_admin(update, context)
            else:
                await update.message.reply_text("⛔ У вас нет доступа к панели администратора.")
        elif text == "Назад":
            await menu(update, context)
        else:
            logging.warning(f"Неизвестная команда: {text}")
    except Exception as e:
        logging.error(f"Ошибка в обработке меню: {e}")
        
# Сохранение заявки на вывод средств в .ini-файл
async def save_request(request_id: str, nick: str, amount: float, remaining_balance: float, user_id: int, context: ContextTypes.DEFAULT_TYPE):
    config = load_withdrawals()
    config[f"request_{request_id}"] = {
        "nick": nick,
        "amount": str(amount),
        "remaining_balance": str(remaining_balance),
        "user_id": str(user_id),
        "status": "pending"
    }
    with open(WITHDRAWALS_FILE, "w", encoding="utf-8") as configfile:
        config.write(configfile)

# Удаление заявки на вывод средств из .ini-файла
def remove_request(request_id: str):
    config = load_withdrawals()
    sec_name = f"request_{request_id}"
    if config.has_section(sec_name):
        config.remove_section(sec_name)
        with open(WITHDRAWALS_FILE, "w", encoding="utf-8") as configfile:
            config.write(configfile)



# Пользователь выбрал "Вывод средств" (инициация заявки)
async def request_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("vivod.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    # --- Новая проверка на расчётный день ---
    rd = get_rd()  # эта функция уже есть в вашем коде и возвращает datetime
    rd1 = rd - timedelta(days=6)
    today = datetime.now().date()
    if not rd or today != rd.date():
        await update.message.reply_text(
            "🔴 Вывод средств доступен только в расчётный день.\n\n"
            f"⚖️ Расчётная неделя.\n"
            f"📅 Период: {rd1.strftime('%d.%m.%Y')} - {rd.strftime('%d.%m.%Y')}\n"
            f"💽 Ближайший расчётный день: {rd.strftime('%d.%m.%Y') if rd else 'не установлен'}"
        )
        return

    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    if not user_info:
        await update.message.reply_text("Ошибка: Информация о пользователе не найдена.")
        return
    balance = float(user_info['personal_account'])
    if balance <= 0:
        await update.message.reply_text("❌ У вас недостаточно средств для вывода.")
        return
    amounts = {
        25: round(balance * 0.25, 2),
        50: round(balance * 0.50, 2),
        75: round(balance * 0.75, 2),
        100: round(balance * 1.00, 2),
    }
    keyboard = [
        [InlineKeyboardButton(f"Вывести 25% ({amounts[25]})", callback_data="withdraw_25")],
        [InlineKeyboardButton(f"Вывести 50% ({amounts[50]})", callback_data="withdraw_50")],
        [InlineKeyboardButton(f"Вывести 75% ({amounts[75]})", callback_data="withdraw_75")],
        [InlineKeyboardButton(f"Вывести 100% ({amounts[100]})", callback_data="withdraw_100")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🟢 Вывод средств доступен. Выберите сумму для вывода из вариантов ниже.\n💽 Сегодня расчётный день.", reply_markup=reply_markup)

# Обработчик выбора процента вывода (после кнопок 25%, 50%, 75%, 100%)
async def handle_withdrawal_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_info = get_user_info(user_id)
    if not user_info:
        await query.message.edit_text("Ошибка: Информация о пользователе не найдена.")
        return
    balance = float(user_info['personal_account'])
    percentage = int(query.data.split("_")[1])
    amount = round(balance * (percentage / 100), 2)
    if amount <= 0:
        await query.message.edit_text("Ошибка: Недостаточно средств для вывода.")
        return
    remaining_balance = round(balance - amount, 2)
    request_id = str(uuid4())[:8]
    # Сохраняем данные заявки во временном контексте пользователя (для подтверждения)
    context.user_data[user_id] = {
        "request_id": request_id,
        "amount": amount,
        "remaining_balance": remaining_balance,
        "nick": user_info['nick']
    }
    keyboard = [
        [InlineKeyboardButton("✅ Да", callback_data="confirm_withdraw")],
        [InlineKeyboardButton("❌ Нет", callback_data="cancel_withdraw")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = (
        f"🔔 Подтверждение заявки на вывод\n\n"
        f"👤 Ник: {user_info['nick']}\n"
        f"💸 Сумма вывода: {amount} RUB\n"
        f"💳 Остаток после вывода: {remaining_balance}\n\n"
        f"Проверьте, правильно ли указаны данные. Нажмите 'Да', если всё верно, или 'Нет' для отмены."
    )
    # Сохраняем заявку в .ini-файл со статусом "pending"
    await save_request(request_id, user_info['nick'], amount, remaining_balance, user_id, context)
    await query.message.edit_text(message, reply_markup=reply_markup)
    

# Обработчик подтверждения заявки ("Да")
async def confirm_withdraw_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id not in context.user_data or "request_id" not in context.user_data[user_id]:
        await query.message.edit_text("❌ Заявка не найдена.")
        return
    req = context.user_data[user_id]
    request_id = req["request_id"]
    amount = req["amount"]
    remaining_balance = req["remaining_balance"]
    nick = req["nick"]
    # Уведомляем администратора о новой заявке
    await notify_admin_about_new_request(nick, amount, request_id, context)
    # Сообщаем пользователю, что заявка отправлена на рассмотрение
    await query.message.edit_text("✅ Заявка отправлена на рассмотрение лидеру семьи.")

# Обработчик отмены заявки ("Нет")
async def cancel_withdraw_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id in context.user_data and "request_id" in context.user_data[user_id]:
        req_id = context.user_data[user_id]["request_id"]
        remove_request(req_id)
        context.user_data.pop(user_id, None)
    await query.message.edit_text("❌ Заявка на вывод отменена.")

# Обработчик нажатия "Заявки на вывод" в админ-панели – список активных заявок
async def admin_withdrawals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    config = load_withdrawals()
    # Собираем все заявки со статусом "pending"
    requests = [sec for sec in config.sections() if sec.startswith("request_") and config[sec].get("status", "pending") == "pending"]
    if not requests:
        await query.message.edit_text("📋 Нет заявок, ожидающих подтверждения.")
        return
    text = "📋 Активные заявки на вывод:\n"
    keyboard = []
    for sec in requests:
        nick = config[sec].get("nick", "Неизвестный")
        amount = config[sec].get("amount", "0")
        text += f"\n🔹 {nick} — {amount} RUB"
        req_id = sec[len("request_"):]
        keyboard.append([InlineKeyboardButton(f"ID заявки: {req_id}", callback_data=f"view_{req_id}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

# Обработчик нажатия на конкретную заявку (ID) – просмотр деталей заявки
async def view_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    request_id = query.data.split("_")[1]
    config = load_withdrawals()
    sec_name = f"request_{request_id}"
    if not config.has_section(sec_name):
        await query.message.edit_text("❌ Заявка не найдена.")
        return
    user_id = int(config[sec_name]["user_id"])
    amount = config[sec_name]["amount"]
    nick = config[sec_name]["nick"]
    text = f"Заявка на вывод {amount} RUB для {nick}\nID заявки: {request_id}\nВыберите действие:"
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data=f"approve_{request_id}")],
        [InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{request_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

# Обработчик подтверждения вывода средств (админ нажал "Подтвердить")
# Обработчик подтверждения вывода средств (админ нажал "Подтвердить")
async def approve_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    request_id = query.data.split("_")[1]
    config = load_withdrawals()
    sec_name = f"request_{request_id}"
    if not config.has_section(sec_name):
        await query.message.edit_text("❌ Заявка не найдена.")
        return
    user_id = int(config[sec_name]["user_id"])
    amount = int(float(config[sec_name]["amount"]))  # Преобразуем сумму в целое число
    nick = config[sec_name]["nick"]
    
    # Загружаем данные аккаунта
    accounts_config = load_accounts()
    user_section = str(user_id)
    if accounts_config.has_section(user_section):
        personal_account = int(float(accounts_config[user_section].get('personal_account', '0')))  # Преобразуем баланс в целое число
        new_balance = personal_account - amount
        if new_balance < 0:
            await query.message.edit_text("❌ Недостаточно средств на личном счете для вывода.")
            return
        accounts_config[user_section]['personal_account'] = str(new_balance)
        save_accounts(accounts_config)
    else:
        await query.message.edit_text("❌ Пользователь не найден.")
        return
    
    # Удаляем заявку из файла
    config.remove_section(sec_name)
    with open(WITHDRAWALS_FILE, "w", encoding="utf-8") as f:
        config.write(f)
    
    # Уведомляем пользователя об одобрении заявки
    await context.bot.send_message(user_id, f"✅ Ваш вывод {amount} RUB одобрен, не забудьте обязательно заполнить тему - бюджет семьи!")
    await query.message.edit_text(f"✅ Вывод {amount} RUB для {nick} одобрен!")


# Обработчик отклонения заявки ("Отклонить")
async def reject_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    request_id = query.data.split("_")[1]
    config = load_withdrawals()
    sec_name = f"request_{request_id}"
    if not config.has_section(sec_name):
        await query.message.edit_text("❌ Заявка не найдена.")
        return
    user_id = int(config[sec_name]["user_id"])
    amount = config[sec_name]["amount"]
    nick = config[sec_name]["nick"]
    # Удаляем заявку из файла
    config.remove_section(sec_name)
    with open(WITHDRAWALS_FILE, "w", encoding="utf-8") as f:
        config.write(f)
    # Логируем отклонение (для отладки)
    print(f"Заявка {request_id} отклонена и удалена.")
    try:
        # Уведомляем пользователя об отклонении
        await context.bot.send_message(user_id, f"❌ Ваша заявка на вывод {amount} RUB отклонена. Пожалуйста, свяжитесь с руководством для уточнений.")
    except Exception as e:
        print(f"Ошибка при отправке сообщения пользователю: {e}")
        await query.message.edit_text("❌ Ошибка при отправке сообщения пользователю.")
        return
    await query.message.edit_text(f"❌ Заявка на вывод {amount} RUB для {nick} отклонена.")

# Уведомление администратора о новой заявке на вывод
async def notify_admin_about_new_request(nick: str, amount: float, request_id: str, context: ContextTypes.DEFAULT_TYPE):
    # Получаем список администраторов с уровнем >= 2
    admin_ids_filtered = load_admin_ids()  # load_admin_ids должна возвращать список ID (строк или чисел) для is_admin >= 2
    if not admin_ids_filtered:
        return

    message = (
        f"🆕 Новая заявка на вывод\n\n"
        f"👤 Пользователь: {nick}\n"
        f"💸 Сумма вывода: {amount} RUB\n"
        f"🆔 ID заявки: {request_id}\n\n"
        f"Проверьте заявку в админ-панели для окончательного подтверждения или отклонения."
    )
    
    # Отправляем уведомление каждому администратору из списка
    for admin_id in admin_ids_filtered:
        try:
            await context.bot.send_message(admin_id, message)
            print(f"Уведомление отправлено админу {admin_id}")
        except Exception as e:
            print(f"Ошибка при отправке уведомления админу {admin_id}: {e}")

# Массовая рассылка (инициация)
async def mass_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    message_text = "Введите сообщение для массовой рассылки:"
    keyboard = [[InlineKeyboardButton("Отменить", callback_data="cancel_mass_message")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(message_text, reply_markup=reply_markup)
    context.user_data['mass_message'] = True

# Отмена массовой рассылки
async def cancel_mass_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if 'mass_message' in context.user_data:
        del context.user_data['mass_message']
    await query.message.edit_text("❌ Массовая рассылка отменена.")

# Одиночная рассылка (инициация)
async def single_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    config = load_accounts()
    # Собираем список всех пользователей (ID и никнейм)
    users = [(sec, config[sec].get("nick", "Неизвестный")) for sec in config.sections() if sec.isdigit()]
    if not users:
        await query.message.reply_text("⚠️ Нет пользователей для отправки сообщений.")
        return
    buttons = []
    for user_id, user_name in users:
        buttons.append([InlineKeyboardButton(user_name, callback_data=f"single_user_{user_id}")])
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text("👤 *Выберите пользователя для отправки сообщения:*", reply_markup=reply_markup, parse_mode="Markdown")

# Обработчик выбора пользователя для одиночной рассылки
async def send_single_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split("_")[2])
    context.user_data['single_message_user'] = user_id
    cancel_button = InlineKeyboardButton("Отменить", callback_data="cancel_single_message")
    reply_markup = InlineKeyboardMarkup([[cancel_button]])
    await query.message.reply_text("📝 Введите текст сообщения для отправки выбранному пользователю:", reply_markup=reply_markup)

# Отмена одиночной рассылки
async def cancel_single_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if 'single_message_user' in context.user_data:
        del context.user_data['single_message_user']
    await query.message.reply_text("❌ Одиночная рассылка отменена.")

# Администратор: список отчетов, ожидающих проверки
async def admin_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    config = load_reports()
    reports = [sec for sec in config.sections() if sec.startswith("report_") and config[sec].get("status", "pending") == "pending"]
    if not reports:
        await query.message.edit_text("📋 Нет отчетов, ожидающих проверки.")
        return
    text = "📋 Активные отчеты:\n"
    keyboard = []
    for sec in reports:
        nick = config[sec].get("nick", "Неизвестный")
        rid = sec[len("report_"):]
        text += f"\n🔹 Отчет от {nick} (ID: {rid})"
        keyboard.append([InlineKeyboardButton(f"ID отчета: {rid}", callback_data=f"viewReport_{rid}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

# Администратор: просмотр конкретного отчета (нажатие на кнопку с ID отчета)
async def view_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    report_id = query.data[len("viewReport_"):]
    config = load_reports()
    sec_name = f"report_{report_id}"
    if not config.has_section(sec_name):
        await query.message.edit_text("❌ Отчет не найден или уже обработан.")
        return
    sec = config[sec_name]
    user_id = int(sec.get("user_id", 0))
    nick = sec.get("nick", "Неизвестный")
    date = sec.get("date", "")
    folder = f"reports/{report_id}"
    # Загружаем текст отчета из файла
    report_text = ""
    try:
        with open(os.path.join(folder, "text.txt"), "r", encoding="utf-8") as f:
            report_text = f.read()
    except Exception as e:
        logging.error(f"Не удалось прочитать текст отчета {report_id}: {e}")
        report_text = "[Ошибка чтения текста отчета]"
    # Удаляем сообщение со списком отчетов (для чистоты интерфейса)
    try:
        await query.message.delete()
    except Exception as e:
        logging.error(f"Не удалось удалить сообщение списка отчетов: {e}")
    # Отправляем администратору детали отчета
    detail_text = f"Отчёт {report_id} от {nick} (дата: {date}):\n\n{report_text}"
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data=f"approveReport_{report_id}")],
        [InlineKeyboardButton("❌ Отклонить", callback_data=f"rejectReport_{report_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    admin_chat_id = update.effective_chat.id
    await context.bot.send_message(admin_chat_id, detail_text, reply_markup=reply_markup)
    # Отправляем фотографии отчета (если есть)
    if os.path.isdir(folder):
        files = sorted([f for f in os.listdir(folder) if f.startswith("photo")])
        for fname in files:
            if fname.startswith("photo"):
                try:
                    with open(os.path.join(folder, fname), "rb") as img:
                        await context.bot.send_photo(admin_chat_id, photo=img)
                except Exception as e:
                    logging.error(f"Ошибка отправки фото {fname} отчета {report_id}: {e}")

# Администратор: подтвердить отчет
async def approve_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    report_id = query.data[len("approveReport_"):]
    try:
        config = load_reports()
        sec_name = f"report_{report_id}"
        if not config.has_section(sec_name):
            await query.message.edit_text("❌ Отчет не найден.")
            return
        nick = config[sec_name].get("nick", "Неизвестный")
        user_id = int(config[sec_name].get("user_id", 0)) if config[sec_name].get("user_id") else 0

        # Check if the admin is trying to approve their own report
        if user_id == update.effective_user.id:
            await query.message.edit_text("❌ Администратор не может подтвердить свой же отчет.")
            return

        # Обновляем статус отчета на "approved"
        config[sec_name]["status"] = "approved"
        with open(REPORTS_FILE, "w", encoding="utf-8") as f:
            config.write(f)
        await send_conversion_reminder(update, context)

        # Уведомляем администратора и запрашиваем количество принятых человек
        context.user_data['approve_report_id'] = report_id
        context.user_data['approve_user_id'] = user_id
        await query.message.edit_text(
            f"🕓 Отчёт ID {report_id} от {nick} подтверждён частично.\n"
        )
    except Exception as e:
        logging.error(f"Ошибка при подтверждении отчета {report_id}: {e}")
        await query.message.edit_text("❌ Не удалось подтвердить отчет.")

async def send_conversion_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Путь к изображению
    image_path = os.path.join(os.path.dirname(__file__), "otchet.png")
    if os.path.exists(image_path):
        await update.effective_message.reply_photo(
            photo=open(image_path, "rb"),
            caption="🅰 Необходимо ввести в чат количество монет активности для начисления согласано перечню:"
        )
    else:
        await update.effective_message.reply_text("❌ Изображение otchet.png не найдено!")

    
#Обработчик для ввода количества принятых человек
async def handle_personnel_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Проверяем, есть ли данные о подтвержденном отчете и пользователе
        report_id = context.user_data.get('approve_report_id')
        user_id = context.user_data.get('approve_user_id')
        nick = context.user_data.get('approve_report_nick')

        if report_id and user_id:
            # Пытаемся преобразовать сообщение в число
            personnel_count = int(update.message.text.strip())

            # Обновление ball
            config = load_accounts()
            admin_id = update.effective_user.id

            if config.has_section(str(admin_id)):
                admin_ball = int(config[str(admin_id)].get('ball', '0'))
                config[str(admin_id)]['ball'] = str(admin_ball + 2)  # выдаем 3 балла админку за принятый отчёт

            if config.has_section(str(user_id)):
                user_data = config[str(user_id)]
                user_ball = int(user_data.get('ball', '0'))
                user_data['ball'] = str(user_ball + personnel_count)

                # Начисляем опыт и проверяем повышение уровня
                exp_multiplier = float(user_data.get('exp_multiplier', '1.0'))
                current_exp = int(user_data.get('exp', '0'))
                current_level = int(user_data.get('level', '0'))
                required_exp = 200 + (current_level * 3)

                # Начисляем EXP
                exp_gained = int(personnel_count * exp_multiplier)
                new_exp = current_exp + exp_gained

                # Уведомляем пользователя о начисленных EXP
                exp_message = f"⚡ Вам начислено {exp_gained} очков опыта (EXP)."
                if exp_multiplier > 1.0:
                    percent_increase = (exp_multiplier - 1.0) * 100
                    exp_message += (
                        f"\n🎉 У вас действует уникальная характеристика, которая увеличивает получаемые EXP на {percent_increase:.0f}%."
                        f"\n💡 Данная характеристика является постоянной и получена из центра обмена."
                    )
                await context.bot.send_message(
                    user_id,
                    exp_message
                )
                
                # Проверяем повышение уровня
                level_up = False  # Флаг для отслеживания повышения уровня
                total_bonus = 0  # Количество денег, начисленное за повышение уровня
                while new_exp >= required_exp and current_level < 100:
                    new_exp -= required_exp
                    current_level += 1
                    # --> вот тут вставить!
                    if current_level in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
                        user_data['lvlconf'] = '1'
                    required_exp = 200 + (current_level * 3)
                    level_up = True  # Уровень повышен
                    bonus = current_level # Вычисляем бонус за уровень
                    total_bonus += bonus

                # Если был уровень, добавляем бонус на личный счет
                if total_bonus > 0:
                    current_account = int(user_data.get('osk', '0'))
                    user_data['osk'] = str(current_account + total_bonus)

                # Обновляем ставку
                new_rate = 200_000 + (current_level * 3_000)

                # Сохраняем обновления
                user_data['exp'] = str(new_exp)
                user_data['level'] = str(current_level)
                user_data['daily_rate'] = str(new_rate)
                save_accounts(config)

                # Уведомляем пользователя о повышении уровня
                if level_up:
                    await context.bot.send_message(
                        user_id,
                        f"🎉 Поздравляем! Вы повысили уровень до {current_level}.\n"
                        f"⚡ Ваши очки опыта: {new_exp} из {required_exp}.\n"
                        f"💰 Ваша новая ставка: {new_rate} RUB.\n"
                        f"💈 На ваш личный счет начислено {total_bonus} бустов."
                    )

                    # Уведомляем администраторов 2 и 3 уровня
                    admin_ids = [admin_id for admin_id in load_admin_ids() if int(config[admin_id].get('is_admin', '0')) >= 2]
                    for admin_id in admin_ids:
                        await context.bot.send_message(
                            admin_id,
                            f"🅰 Пользователь {user_data['nick']} повысил уровень до {current_level}.\n"
                            f"💰 Новая ставка: {new_rate} RUB.\n"
                            f"💈 Начислено на личный счет: {total_bonus} бустов."
                        )

            # Уведомление пользователя о подтверждении отчета и начислении баллов
            try:
                await context.bot.send_message(user_id, f"✅ Ваш отчёт (ID {report_id}) подтверждён. Вам начислено {personnel_count} монет активности.")
            except Exception as e:
                logging.error(f"Не удалось уведомить пользователя {user_id} о подтверждении отчета {report_id}: {e}")

            # Уведомление о завершении
            await update.message.reply_text("🅰 Отчёт подтвержден! Вы получили 2 🧿 за модерацию отчёта.")
            update_balls()
            context.user_data.pop('approve_report_id', None)
            context.user_data.pop('approve_user_id', None)
            context.user_data.pop('approve_report_nick', None)
        else:
            # Если нет данных о подтвержденном отчете и пользователе, пропускаем сообщение
            await handle_menu_selection(update, context)
    except ValueError:
        if report_id and user_id:
            await update.message.reply_text("Ошибка: Пожалуйста, введите корректное число.")
        else:
            await handle_menu_selection(update, context)
    except telegram.error.TimedOut:
        logging.error("Ошибка при обработке ввода количества принятых человек: Timed out")
        await update.message.reply_text("❌ Произошла ошибка: запрос к Telegram API истек.")
    except Exception as e:
        logging.error(f"Ошибка при обработке ввода количества принятых человек: {e}")
        if report_id and user_id:
            await update.message.reply_text("❌ Произошла ошибка при обработке ввода.")
        else:
            await handle_menu_selection(update, context)
            

# Администратор: отклонить отчет (запрос причины отклонения)
async def reject_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    report_id = query.data[len("rejectReport_"):]
    try:
        config = load_reports()
        sec_name = f"report_{report_id}"
        if not config.has_section(sec_name):
            await query.message.edit_text("❌ Отчет не найден.")
            return
        # Убираем кнопки и запрашиваем причину отклонения
        await query.message.edit_reply_markup(reply_markup=None)
        context.user_data['reject_report_id'] = report_id
        await query.message.reply_text(f"❓ Пожалуйста, введите причину отклонения отчета ID {report_id}.")
    except Exception as e:
        logging.error(f"Ошибка при инициации отклонения отчета {report_id}: {e}")
        await query.message.edit_text("❌ Не удалось отклонить отчет.")

# Обработчик всех текстовых сообщений (включая этапы создания отчета и рассылок)
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()

    # Delegate to handle_personnel_input if we are in the process of approving a report
    if context.user_data.get('approve_report_id') and context.user_data.get('approve_user_id'):
        await handle_personnel_input(update, context)
        return

    # Existing logic for handling other text messages
    # Если пользователь отменяет отправку отчета кнопкой "Назад"
    if message_text == "Назад" and context.user_data.get('report_state'):
        report_id = context.user_data.get('current_report_id')
        if report_id and os.path.isdir(f"reports/{report_id}"):
            try:
                shutil.rmtree(f"reports/{report_id}")
                logging.info(f"Отчет {report_id} отменен пользователем, папка удалена.")
            except Exception as e:
                logging.error(f"Ошибка при удалении папки отчета {report_id} при отмене: {e}")
        # Сбрасываем состояние отчета
        context.user_data.pop('report_state', None)
        context.user_data.pop('current_report_id', None)
        context.user_data.pop('report_text', None)
        context.user_data.pop('photo_count', None)
        context.user_data.pop('saved_photos', None)
        await update.message.reply_text("❌ Отправка отчета отменена.", reply_markup=ReplyKeyboardRemove())
        await menu(update, context)
        return

    # Если администратор вводит причину отклонения отчета
    if context.user_data.get('reject_report_id'):
        report_id = context.user_data['reject_report_id']
        reason = message_text
        try:
            config = load_reports()
            sec_name = f"report_{report_id}"
            if not config.has_section(sec_name):
                await update.message.reply_text("❌ Отчет не найден.")
            else:
                user_id = int(config[sec_name].get("user_id", 0))
                nick = config[sec_name].get("nick", "Неизвестный")
                # Удаляем файлы отчета (папку с фото и текстом)
                folder = f"reports/{report_id}"
                if os.path.isdir(folder):
                    try:
                        shutil.rmtree(folder)
                        logging.info(f"Папка отчета {report_id} удалена.")
                    except Exception as e:
                        logging.error(f"Ошибка при удалении папки отчета {report_id}: {e}")
                # Удаляем запись об отчете из .ini-файла
                config.remove_section(sec_name)
                with open(REPORTS_FILE, "w", encoding="utf-8") as f:
                    config.write(f)
                logging.info(f"Отчет {report_id} отклонен и удален.")
                # Уведомляем пользователя об отклонении и причине
                try:
                    await context.bot.send_message(user_id, f"❌ Ваш отчёт (ID {report_id}) отклонён. Причина: {reason}")
                except Exception as e:
                    logging.error(f"Ошибка при отправке причины отклонения пользователю {user_id} для отчета {report_id}: {e}")
                    await update.message.reply_text("⚠️ Не удалось отправить сообщение пользователю.")
                else:
                    await update.message.reply_text(f"❌ Отчёт ID {report_id} отклонён. Пользователь уведомлен.")
        except Exception as e:
            logging.error(f"Ошибка при обработке отклонения отчета {report_id}: {e}")
            await update.message.reply_text("❌ Произошла ошибка при отклонении отчета.")
        finally:
            context.user_data.pop('reject_report_id', None)
        return

    # Обработка текста отчета от пользователя (этап отправки текста отчета)
    if context.user_data.get('report_state') == 'await_text':
        report_text = message_text
        report_id = generate_random_id()
        config = load_reports()
        # Генерируем уникальный идентификатор отчета, который отсутствует в файле
        while config.has_section(f"report_{report_id}"):
            report_id = generate_random_id()
        try:
            os.makedirs("reports", exist_ok=True)
            folder = f"reports/{report_id}"
            os.makedirs(folder, exist_ok=True)
            with open(os.path.join(folder, "text.txt"), "w", encoding="utf-8") as f:
                f.write(report_text)
        except Exception as e:
            logging.error(f"Ошибка при сохранении текста отчета: {e}")
            await update.message.reply_text("❌ Не удалось сохранить текст отчета. Попробуйте позже.")
            context.user_data.pop('report_state', None)
            return
        # Переходим к этапу добавления фотографий
        context.user_data['current_report_id'] = report_id
        context.user_data['report_text'] = report_text
        context.user_data['photo_count'] = 0
        context.user_data['saved_photos'] = []
        context.user_data['report_state'] = 'await_photos'
        await update.message.reply_text(
            "📷 Теперь отправьте до 10 фотографий для отчета. "
            "Отправьте их по одному сообщению. Когда закончите, отправьте команду /done. "
            "Если у вас нет фотографий, отправьте /done сразу."
        )
        return

    # Если ожидаются фотографии, а пользователь прислал текст – напоминаем команду /done
    if context.user_data.get('report_state') == 'await_photos':
        await update.message.reply_text(
            "📷 Пожалуйста, продолжайте отправлять фотографии или введите /done, если больше фотографий нет."
        )
        return

    # Пользователь вводит "войти" вручную (дублирует нажатие кнопки)
    if message_text.lower() == "авторизация":
        await login(update, context)
        return

    # Отправка сообщений для массовой рассылки
    if 'mass_message' in context.user_data:
        # Получаем всех пользователей из файла
        config = load_accounts()
        user_sections = [sec for sec in config.sections() if sec.isdigit()]
        successes = 0
        for sec in user_sections:
            try:
                await context.bot.send_message(chat_id=int(sec), text=message_text)
                successes += 1
            except Exception as e:
                logging.error(f"Ошибка при отправке пользователю {sec}: {e}")
        await update.message.reply_text(f"Массовая рассылка завершена. Отправлено {successes} сообщений.")
        context.user_data.pop('mass_message', None)
        return

    # Отправка сообщения выбранному пользователю (одиночная рассылка)
    if 'single_message_user' in context.user_data:
        user_id = context.user_data['single_message_user']
        try:
            await context.bot.send_message(chat_id=user_id, text=message_text)
            await update.message.reply_text("✅ Сообщение успешно отправлено пользователю.")
        except Exception as e:
            await update.message.reply_text(f"❌ Не удалось отправить сообщение: {e}")
        context.user_data.pop('single_message_user', None)
        return
    
        # Обработка изменения параметра пользователя
    if 'handle_change_param' in context.user_data:
        user_id = context.user_data.get('user_id')
        param = context.user_data.get('change_param')
        if not user_id or not param:
            await update.message.reply_text("Ошибка: Нет данных для изменения.")
            return

        value = update.message.text.strip()
        config = load_accounts()
        if config.has_section(user_id):
            config[user_id][param] = value
            save_accounts(config)
            await update.message.reply_text(f"Значение {param} пользователя {user_id} успешно изменено на {value}.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="edit_user")]]))
        else:
            await update.message.reply_text("Ошибка: Пользователь не найден.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="edit_user")]]))
        return

    # Обработка изменения ника
    if context.user_data.get('handle_change_nick'):
        user_id = context.user_data.get('user_id')
        new_nick = message_text
        config = load_accounts()
        if config.has_section(user_id):
            config[user_id]['nick'] = new_nick
            save_accounts(config)
            await update.message.reply_text(f"Ник пользователя {user_id} изменен на {new_nick}.",
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]]))
        else:
            await update.message.reply_text("Ошибка: Пользователь не найден.",
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]]))
        context.user_data.pop('handle_change_nick', None)
        context.user_data.pop('user_id', None)
        return

    # Обработка изменения Ball
     # Handle ball change
    if context.user_data.get('handle_change_ball'):
        user_id = context.user_data.get('user_id')
        try:
            change_type = context.user_data['handle_change_ball']
            change_amount = int(message_text)
            config = load_accounts()
            if config.has_section(user_id):
                current_ball = int(config[user_id].get('ball', '0'))
                new_ball = current_ball + change_amount if change_type == 'add' else current_ball - change_amount
                config[user_id]['ball'] = str(new_ball)
                save_accounts(config)
                await update.message.reply_text(f"Монеты активности пользователя {user_id} изменены на {new_ball}.",
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]]))
                # Notify user about the ball change
                if change_type == 'add':
                    await context.bot.send_message(chat_id=int(user_id), text=f"🅱 Администратор добавил Вам на счёт {change_amount} монет активности. Теперь на балансе {new_ball}.")
                else:
                    await context.bot.send_message(chat_id=int(user_id), text=f"🅱 Администратор снял у Вас {change_amount} монет активности. Теперь на балансе {new_ball}.")
            else:
                await update.message.reply_text("Ошибка: Пользователь не найден.",
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]]))
        except ValueError:
            await update.message.reply_text("Ошибка: введите целое число для монет активности.")
            return
        context.user_data.pop('handle_change_ball', None)
        return

    # Обработка изменения личного счета
    if context.user_data.get('handle_change_account'):
        user_id = context.user_data.get('user_id')
        try:
            change_type = context.user_data['handle_change_account']
            change_amount = int(message_text)
            config = load_accounts()
            if config.has_section(user_id):
                current_account = int(config[user_id].get('personal_account', '0'))
                new_account = current_account + change_amount if change_type == 'add' else current_account - change_amount
                config[user_id]['personal_account'] = str(new_account)
                save_accounts(config)
                await update.message.reply_text(f"Личный счёт пользователя {user_id} изменён на {new_account}.",
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]]))
                # Notify user about the account change
                if change_type == 'add':
                    await context.bot.send_message(chat_id=int(user_id), text=f"💳 Администратор добавил Вам на личный счёт {change_amount} RUB. Теперь на счёте {new_account} RUB.")
                else:
                    await context.bot.send_message(chat_id=int(user_id), text=f"💳 Администратор снял у Вас с личного счёта {change_amount} RUB. Теперь на счёте {new_account} RUB.")
            else:
                await update.message.reply_text("Ошибка: Пользователь не найден.",
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]]))
        except ValueError:
            await update.message.reply_text("Ошибка: введите целое число для суммы.")
            return
        context.user_data.pop('handle_change_account', None)
        return

    # Если пользователь нажал кнопку "Регистрация"
    if message_text.lower() == "регистрация":
        # Запускаем регистрацию, только если она не в процессе
        if not await check_access(update, context):
            return  # блокируем доступ
        if not context.user_data.get('registration_in_progress'):
            await start_registration(update, context)
        return

    # Если в данный момент идёт диалог регистрации, продолжаем обработку по этапам
    if context.user_data.get('registration_in_progress'):
        if context.user_data.get('reg_stage') == 'nick':
            await reg_name(update, context)
        elif context.user_data.get('reg_stage') == 'realname':
            await reg_realname(update, context)
        elif context.user_data.get('reg_stage') == 'birthdate':
            await reg_birthdate(update, context)
        return

    # Обработка других команд (например, "Авторизация")
    if message_text.lower() == "авторизация":
        await login(update, context)
        return

     # Обработка изменения расчетного дня
    if context.user_data.get('handle_change_rd'):
        try:
            new_rd = datetime.strptime(message_text, "%Y-%m-%d")
            set_rd(new_rd)
            await update.message.reply_text(f"Расчетный день установлен на {new_rd.strftime('%Y-%m-%d')}.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="admin")]]))
            context.user_data.pop('handle_change_rd', None)
        except ValueError:
            await update.message.reply_text("Ошибка: Пожалуйста, введите корректную дату в формате ГГГГ-ММ-ДД.")
        return
    
    # Если ни одно из специальных состояний не активно – обрабатываем как команду меню
    await handle_menu_selection(update, context)

# Обработчик полученных фотографий во время отправки отчета
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('report_state') != 'await_photos':
        return
    report_id = context.user_data.get('current_report_id')
    photo_count = context.user_data.get('photo_count', 0)
    if photo_count >= 10:
        await update.message.reply_text("Вы уже отправили 10 фотографий. Отправьте /done для завершения отчета.")
        return
    try:
        file_id = update.message.photo[-1].file_id
        file = await context.bot.get_file(file_id)
        folder = f"reports/{report_id}"
        os.makedirs(folder, exist_ok=True)
        photo_count += 1
        # Определяем расширение файла фотографии
        ext = ""
        if file.file_path:
            ext = os.path.splitext(file.file_path)[1]
            if not ext:
                ext = ".jpg"
        else:
            ext = ".jpg"
        filename = f"photo{photo_count:02d}{ext}"
        path = os.path.join(folder, filename)
        await file.download_to_drive(path)
        context.user_data['photo_count'] = photo_count
        saved_photos = context.user_data.get('saved_photos', [])
        saved_photos.append(filename)
        context.user_data['saved_photos'] = saved_photos
        logging.info(f"Фото {filename} сохранено для отчета {report_id}.")
    except Exception as e:
        logging.error(f"Ошибка при обработке фото для отчета: {e}")
        await update.message.reply_text("❌ Не удалось сохранить фото. Попробуйте еще раз или отмените отчёт командой /cancel.")
        return
    if context.user_data['photo_count'] == 10:
        await update.message.reply_text("✅ Вы отправили максимальное количество фото (10). Теперь отправьте /done для завершения отчета.")

# Команда /done – завершение отправки отчета (после фотографий)
async def finish_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('report_state') != 'await_photos':
        await update.message.reply_text("У вас нет активного отчета для завершения.")
        return
    report_id = context.user_data.get('current_report_id')
    report_text = context.user_data.get('report_text', '')
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    nick = user_info['nick'] if user_info else (update.effective_user.username or update.effective_user.first_name or "")
    date_str = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        config = load_reports()
        config[f"report_{report_id}"] = {
            "user_id": str(user_id),
            "nick": nick,
            "date": date_str,
            "status": "pending"
        }
        with open(REPORTS_FILE, "w", encoding="utf-8") as f:
            config.write(f)
        logging.info(f"Отчет {report_id} сохранен в файл данных.")
    except Exception as e:
        logging.error(f"Ошибка при сохранении отчета {report_id} в файл: {e}")
        await update.message.reply_text("❌ Произошла ошибка при сохранении отчета. Попробуйте позже.")
        # Если сохранить не удалось, удаляем папку отчета
        folder = f"reports/{report_id}"
        if os.path.isdir(folder):
            try:
                shutil.rmtree(folder)
                logging.info(f"Удалена папка отчета {report_id} из-за ошибки сохранения.")
            except Exception as e2:
                logging.error(f"Ошибка удаления папки отчета {report_id} при отмене: {e2}")
        # Сбрасываем состояние отчета у пользователя
        context.user_data.pop('report_state', None)
        context.user_data.pop('current_report_id', None)
        context.user_data.pop('report_text', None)
        context.user_data.pop('photo_count', None)
        context.user_data.pop('saved_photos', None)
        return
    # Уведомляем администраторов 2 и 3 уровней
    await update.message.reply_text(f"✅ Ваш отчёт отправлен и ожидает проверки. ID вашего отчета: {report_id}. Вы получите уведомление после проверки.")
    admin_ids_filtered = load_admin_ids()  # Ensure this function returns only admin IDs with levels 2 and 3
    for admin_id in admin_ids_filtered:
        try:
            await context.bot.send_message(admin_id, f"🅰 Новый отчёт от пользователя {nick} (ID: {report_id}). Проверьте панель администратора для просмотра.")
        except Exception as e:
            logging.error(f"Ошибка при отправке уведомления админу {admin_id} о новом отчете {report_id}: {e}")
        # Сбрасываем состояние отчета у пользователя
    context.user_data.pop('report_state', None)
    context.user_data.pop('current_report_id', None)
    context.user_data.pop('report_text', None)
    context.user_data.pop('photo_count', None)
    context.user_data.pop('saved_photos', None)

# Команда /cancel – досрочная отмена создания отчета
async def cancel_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('report_state'):
        await update.message.reply_text("У вас нет активного отчета для отмены.")
        return
    report_id = context.user_data.get('current_report_id')
    if report_id and os.path.isdir(f"reports/{report_id}"):
        try:
            shutil.rmtree(f"reports/{report_id}")
            logging.info(f"Отчет {report_id} отменен пользователем, данные удалены.")
        except Exception as e:
            logging.error(f"Ошибка при удалении данных отчета {report_id} при отмене: {e}")
    context.user_data.pop('report_state', None)
    context.user_data.pop('current_report_id', None)
    context.user_data.pop('report_text', None)
    context.user_data.pop('photo_count', None)
    context.user_data.pop('saved_photos', None)
    await update.message.reply_text("❌ Отправка отчета отменена.", reply_markup=ReplyKeyboardRemove())
    await menu(update, context)
    
# =============================================
# СИСТЕМА РЕГИСТРАЦИИ
# =============================================
async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context):
        return  # блокируем доступ
    user_id = update.effective_user.id
    accounts = load_accounts()

    with open("reg.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)

    # Если аккаунт уже существует, уведомляем пользователя и очищаем состояние регистрации
    if accounts.has_section(str(user_id)):
        await update.message.reply_text("Вы уже зарегистрированы. Для входа используйте кнопку «Авторизация».")
        context.user_data.pop('registration_in_progress', None)
        return ConversationHandler.END

    # Проверка: есть ли заявка в registrations.ini
    user_id = str(update.effective_user.id)
    # Проверка: есть ли заявка в registrations.ini
    config = configparser.ConfigParser()
    config.read(REGISTRATIONS_FILE, encoding="utf-8")
    for section in config.sections():
        if str(config[section].get('user_id', '')) == user_id:
            await update.message.reply_text(
            "❌ Ваша заявка уже отправлена и ожидает модерации! Ожидайте решения администратора бота."
            )
        context.user_data.pop('registration_in_progress', None)
        return ConversationHandler.END

    # Если аккаунт не существует, запускаем диалог регистрации
    context.user_data['registration_in_progress'] = True
    context.user_data['reg_stage'] = 'nick'
    await update.message.reply_text(
        "✏️ Введите ваш никнейм:",
        reply_markup=get_back_keyboard()
    )
    return REG_NAME

async def reg_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка никнейма"""
    if update.message.text == "Назад":
        # Возвращаем пользователя к меню с кнопками "Войти" и "Регистрация"
        await update.message.reply_text(
            "Для входа в систему нажмите кнопку ниже.",
            reply_markup=get_login_keyboard()
        )
        return ConversationHandler.END  # Завершаем диалог регистрации
    
    context.user_data['reg_data'] = {'nick': update.message.text}
    await update.message.reply_text(
        "👤 Введите ваше реальное имя:",
        reply_markup=get_back_keyboard()
    )
    return REG_REALNAME

async def reg_realname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка реального имени"""
    if update.message.text == "Назад":
        # Возвращаем пользователя к вводу никнейма
        await update.message.reply_text(
            "✏️ Введите ваш никнейм:",
            reply_markup=get_back_keyboard()
        )
        return REG_NAME
    
    context.user_data['reg_data']['realname'] = update.message.text
    await update.message.reply_text(
        "🎂 Введите дату рождения (ДД.ММ.ГГГГ):",
        reply_markup=get_back_keyboard()
    )
    return REG_BIRTHDATE

async def reg_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка даты рождения и сохранение заявки"""
    if update.message.text == "Назад":
        await update.message.reply_text(
            "👤 Введите ваше реальное имя:",
            reply_markup=get_back_keyboard()
        )
        return REG_REALNAME
    
    # Валидация даты
    try:
        datetime.strptime(update.message.text, "%d.%m.%Y")
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ",
            reply_markup=get_back_keyboard()
        )
        return REG_BIRTHDATE

    context.user_data['reg_data']['birthdate'] = update.message.text
    context.user_data['reg_stage'] = 'position'
    await update.message.reply_text(
        "💼 Введите вашу должность/ранг (например: Заместитель, Хранитель, XVIP):",
        reply_markup=get_back_keyboard()
    )
    return REG_POSITION_MANUAL

ALLOWED_POSITIONS = {"Заместитель": ("0", "🔳 Заместитель"),
                     "Хранитель": ("1", "🟫 Хранитель"),
                     "XVIP": ("-2", "🟨 XVIP")}

async def reg_position_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        await update.message.reply_text(
            "🎂 Введите дату рождения (ДД.ММ.ГГГГ):",
            reply_markup=get_back_keyboard()
        )
        return REG_BIRTHDATE

    position_input = update.message.text.strip()
    if position_input not in ALLOWED_POSITIONS:
        await update.message.reply_text(
            "❌ Ошибка: допустимы только должности 'Заместитель', 'Хранитель' или 'XVIP'.\nПожалуйста, введите одну из них!",
            reply_markup=get_back_keyboard()
        )
        return REG_POSITION_MANUAL

    # Всё ок, сохраняем заявку
    context.user_data['reg_data']['position'] = position_input
    reg_data = context.user_data['reg_data']
    reg_id = str(uuid4())[:8]

    config = configparser.ConfigParser()
    config.read(REGISTRATIONS_FILE, encoding="utf-8")
    config[reg_id] = {
        'user_id': str(update.effective_user.id),
        'nick': reg_data['nick'],
        'realname': reg_data['realname'],
        'birthdate': reg_data['birthdate'],
        'position': reg_data['position'],
        'status': 'pending',
        'timestamp': str(datetime.now())
    }
    with open(REGISTRATIONS_FILE, "w", encoding="utf-8") as f:
        config.write(f)

    await notify_admins_about_new_registration(reg_id, reg_data['nick'], reg_data['position'], context)

    await update.message.reply_text(
        "✅ Заявка отправлена на модерацию!",
        reply_markup=get_login_keyboard()
    )
    context.user_data.clear()
    return ConversationHandler.END

# Новый обработчик
async def view_registrations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = configparser.ConfigParser()

    # Проверка, существует ли файл
    if not os.path.exists(REGISTRATIONS_FILE):
        print(f"❌ Файл {REGISTRATIONS_FILE} не найден!")
        # Используем update.callback_query.message.reply_text, если обновление это callback_query
        if update.callback_query:
            await update.callback_query.message.reply_text("📭 Нет заявок на регистрацию (файл отсутствует).")
        else:
            await update.message.reply_text("📭 Нет заявок на регистрацию (файл отсутствует).")
        return

    config.read(REGISTRATIONS_FILE, encoding="utf-8")

    # Отладка: Выводим все секции файла
    print(f"🔍 Загруженные заявки: {config.sections()}")

    keyboard = []  # Список кнопок для отображения заявок

    # Проходим по секциям файла и проверяем статус заявок
    for section in config.sections():
        status = config[section].get('status', 'unknown')  # Получаем статус заявки
        print(f"📝 Заявка ID {section}: статус {status}")  # Отладка

        # Если заявка в статусе "pending", добавляем её в список
        if status == 'pending':
            keyboard.append([
                InlineKeyboardButton(f"{config[section]['nick']} ({section})", callback_data=f"reg_detail_{section}")
            ])

    # Если нет заявок с нужным статусом, информируем пользователя
    if not keyboard:
        if update.callback_query:
            await update.callback_query.message.reply_text("📭 Нет заявок на регистрацию.")
        else:
            await update.message.reply_text("📭 Нет заявок на регистрацию.")
        return

    # Отправляем сообщение с кнопками для администрирования заявок
    if update.callback_query:
        await update.callback_query.message.edit_text(
            "📝 Заявки на регистрацию:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            "📝 Заявки на регистрацию:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


def load_admin_ids():
    config = load_accounts()  # Функция для загрузки аккаунтов
    admin_ids = []
    for user_id, user_info in config.items():
        if int(user_info.get('is_admin', -1)) >= 2:
            admin_ids.append(user_id)
    return admin_ids

async def notify_admins_about_new_registration(reg_id: str, nick: str, position: str, context: ContextTypes.DEFAULT_TYPE):
    admin_ids = load_admin_ids()
    for admin_id in admin_ids:
        try:
            await context.bot.send_message(
                admin_id,
                f"🅰 Новая заявка на регистрацию:\nID: {reg_id}\nНикнейм: {nick}\nДолжность: {position}"
            )
        except Exception as e:
            logging.error(f"Ошибка при отправке уведомления админу {admin_id}: {e}")

                    
# Просмотр деталей заявки
async def reg_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reg_id = update.callback_query.data.split("_")[2]
    config = configparser.ConfigParser()
    config.read(REGISTRATIONS_FILE, encoding="utf-8")

    position = config[reg_id].get('position', 'Не указана')
    msg = f"""📄 Заявка {reg_id}
👤 Ник: {config[reg_id]['nick']}
📛 Имя: {config[reg_id]['realname']}
🎂 Дата рождения: {config[reg_id]['birthdate']}
💼 Должность: {position}"""

    keyboard = [
        [
            InlineKeyboardButton("✅ Одобрить", callback_data=f"reg_approve_{reg_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reg_reject_{reg_id}")
        ]
    ]
    await update.callback_query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

# Одобрение заявки
# Одобрение заявки
async def reg_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reg_id = update.callback_query.data.split("_")[2]

    config = configparser.ConfigParser()
    config.read(REGISTRATIONS_FILE, encoding="utf-8")
    accounts = configparser.ConfigParser()
    accounts.read(ACCOUNTS_FILE, encoding="utf-8")

    if reg_id not in config.sections():
        await update.callback_query.message.edit_text("❌ Заявка не найдена.")
        return

    user_id = config[reg_id]['user_id']
    position = config[reg_id].get('position', '-')
    level = int(config[reg_id].get('level', '0'))
    daily_rate = get_daily_rate_by_level(level)

    # Присваиваем уровень админки и эмодзи
    is_admin, emoji_position = ALLOWED_POSITIONS.get(position, ("-1", "⬜ Гость"))

    accounts[user_id] = {
        'nick': config[reg_id]['nick'],
        'position': position,
        'daily_rate': daily_rate,
        'warnings': config[reg_id].get('warnings', '0'),
        'predicted_payment': config[reg_id].get('predicted_payment', '0'),
        'personal_account': config[reg_id].get('personal_account', '0'),
        'rating': config[reg_id].get('rating', '0'),
        'is_admin': is_admin,
        'realname': config[reg_id].get('realname', ''),
        'daterod': config[reg_id].get('birthdate', ''),
        'ball': '0',
        'pop': '0',
        'osk': '0',
        'level': '0',
        'exp': '0',
        'exp_multiplier': '1.0',
        'lvlconf': '0'
    }
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        accounts.write(f)

    # Уведомление пользователю с эмодзи
    try:
        await context.bot.send_message(
            user_id,
            f"✅ Ваша регистрация одобрена!\n"
            f"Вам присвоена должность: {emoji_position}\n"
            f"Теперь вы можете войти в систему."
        )
    except Exception as e:
        print(f"Ошибка при отправке уведомления пользователю: {e}")
        await update.callback_query.message.edit_text("❌ Ошибка при отправке уведомления пользователю.")
        return

    config.remove_section(reg_id)
    with open(REGISTRATIONS_FILE, "w", encoding="utf-8") as f:
        config.write(f)

    await update.callback_query.message.edit_text(
        f"✅ Заявка одобрена!\nПользователь получил должность: {emoji_position}"
    )


# Добавляем обработчик отмены регистрации
async def reg_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отклонение заявки на регистрацию"""
    query = update.callback_query
    await query.answer()
    reg_id = query.data.split('_')[-1]
    
    config = configparser.ConfigParser()
    config.read(REGISTRATIONS_FILE, encoding="utf-8")
    
    # Удаление заявки
    user_id = config[reg_id]['user_id']
    config.remove_section(reg_id)
    
    with open(REGISTRATIONS_FILE, "w", encoding="utf-8") as f:
        config.write(f)
    
    # Уведомление пользователю
    await context.bot.send_message(
        user_id,
        "❌ Ваша заявка на регистрацию отклонена. Обратитесь к администратору."
    )
    await query.edit_message_text(f"❌ Заявка #{reg_id} отклонена")

# ОБРАБОТЧИК ОТМЕНЫ РЕГИСТРАЦИИ
async def cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена процесса регистрации"""
    await update.message.reply_text(
        "❌ Регистрация отменена",
        reply_markup=get_login_keyboard()  # Возвращаем пользователя к клавиатуре входа
    )
    context.user_data.clear()  # Очищаем временные данные
    return ConversationHandler.END

conv_reg = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^Регистрация$"), start_registration)],
    states={
        REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_name)],
        REG_REALNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_realname)],
        REG_BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_birthdate)],
        REG_POSITION_MANUAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_position_manual)],
        ConversationHandler.TIMEOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_input)]
    },
    fallbacks=[CommandHandler("cancel", cancel_registration)]
)
# =============================================
# РАЗРЯДНАЯ СИСТЕМА
# =============================================

# Порядок должностей (обратный, как просили ранее)
POSITIONS = ["Лидер семьи", "Старший заместитель", "Заместитель", "Хранитель", "XVIP"]

async def manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    config = load_accounts()

    # Экран выбора пользователя по должности
    if query.data.startswith("show_users_"):
        position = query.data.replace("show_users_", "")
        users = [
            (user_id, config[user_id].get('nick', 'Неизвестный'))
            for user_id in config.sections()
            if user_id.isdigit() and config[user_id].get('position', '') == position
        ]
        keyboard = [
            [InlineKeyboardButton(nick, callback_data=f"edit_user_{user_id}")]
            for user_id, nick in users
        ]
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_positions")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = f"Пользователи с должностью <b>{position}</b>:" if users else f"Нет пользователей с должностью <b>{position}</b>."
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        return

    # Экран управления пользователем (по admin_level)
    if query.data.startswith("edit_user_"):
        user_id = query.data.replace("edit_user_", "")
        context.user_data['user_id'] = user_id

        # Получить информацию о текущем пользователе (админ, который управляет)
        current_user_info = get_user_info(update.effective_user.id)
        admin_level = int(current_user_info.get('is_admin', 0)) if current_user_info else 0

        # Получить информацию о выбранном пользователе (которого редактируем)
        user_info = config[user_id]
        nick = user_info.get('nick', 'Неизвестный')
        position = user_info.get('position', '')
        balance = user_info.get('personal_account', '0')
        boosts = user_info.get('osk', '0')

        if admin_level == 1:
            keyboard = [
                [InlineKeyboardButton("📊 Статистика", callback_data=f"statistics_{user_id}")],
                [InlineKeyboardButton("🔙 Назад", callback_data=f"show_users_{position}")]
            ]
        elif admin_level == 2:
            keyboard = [
                [InlineKeyboardButton("✏️ Никнейм", callback_data=f"change_nick_{user_id}")],
                [InlineKeyboardButton("⚠➕️ Предупреждение", callback_data=f"add_warning_{user_id}")],
                [InlineKeyboardButton("⚠➖ Предупреждение", callback_data=f"remove_warning_{user_id}")],
                [InlineKeyboardButton("📊 Статистика", callback_data=f"statistics_{user_id}")],
                [InlineKeyboardButton("📋 История отчётов", callback_data=f"report_history_{user_id}")],
                [InlineKeyboardButton("🔙 Назад", callback_data=f"show_users_{position}")]
            ]
        elif admin_level == 3:
            keyboard = [
                [InlineKeyboardButton("✏️ Никнейм", callback_data=f"change_nick_{user_id}")],
                [InlineKeyboardButton("📌 Должность", callback_data=f"change_position_{user_id}")],
                [InlineKeyboardButton("⚠➕️ Предупреждение", callback_data=f"add_warning_{user_id}")],
                [InlineKeyboardButton("⚠➖ Предупреждение", callback_data=f"remove_warning_{user_id}")],
                [InlineKeyboardButton("🧿 Монеты активности", callback_data=f"change_ball_{user_id}")],
                [InlineKeyboardButton("💳 Личный счёт", callback_data=f"change_personal_account_{user_id}")],
                [InlineKeyboardButton("📊 Статистика", callback_data=f"statistics_{user_id}")],
                [InlineKeyboardButton("📋 История отчётов", callback_data=f"report_history_{user_id}")],
                [InlineKeyboardButton("🅰 Админ права", callback_data=f"set_admin_rights_{user_id}")],
                [InlineKeyboardButton("🗑 Удалить аккаунт", callback_data=f"delete_user_account_{user_id}")],
                [InlineKeyboardButton("🔙 Назад", callback_data=f"show_users_{position}")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("🔙 Назад", callback_data=f"show_users_{position}")]
            ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        text = (f"<b>Управление пользователем.</b>\n"
                f"👤 <b>Никнейм:</b> {nick}\n"
                f"🏷 <b>Должность:</b> {position}\n")
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        return

    # Если нажата "Назад" из списка пользователей, возвращаем к списку должностей
    if query.data == "back_to_positions":
        keyboard = [
            [InlineKeyboardButton(pos, callback_data=f"show_users_{pos}")]
            for pos in POSITIONS
        ]
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("Выберите должность для просмотра пользователей:", reply_markup=reply_markup)
        return

    # Первый экран: выбор должности
    keyboard = [
        [InlineKeyboardButton(pos, callback_data=f"show_users_{pos}")]
        for pos in POSITIONS
    ]
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("Выберите должность для просмотра пользователей:", reply_markup=reply_markup)
    

async def change_nick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = context.user_data.get('user_id')
    context.user_data['handle_change_nick'] = True

    # Кнопка "Назад"
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="cancel_change_nick")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text("Введите новый ник пользователя:", reply_markup=reply_markup)

async def handle_back_to_user_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = context.user_data.get('user_id')
    context.user_data.pop('handle_change_nick', None)
    await edit_user(update, context)

async def change_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Извлекаем user_id из context.user_data, он был установлен в edit_user
    user_id = context.user_data.get('user_id')
    if not user_id:
        await query.message.edit_text("Ошибка: не выбран пользователь.")
        return
    keyboard = [
        [InlineKeyboardButton("ХРАНИТЕЛЬ", callback_data="set_position_хранитель")],
        [InlineKeyboardButton("XVIP", callback_data="set_position_xvip")],
        [InlineKeyboardButton("ЗАМ", callback_data="set_position_заместитель")],
        [InlineKeyboardButton("СТАРШИЙ ЗАМ", callback_data="set_position_старший_заместитель")],
        [InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("Выберите новую должность для пользователя:", reply_markup=reply_markup)

async def set_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Извлекаем ключ позиции, например "хранитель" из "set_position_хранитель"
    pos_key = query.data.replace("set_position_", "")
    # Используем ключ 'user_id' из context.user_data, установленный в edit_user
    user_id = context.user_data.get('user_id')
    if not user_id:
        await query.message.edit_text("Ошибка: не выбран пользователь.")
        return
    # Сопоставление для позиции и уровня админских прав
    position_mapping = {
        "xvip": ("XVIP", "-2"),
        "хранитель": ("Хранитель", "1"),
        "заместитель": ("Заместитель", "0"),
        "старший_заместитель": ("Старший заместитель", "2")
    }
    if pos_key in position_mapping:
        position, is_admin = position_mapping[pos_key]
        config = load_accounts()
        if config.has_section(user_id):
            config[user_id]['position'] = position
            config[user_id]['is_admin'] = is_admin
            # Для позиции "старший заместитель" дополнительно устанавливаем rank = "10"
            if pos_key == "старший_заместитель":
                config[user_id]['level'] = "100"
            save_accounts(config)
            # Отправка уведомления админу(ам)
            try:
                notification_admin = f"🔔 Уведомление: Пользователь {config[user_id]['nick']} теперь имеет должность: {position}"
                # admin_ids - глобальная переменная, содержащая список ID администраторов
                for admin in admin_ids:
                    await context.bot.send_message(chat_id=admin, text=notification_admin)
            except Exception as e:
                logging.error(f"Ошибка отправки уведомления админу: {e}")
            # Отправка уведомления пользователю
            try:
                notification_user = f"✅ Ваша должность изменена на: {position}"
                await context.bot.send_message(chat_id=int(user_id), text=notification_user)
            except Exception as e:
                logging.error(f"Ошибка отправки уведомления пользователю: {e}")
            await query.message.edit_text(f"Должность пользователя изменена на: {position}")
        else:
            await query.message.edit_text("Ошибка: пользователь не найден.")
    else:
        await query.message.edit_text("Ошибка: неизвестная должность.")


async def add_warning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = context.user_data.get('user_id')
    config = load_accounts()
    if config.has_section(user_id):
        warnings = int(config[user_id].get('warnings', '0')) + 1
        config[user_id]['warnings'] = str(warnings)
        save_accounts(config)
        await query.message.edit_text(f"Предупреждение добавлено. Теперь предупреждений: {warnings}.",
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]]))
        user_info = get_user_info(user_id)
        await context.bot.send_message(user_id, f"⚠️ Вам выдано предупреждение. Теперь у вас {warnings} предупреждений.")
        await context.bot.send_message(admin_ids[0], f"⚠️ Пользователю {user_info['nick']} выдано предупреждение. Теперь у него {warnings} предупреждений.")
    else:
        await query.message.edit_text("Ошибка: Пользователь не найден.",
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]]))

async def remove_warning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = context.user_data.get('user_id')
    config = load_accounts()
    if config.has_section(user_id):
        warnings = max(0, int(config[user_id].get('warnings', '0')) - 1)
        config[user_id]['warnings'] = str(warnings)
        save_accounts(config)
        await query.message.edit_text(f"Предупреждение снято. Теперь предупреждений: {warnings}.",
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]]))
        user_info = get_user_info(user_id)
        await context.bot.send_message(user_id, f"✅ С вас снято предупреждение. Теперь у вас {warnings} предупреждений.")
        await context.bot.send_message(admin_ids[0], f"✅ С пользователя {user_info['nick']} снято предупреждение. Теперь у него {warnings} предупреждений.")
    else:
        await query.message.edit_text("Ошибка: Пользователь не найден.",
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]]))

 
async def change_ball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = context.user_data.get('user_id')
    keyboard = [
        [InlineKeyboardButton("Пополнить 🅱", callback_data="add_ball")],
        [InlineKeyboardButton("Снять 🅱", callback_data="remove_ball")],
        [InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("Выберите действие:", reply_markup=reply_markup)

async def add_ball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['handle_change_ball'] = 'add'
    await query.message.edit_text("Введите количество монет активности для пополнения:")

async def remove_ball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['handle_change_ball'] = 'remove'
    await query.message.edit_text("Введите количество монет активности для снятия:")
    
async def change_personal_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = context.user_data.get('user_id')
    keyboard = [
        [InlineKeyboardButton("Пополнить 💳", callback_data="add_account")],
        [InlineKeyboardButton("Снять 💳", callback_data="remove_account")],
        [InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("Выберите действие:", reply_markup=reply_markup)

async def add_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['handle_change_account'] = 'add'
    await query.message.edit_text("Введите сумму для пополнения счёта:")

async def remove_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['handle_change_account'] = 'remove'
    await query.message.edit_text("Введите сумму для снятия со счёта:")
    

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = context.user_data.get('user_id')
    user_info = get_user_info(user_id)
    if user_info:
        current_level = int(user_info.get('level', '0'))
        current_exp = int(user_info.get('exp', '0'))
        required_exp = 200 + (current_level * 3)
        predicted_payment_formatted = locale.format_string("%d", user_info['predicted_payment'], grouping=True).replace(' ', '.')
        daily_rate_formatted = locale.format_string("%d", user_info['daily_rate'], grouping=True).replace(' ', '.')
        personal_account_formatted = locale.format_string("%d", int(user_info['personal_account']), grouping=True).replace(' ', '.')
        message = (
            f"📋 Статистика(ID: {user_id})\n\n"
            f"👤 Никнейм: {user_info['nick']}\n"
            f"🔮 Реальное имя: {user_info['realname']}\n"
            f"🎂 Дата рождения: {user_info['daterod']}\n"
            f"💼 Должность: {user_info['position']}\n"
            f"🧗 Уровень: {current_level}\n"
            f"⚡ Очки опыта: {current_exp} из {required_exp}\n"
            f"💰 Ставка за монету: {daily_rate_formatted} RUB\n"
            f"⚠️ Предупреждения: {user_info['warnings']}\n"
            f"🧿 Монеты активности: {user_info['ball']}\n"
            f"💈 Бусты: {user_info['osk']}\n"
            f"💸 Зарплата: {predicted_payment_formatted} RUB\n"
            f"💳 Личный счет: {personal_account_formatted} RUB"
        )
            
        await query.message.edit_text(message, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]]))
    else:
        await query.message.edit_text("Информация о пользователе не найдена.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]]))
        

# Добавьте новую функцию для создания клавиатуры с сообщением о недостатке прав
def get_limited_keyboard():
    keyboard = [[KeyboardButton("Для выдачи прав обратитесь к администратору бота.")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

async def fetch_updates():
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post("https://api.telegram.org/bot{token}/getUpdates")
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as exc:
        logging.error(f"An error occurred while requesting {exc.request.url!r}.")
    except httpx.HTTPStatusError as exc:
        logging.error(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
    except httpx.TimeoutException as exc:
        logging.error("Request timed out.")

#ЗАКРЫТИЕ НЕДЕЛИ
async def close_week_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Инициализируем стадию подтверждения, если ещё не задана
    if 'week_close_stage' not in context.user_data:
        context.user_data['week_close_stage'] = 1
    else:
        context.user_data['week_close_stage'] += 1

    # Если нажали "Нет" – сброс и возврат в меню
    if query.data == "week_close_no":
        context.user_data.pop('week_close_stage', None)
        await query.edit_message_text("Операция прервана. Возврат в панель администратора.")
        # можно вызвать функцию admin() для возврата в админ-панель
        await admin(update, context)
        return

    # Если стадия подтверждения меньше 3 – спрашиваем снова
    if context.user_data['week_close_stage'] < 3:
        keyboard = [
            [InlineKeyboardButton("Да", callback_data="week_close_yes")],
            [InlineKeyboardButton("Нет", callback_data="week_close_no")]
        ]
        confirmation_text = (
            "☢️ Вы точно хотите закрыть расчётную неделю?\n"
            "Это функция необратима.\n"
            "После активации этой функции произойдет:\n"
            "🔺 Перевод всех монет активности на личный счёт по курсу разряда с учетом предупреждений.\n"
            "🔺 Обнуление всех монет активности пользователей.\n"
            "🔺 Расчёт выплаты.\n"
            "🔺 Уведомление всех пользователей о зачислении выплаты на счёт.\n\n\n"
            f"🔴 Потвердите действие {context.user_data['week_close_stage']}/3:"
        )
        await query.edit_message_text(
            confirmation_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        # Если это третий "Да", выполняем закрытие недели
        await execute_week_close(update, context)
        # Сброс подтверждения после выполнения
        context.user_data.pop('week_close_stage', None)

        
async def execute_week_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = load_accounts()
    notifications = []  # для формирования сообщений

    for section in config.sections():
        if section.isdigit():
            ball = int(config[section].get('ball', '0'))
            warnings = int(config[section].get('warnings', '0'))
            level = int(config[section].get('level', '0'))  # Получаем уровень пользователя
            
            # Расчёт зарплаты на основе уровня
            daily_rate = get_daily_rate_by_level(level)  # Используем ставку, основанную на уровне
            salary = ball * daily_rate * (1 - 0.25 * warnings)  # Формула расчёта зарплаты
            salary = int(salary)  # Округляем до целого числа
            
            current_account = int(config[section].get('personal_account', '0'))
            new_account = current_account + salary
            config[section]['personal_account'] = str(new_account)
            config[section]['ball'] = "0"  # Обнуляем монеты активности
            
            nick = config[section].get('nick', 'Неизвестный')
            notifications.append((int(section), nick, salary))
    
    save_accounts(config)
    
    # Рассылка уведомлений для обычных пользователей (админам 1 уровня не отправляем)
    for user_id, nick, computed_salary in notifications:
        user_info = get_user_info(user_id)
        if user_info and int(user_info.get('is_admin', 0)) == 1:
            continue
        text = (
            f"✅ Закрытие недели выполнено.\n"
            f"💵 На ваш счет зачислено: {computed_salary} RUB.\n"
            "🧿 Ваши монеты активности обнулены."
        )
        try:
            await context.bot.send_message(user_id, text)
        except Exception as e:
            logging.error(f"Ошибка отправки уведомления пользователю {user_id}: {e}")
    
    # Дополнительно отправляем уведомления администраторам с is_admin > 1 (если нужно)
    for user_id, nick, computed_salary in notifications:
        user_info = get_user_info(user_id)
        if user_info and int(user_info.get('is_admin', 0)) > 1:
            admin_text = (
                "✅ Закрытие недели выполнено.\n"
                f"Пользователь {nick} получил зачисление: {computed_salary} RUB, и его монеты активности обнулены."
            )
            try:
                await context.bot.send_message(user_id, admin_text)
            except Exception as e:
                logging.error(f"Ошибка отправки уведомления админу {user_id}: {e}")
    
    # Уведомляем об успешном закрытии недели
    await update.callback_query.edit_message_text("✅ Закрытие недели выполнено. Все платежи зачислены, а монеты активности обнулены.")
    
# Обработчик изменения расчетного дня
async def change_rd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['handle_change_rd'] = True
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="cancel_change_rd")]
    ]
    await query.message.edit_text("Введите новый расчетный день (в формате ГГГГ-ММ-ДД):", reply_markup=InlineKeyboardMarkup(keyboard))


# Функция для отмены изменения расчетного дня
async def cancel_change_rd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if 'handle_change_rd' in context.user_data:
        del context.user_data['handle_change_rd']
    await query.message.edit_text("Изменение расчетного дня отменено.", reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Назад", callback_data="admin")]]
    ))


async def gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)

    if len(context.args) != 1:
        await update.message.reply_text("❌ Неверный формат команды. Используйте: /gift <PROMO>")
        return

    promo_code = context.args[0].strip().lower()  # Приводим промокод к нижнему регистру и убираем пробелы

    logging.info(f"Пользователь ввёл промокод: {promo_code}")

    # Чтение файла промокодов
    promo_config = configparser.ConfigParser()
    promo_config.optionxform = str  # Отключаем автоматическое изменение регистра
    try:
        promo_config.read(PROMO_FILE, encoding="utf-8")
    except Exception as e:
        logging.error(f"Ошибка чтения файла промокодов: {e}")
        await update.message.reply_text("❌ Произошла ошибка при доступе к файлу промокодов.")
        return

    logging.info(f"Содержимое файла промокодов: {promo_config.sections()}")

    # Приводим секции файла к нижнему регистру для сравнения
    promo_sections = [section.strip().lower() for section in promo_config.sections()]
    logging.info(f"Секции (обработанные): {promo_sections}")

    # Проверяем наличие промокода
    if promo_code not in promo_sections:
        await update.message.reply_text("❌ Неверный промокод.")
        return

    # Получаем оригинальное имя секции
    original_promo_code = promo_config.sections()[promo_sections.index(promo_code)]

    logging.info(f"Оригинальное имя промокода в файле: {original_promo_code}")

    # Проверка на использование промокода
    activation_config = configparser.ConfigParser()
    try:
        activation_config.read(PROMO_ACTIVATIONS_FILE, encoding="utf-8")
    except Exception as e:
        logging.error(f"Ошибка чтения файла активаций промокодов: {e}")
        await update.message.reply_text("❌ Произошла ошибка при доступе к истории активаций.")
        return

    if activation_config.has_section(str(user_id)) and promo_code in activation_config[str(user_id)]:
        await update.message.reply_text("❌ Вы уже активировали этот промокод.")
        return

    # Получаем данные промокода
    promo_data = promo_config[original_promo_code]

    # Начисление бонусов
    ball_bonus = int(promo_data.get('ball', 0))
    money_bonus = int(promo_data.get('money', 0))
    exp_bonus = int(promo_data.get('exp', 0))
    shards_bonus = int(promo_data.get('shards', 0))  # Новый параметр для осколков

    config = load_accounts()
    if config.has_section(str(user_id)):
        user_section = config[str(user_id)]
        user_section['ball'] = str(int(user_section.get('ball', '0')) + ball_bonus)
        user_section['personal_account'] = str(int(user_section.get('personal_account', '0')) + money_bonus)
        user_section['exp'] = str(int(user_section.get('exp', '0')) + exp_bonus)
        user_section['osk'] = str(int(user_section.get('osk', '0')) + shards_bonus)  # Добавляем осколки
        save_accounts(config)

    # Обновление активаций промокодов
    if not activation_config.has_section(str(user_id)):
        activation_config.add_section(str(user_id))
    activation_config[str(user_id)][original_promo_code] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(PROMO_ACTIVATIONS_FILE, "w", encoding="utf-8") as f:
            activation_config.write(f)
    except Exception as e:
        logging.error(f"Ошибка записи в файл активаций промокодов: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обновлении файла активаций.")
        return

    # Формируем сообщение для пользователя
    message = "✅ Промокод успешно активирован!\n"
    if ball_bonus > 0:
        message += f"🧿 Монеты активности: {ball_bonus}\n"
    if money_bonus > 0:
        message += f"💰 Деньги: {money_bonus} RUB\n"
    if exp_bonus > 0:
        message += f"⚡ EXP: {exp_bonus}\n"
    if shards_bonus > 0:
        message += f"💈 Бусты: {shards_bonus}"

    await update.message.reply_text(message)

    # Уведомление админам
    admin_ids = load_admin_ids()
    for admin_id in admin_ids:
        try:
            await context.bot.send_message(
                admin_id,
                f"🅰 Пользователь {user_info['nick']} активировал промокод {original_promo_code}.\n"
                f"🧿 Монеты активности: {ball_bonus}\n"
                f"💰 Деньги: {money_bonus} RUB\n"
                f"⚡ EXP: {exp_bonus}\n"
                f"💈 Бусты: {shards_bonus}"
            )
        except Exception as e:
            logging.error(f"Ошибка при отправке уведомления админу {admin_id}: {e}")

async def setpromocode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    
    # Проверка прав администратора
    if int(user_info.get('is_admin', 0)) < 3:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    # Проверка аргументов
    if len(context.args) != 5:
        await update.message.reply_text(
            "❌ Неверный формат команды. Используйте: /setpromocode <PROMO> <ball> <money> <exp> <shards>"
        )
        return
    
    promo_code, ball, money, exp, shards = context.args
    try:
        ball = int(ball)
        money = int(money)
        exp = int(exp)
        shards = int(shards)  # Новый параметр для осколков
    except ValueError:
        await update.message.reply_text("❌ Все бонусы (монеты активности, деньги, EXP, бусты) должны быть целыми числами.")
        return
    
    # Работа с конфигурацией промокодов
    promo_config = configparser.ConfigParser()
    promo_config.read(PROMO_FILE, encoding="utf-8")
    
    if not promo_config.has_section(promo_code):
        promo_config.add_section(promo_code)
    
    promo_config[promo_code]['ball'] = str(ball)
    promo_config[promo_code]['money'] = str(money)
    promo_config[promo_code]['exp'] = str(exp)
    promo_config[promo_code]['shards'] = str(shards)  # Сохраняем осколки
    
    with open(PROMO_FILE, "w", encoding="utf-8") as f:
        promo_config.write(f)
    
    # Уведомление пользователя
    await update.message.reply_text(
        f"✅ Промокод {promo_code} успешно создан!\n"
        f"🧿 Монеты активности: {ball}\n"
        f"💰 Деньги: {money} RUB\n"
        f"⚡ EXP: {exp}\n"
        f"💈 Бусты: {shards}"
    )

async def resetpromocode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    
    # Проверка прав администратора
    if int(user_info.get('is_admin', 0)) < 3:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    # Проверка аргументов
    if len(context.args) != 1:
        await update.message.reply_text("❌ Неверный формат команды. Используйте: /resetpromocode <PROMO>")
        return
    
    promo_code = context.args[0].strip().upper()  # Приводим промокод к верхнему регистру
    
    # Чтение файла промокодов
    promo_config = configparser.ConfigParser()
    promo_config.optionxform = str  # Отключаем изменение регистра ключей
    try:
        promo_config.read(PROMO_FILE, encoding="utf-8")
    except Exception as e:
        logging.error(f"Ошибка чтения файла промокодов: {e}")
        await update.message.reply_text("❌ Произошла ошибка при доступе к файлу промокодов.")
        return
    
    # Логируем секции для диагностики
    logging.info(f"Секции в файле промокодов: {promo_config.sections()}")
    
    # Приводим все секции к верхнему регистру для сравнения
    promo_sections = [section.upper() for section in promo_config.sections()]
    
    if promo_code not in promo_sections:
        await update.message.reply_text("❌ Промокод не найден.")
        return
    
    # Удаление промокода
    original_promo_code = promo_config.sections()[promo_sections.index(promo_code)]  # Получаем оригинальное имя секции
    promo_config.remove_section(original_promo_code)
    
    try:
        with open(PROMO_FILE, "w", encoding="utf-8") as f:
            promo_config.write(f)
    except Exception as e:
        logging.error(f"Ошибка записи в файл промокодов: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обновлении файла промокодов.")
        return
    
    # Подтверждение пользователю
    await update.message.reply_text(f"✅ Промокод {promo_code} успешно удален!")
    
    # Логирование успешного удаления
    logging.info(f"Администратор {user_info['nick']} удалил промокод {promo_code}.")
    

async def report_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.debug("Запуск функции report_history")
    query = update.callback_query
    await query.answer()
    user_id = query.data.split("_")[2]
    
    # Загрузка отчетов из файла reports.ini
    config = configparser.ConfigParser()
    config.read("reports.ini", encoding="utf-8")  # Указываем кодировку utf-8
    
    reports = []
    for section in config.sections():
        if config.has_option(section, "user_id") and config.get(section, "user_id") == user_id:
            reports.append((section, config[section]))
    
    if not reports:
        logging.debug("У пользователя нет отчетов")
        await query.message.edit_text("У пользователя нет отчетов.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]]))
        return

    sorted_reports = sorted(reports, key=lambda x: datetime.strptime(x[1]['date'], "%Y-%m-%d %H:%M:%S"))
    
    keyboard = [[InlineKeyboardButton(f"Отчёт {report_id.split('_')[1]} ({report_data['date']})", callback_data=f"viewreport_{user_id}_{report_id.split('_')[1]}")]
                for report_id, report_data in sorted_reports]
    keyboard.append([InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    logging.debug("Отправка списка отчетов пользователю")
    await query.message.edit_text("Выберите отчёт для просмотра:", reply_markup=reply_markup)

async def view_full_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.debug("Запуск функции view_full_report")
    query = update.callback_query
    await query.answer()
    logging.debug(f"Callback data: {query.data}")
    
    try:
        user_id, report_id = query.data.split("_")[1:3]
    except ValueError as e:
        logging.error(f"Ошибка разбора callback data: {e}")
        await query.message.edit_text("Некорректные данные. Пожалуйста, попробуйте еще раз.")
        return
    
    config = configparser.ConfigParser()
    config.read("reports.ini", encoding="utf-8")  # Указываем кодировку utf-8
    
    if not config.has_section(f"report_{report_id}"):
        logging.debug("Отчёт не найден")
        await query.message.edit_text("Отчёт не найден.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"report_history_{user_id}")]]))
        return
    
    report_data = config[f"report_{report_id}"]
    folder = os.path.join("reports", report_id)
    
    report_text = ""
    text_file_path = os.path.join(folder, "text.txt")
    logging.debug(f"Проверка существования текстового файла по пути: {text_file_path}")
    if os.path.exists(text_file_path):
        try:
            with open(text_file_path, "r", encoding="utf-8") as f:  # Указываем кодировку utf-8
                report_text = f.read()
            logging.debug("Текст отчета успешно прочитан")
        except Exception as e:
            logging.error(f"Не удалось прочитать текст отчета {report_id}: {e}")
            report_text = "[Ошибка чтения текста отчета]"
    else:
        logging.debug("Текст отчета не найден")
        report_text = "[Текст отчета не найден]"
    
    detail_text = f"Отчёт {report_id} от {report_data['nick']} (дата: {report_data['date']}):\n\n{report_text}"
    
    keyboard = [[InlineKeyboardButton("Назад", callback_data=f"report_history_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    logging.debug("Отправка детальной информации об отчете пользователю")
    await query.message.edit_text(detail_text, reply_markup=reply_markup)
    
    if os.path.isdir(folder):
        files = sorted([f for f in os.listdir(folder) if f.startswith("photo")])
        logging.debug(f"Найдено {len(files)} фото в папке отчета")
        for fname in files:
            if fname.startswith("photo"):
                try:
                    with open(os.path.join(folder, fname), "rb") as img:
                        await context.bot.send_photo(update.effective_chat.id, photo=img)
                    logging.debug(f"Фото {fname} успешно отправлено")
                except Exception as e:
                    logging.error(f"Ошибка отправки фото {fname} отчета {report_id}: {e}")

async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, что передано достаточно аргументов
    if len(context.args) < 5:
        await update.message.reply_text(
            "❌ Неверный формат команды. Используйте: /send <никнейм> <монеты активности> <бусты> <опыт> <деньги>"
        )
        return

    # Извлекаем никнейм, монеты активности, осколки, опыт и деньги из аргументов
    *nick_parts, activity_coins, shards, exp, money = context.args
    target_nick = " ".join(nick_parts)  # Объединяем части никнейма с пробелами

    try:
        activity_coins = int(activity_coins)
        shards = int(shards)
        exp = int(exp)
        money = int(money)
    except ValueError:
        await update.message.reply_text(
            "❌ Количество монет активности, бустов, опыта и денег должно быть числом."
        )
        return

    # Проверка на положительные значения
    if activity_coins < 0 or shards < 0 or exp < 0 or money < 0:
        await update.message.reply_text(
            "❌ Количество монет активности, бустов, опыта и денег должно быть положительным числом."
        )
        return

    # Получение информации об отправителе
    sender_id = str(update.effective_user.id)
    accounts = load_accounts()

    if not accounts.has_section(sender_id):
        await update.message.reply_text("❌ Ошибка: информация о вашем аккаунте не найдена.")
        return

    sender_info = accounts[sender_id]
    sender_activity_coins = int(sender_info.get("ball", 0))
    sender_shards = int(sender_info.get("osk", 0))
    sender_exp = int(sender_info.get("exp", 0))
    sender_personal_account = int(sender_info.get("personal_account", 0))

    # Проверка, хватает ли ресурсов у отправителя
    if sender_activity_coins < activity_coins:
        await update.message.reply_text("❌ У вас недостаточно монет активности для перевода.")
        return

    if sender_shards < shards:
        await update.message.reply_text("❌ У вас недостаточно бустов для перевода.")
        return

    if sender_exp < exp:
        await update.message.reply_text("❌ У вас недостаточно опыта для перевода.")
        return

    if sender_personal_account < money:
        await update.message.reply_text("❌ У вас недостаточно денег на личном счёте для перевода.")
        return

    # Поиск пользователя по никнейму
    recipient_id = None
    for section in accounts.sections():
        if accounts[section].get("nick", "").lower() == target_nick.lower():
            recipient_id = section
            break

    if not recipient_id:
        await update.message.reply_text("❌ Пользователь с таким никнеймом не найден.")
        return

    # Проверка: отправитель и получатель не должны быть одним и тем же пользователем
    if sender_id == recipient_id:
        await update.message.reply_text("❌ Вы не можете отправить ресурсы самому себе.")
        return

    # Обновление балансов
    recipient_info = accounts[recipient_id]
    recipient_activity_coins = int(recipient_info.get("ball", 0))
    recipient_shards = int(recipient_info.get("osk", 0))
    recipient_exp = int(recipient_info.get("exp", 0))
    recipient_personal_account = int(recipient_info.get("personal_account", 0))

    # Снятие ресурсов у отправителя
    sender_info["ball"] = str(sender_activity_coins - activity_coins)
    sender_info["osk"] = str(sender_shards - shards)
    sender_info["exp"] = str(sender_exp - exp)
    sender_info["personal_account"] = str(sender_personal_account - money)

    # Начисление ресурсов получателю
    recipient_info["ball"] = str(recipient_activity_coins + activity_coins)
    recipient_info["osk"] = str(recipient_shards + shards)
    recipient_info["exp"] = str(recipient_exp + exp)
    recipient_info["personal_account"] = str(recipient_personal_account + money)

    # Сохранение изменений в accounts.ini
    save_accounts(accounts)

    # Уведомление отправителя
    await update.message.reply_text(
        f"✅ Вы успешно перевели:\n"
        f"🧿 Монеты активности: {activity_coins}\n"
        f"💈 Бусты: {shards}\n"
        f"⚡ Опыт: {exp}\n"
        f"💳 Деньги: {money} RUB\n"
        f"пользователю {target_nick}."
    )

    # Уведомление получателя
    try:
        await context.bot.send_message(
            chat_id=int(recipient_id),
            text=(
                f"💱 Вы получили перевод от {sender_info.get('nick', 'Неизвестно')}!\n\n"
                f"🧿 Монеты активности: {activity_coins}\n"
                f"💈 Бусты: {shards}\n"
                f"⚡ Опыт: {exp}\n"
                f"💳 Деньги: {money} RUB"
            ),
        )
    except Exception as e:
        logging.error(f"Ошибка при уведомлении пользователя {recipient_id}: {e}")

    # Уведомление администраторов 2 уровня и выше
    for section in accounts.sections():
        admin_level = int(accounts[section].get("is_admin", 0))
        if admin_level >= 2:  # Проверка уровня администратора
            try:
                await context.bot.send_message(
                    chat_id=int(section),
                    text=(
                        f"🅰 Уведомление о переводе.\n"
                        f"👤 Отправитель: {sender_info.get('nick', 'Неизвестно')}\n"
                        f"👤 Получатель: {recipient_info.get('nick', 'Неизвестно')}\n"
                        f"🧿 Монеты активности: {activity_coins}\n"
                        f"💈 Бусты: {shards}\n"
                        f"⚡ Опыт: {exp}\n"
                        f"💳 Деньги: {money} RUB"
                    ),
                )
            except Exception as e:
                logging.error(f"Ошибка при уведомлении администратора {section}: {e}")

async def delete_user_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = context.user_data.get('user_id')  # ID пользователя для удаления

    # Проверка прав администратора (только 3 уровень)
    current_user_info = get_user_info(update.effective_user.id)
    admin_level = int(current_user_info.get('is_admin', 0)) if current_user_info else 0
    if admin_level < 3:
        await query.message.edit_text("⛔ У вас нет прав для удаления аккаунта.")
        return

    # Проверка существования аккаунта
    config = load_accounts()
    if not config.has_section(user_id):
        await query.message.edit_text("Пользователь не найден.")
        return

    nick = config[user_id].get("nick", "Неизвестный")
    config.remove_section(user_id)
    save_accounts(config)

    await query.message.edit_text(f"✅ Аккаунт пользователя {nick} (ID: {user_id}) успешно удалён.")
    # Оповещение пользователя и переброс на /start (меню авторизации)
    try:
        await context.bot.send_message(
            chat_id=int(user_id), 
            text="❌ Ваш аккаунт был удалён администратором.\n\nДля повторного входа используйте меню авторизации.",
            reply_markup=get_login_keyboard()
        )
    except Exception:
        pass
    
def load_set(set_id):
    """Загрузка набора из sets.ini, возвращает словарь параметров."""
    config = configparser.ConfigParser(interpolation=None)
    config.read("sets.ini", encoding="utf-8")
    set_id = str(int(str(set_id).strip()))
    if set_id in config.sections():
        data = config[set_id]
        return {
            "name": data.get("name", ""),
            "required_boosts": int(data.get("required_boosts", 0)),
            "ball": int(data.get("ball", 0)),
            "exp": int(data.get("exp", 0)),
            "money": int(data.get("money", 0)),
            "limit": int(data.get("limit", 0)),
            "limitiz": int(data.get("limitiz", 0))
        }
    return None

def save_set_limitiz(set_id, new_limitiz):
    """Сохраняет новый limitiz в sets.ini"""
    config = configparser.ConfigParser(interpolation=None)
    config.read("sets.ini", encoding="utf-8")
    set_id = str(int(str(set_id).strip()))
    if set_id in config.sections():
        config[set_id]["limitiz"] = str(new_limitiz)
        with open("sets.ini", "w", encoding="utf-8") as f:
            config.write(f)

def get_sets_limits():
    """Возвращает список лимитов для всех наборов из sets.ini"""
    config = configparser.ConfigParser(interpolation=None)
    config.read("sets.ini", encoding="utf-8")
    limits_list = []
    for set_id in config.sections():
        name = config[set_id].get("name", f"Набор {set_id}")
        limit = int(config[set_id].get("limit", 0))
        limitiz = int(config[set_id].get("limitiz", 0))
        if limit == 0:
            remain = "∞"
            total = "∞"
        else:
            remain = str(max(0, limit - limitiz))
            total = str(limit)
        limits_list.append(
            f"▫️ <b>{name}</b> — осталось <b>{remain}</b> из <b>{total}</b>"
        )
    return "\n".join(limits_list)

def get_admins_ids(level_min=2):
    config = load_accounts()
    return [int(sec) for sec in config.sections() 
            if sec.isdigit() and int(config[sec].get("is_admin", "0")) >= level_min]

async def buyn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_info = get_user_info(user_id)

    # Проверка аргумента
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("❌ Неверный формат команды! Используйте: /buyn <номер_набора>")
        return

    set_id = str(int(context.args[0].strip()))  # строка без ведущих нулей
    set_data = load_set(set_id)
    if not set_data:
        config = configparser.ConfigParser()
        config.read("sets.ini", encoding="utf-8")
        await update.message.reply_text(
            f"❌ Набор с таким номером не найден!\n"
            f"Доступные наборы: {', '.join(config.sections())}"
        )
        return

    # Проверка лимита всего набора
    limit = set_data["limit"]
    limitiz = set_data["limitiz"]
    # Проверка лимита всего набора (если лимит > 0)
    if limit > 0 and limitiz >= limit:
        await update.message.reply_text(
            f"❌ Набор \"{set_data['name']}\" закончился!\n"
            f"Максимум покупок: {limit}."
        )
        return

    boosts = int(user_info.get("osk", 0))
    required_boosts = set_data["required_boosts"]

    if boosts < required_boosts:
        await update.message.reply_text(
            f"❌ Недостаточно бустов!\n"
            f"Для покупки набора \"{set_data['name']}\" нужно {required_boosts} 💈, а у вас только {boosts} 💈."
        )
        return

    # --- Обновление данных пользователя ---
    config_accounts = load_accounts()
    sec = config_accounts[user_id]
    sec["osk"] = str(boosts - required_boosts)
    sec["ball"] = str(int(sec.get("ball", 0)) + set_data["ball"])
    sec["exp"] = str(int(sec.get("exp", 0)) + set_data["exp"])
    sec["personal_account"] = str(int(sec.get("personal_account", 0)) + set_data["money"])
    save_accounts(config_accounts)

    # --- Увеличение общего лимита в sets.ini ---
    new_limitiz = limitiz + 1
    save_set_limitiz(set_id, new_limitiz)

    # Сообщение пользователю
    if limit == 0:
        remaining_str = "∞"
        total_str = "∞"
    else:
        remaining_str = str(max(0, limit - new_limitiz))
        total_str = str(limit)

    await update.message.reply_text(
        f"✅️ Вы успешно купили {set_data['name']}!\n"
        f"🧿 ➕ {set_data['ball']} монет активности\n"
        f"⚡ ➕ {set_data['exp']} опыта\n"
        f"💳 ➕ {set_data['money']} RUB\n"
        f"💈 ➖ {required_boosts} бустов\n"
        f"Осталось наборов: {remaining_str} из {total_str}"
    )

    # Уведомление админам > 2 уровня
    admin_ids = get_admins_ids(level_min=2)
    msg = (f"🅰 Покупка набора.\n"
           f"👤 Пользователь: {user_info.get('nick', user_id)}\n"
           f"💈 Списано бустов: {required_boosts}\n"
           f"Набор: {set_data['name']} (ID: {set_id})\n"
           f"🧿 ➕{set_data['ball']} | ⚡ ➕{set_data['exp']} | 💳 ➕{set_data['money']} RUB\n"
           f"Осталось наборов: {remaining_str} из {total_str}")
    for admin_id in admin_ids:
        if admin_id != int(user_id):  # не отправлять себе
            try:
                await context.bot.send_message(admin_id, msg)
            except Exception:
                pass

def get_sets_limits():
    """Возвращает список лимитов для всех наборов из sets.ini"""
    config = configparser.ConfigParser()
    config.read("sets.ini", encoding="utf-8")
    limits_list = []
    for set_id in config.sections():
        name = config[set_id].get("name", f"Набор {set_id}")
        limit = int(config[set_id].get("limit", 0))
        limitiz = int(config[set_id].get("limitiz", 0))
        limits_list.append(
            f"▫️ <b>{name}</b> — осталось <b>{max(0, limit - limitiz)}</b> из <b>{limit}</b>"
        )
    return "\n".join(limits_list)

def get_main_exchange_keyboard():
    keyboard = [
        [KeyboardButton("Наборы")],
        [KeyboardButton("Кейсы")],
        [KeyboardButton("Характеристики")],
        [KeyboardButton("Подтверждение уровня")],
        [KeyboardButton("Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_main_nabors_keyboard():
    keyboard = [
        [KeyboardButton("Обычные наборы")],
        [KeyboardButton("Сезонные наборы")],
        [KeyboardButton("Лимитированные наборы")],
        [KeyboardButton("Назад в центр обмена")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_to_exchange_keyboard():
    # Кнопка Назад, возвращающая в центр обмена
    keyboard = [[KeyboardButton("Назад в центр обмена")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def active(update, context):
    today_str = datetime.now().strftime("%d.%m.%Y")
    # Получаем цены из bot_data (или дефолтные значения, если еще не обновились)
    sell_price = context.bot_data.get('sell_price', 500_000)
    buy_price = context.bot_data.get('buy_price', 400_000)
    with open("obmen.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    message = (
        f"🏢 В центре обмена вы можете обменять свои <b>бусты</b> на товары.\n"
        f"💈 Бусты - основная валюта для покупки и продажи по курсу ниже. Цены на бусты обновляются каждый час.\n\n"
        f"📈 Покупка.\n"
        f"1 💈 = {sell_price:,}".replace(",", ".") + " RUB 💳\n"
        f"🟢 КУПИТЬ: /buyboost [количество]\n\n"
        f"📉 Продажа.\n"
        f"1 💈 = {buy_price:,}".replace(",", ".") + " RUB 💳\n"
        f"🔴 ПРОДАТЬ: /sellboost [количество]\n\n"
        f"🗓 Товары и курсы обмена актуальны на <b>{today_str}</b>.\n\n"
        f"<b>Выберите из представленного меню необходимый вариант:</b>\n"
    )
    await update.message.reply_text(message, reply_markup=get_main_exchange_keyboard(), parse_mode="HTML")

async def usual_sets(update, context):
    with open("obmen.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    message = (
        f"🎁 <b>Обычные наборы.</b>\n"
        f"💼 <b>Рейтинговый набор максимальный (500 💈):</b>\n"
        f"В набор входит: 100 🧿 200 ⚡ 100КК 💳\n"
        f"Для покупки введите <code>/buyn 1</code>\n\n"
        f"🕶 <b>Рейтинговый набор средний (250 💈):</b>\n"
        f"В набор входит: 50 🧿 100 ⚡ 50КК 💳\n"
        f"Для покупки введите <code>/buyn 2</code>\n\n"
        f"🧸 <b>Рейтинговый набор минимальный (100 💈):</b>\n"
        f"В набор входит: 50 ⚡ 25КК 💳\n"
        f"Для покупки введите <code>/buyn 3</code>\n\n"
    )
    await update.message.reply_text(message, reply_markup=get_back_to_nabors_keyboard(), parse_mode="HTML")

async def seasonal_sets(update, context):
    with open("obmen.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    message = (
        f"🎁 <b>Сезонные наборы.</b>\n"
        f"🍂 <b>Осенний набор (10 💈):</b>\n"
        f"В набор входит: 3 🧿 20 ⚡\n"
        f"Для покупки введите <code>/buyn 4</code>\n\n"
    )
    await update.message.reply_text(message, reply_markup=get_back_to_nabors_keyboard(), parse_mode="HTML")

async def limited_sets(update, context):
    with open("obmen.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    message = (
        f"💎 <b>Лимитированные наборы.</b>\n"
        f"❌ Наборов нет в наличии.\n\n"
    )
    await update.message.reply_text(message, reply_markup=get_back_to_nabors_keyboard(), parse_mode="HTML")

async def characteristics(update, context):
    with open("obmen.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    message = (
        f"🕶️ <b>Характеристики.</b>\n"
        f"🆙 <b>+ 50% к получаемым EXP (500 💈):</b>\n"
        f"Для покупки введите <code>/buych 1</code>\n\n"
        f"🆙 <b>+ 100% к получаемым EXP (1К 💈):</b>\n"
        f"Для покупки введите <code>/buych 2</code>\n\n"
    )
    await update.message.reply_text(message, reply_markup=get_back_to_exchange_keyboard(), parse_mode="HTML")

async def pod(update, context):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    current_level = int(user_info.get('level', 0)) if user_info else 0
    lvlconf = int(user_info.get('lvlconf', 0)) if user_info else 0

    confirm_status = "☑️ Не требуется" if lvlconf == 0 else "❗️ Требуется"

    # Словарь стоимости подтверждения по уровням
    confirm_costs = {10: 50, 20: 100, 30: 150, 40: 200, 50: 250, 60: 300, 70: 350, 80: 400, 90: 450, 100: 500}
    # Определение стоимости для текущего уровня
    cost_str = ""
    if current_level in confirm_costs:
        cost_str = f"🔔 Стоимость подтверждения: <b>{confirm_costs[current_level]} 💈</b>\n"
    else:
        cost_str = ""
        
    with open("obmen.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    message = (
        f"☑️ <b>Подтверждение уровня.</b>\n"
        f"Ваш текущий уровень: <b>{current_level}</b>\n"
        f"Статус подтверждения: <b>{confirm_status}</b>\n"
        f"{cost_str}"
        f"Подтверждение уровня — это сохранение ранжировки уровня путем оплаты.\n\n"
        f"☑ Для подтверждения уровня введите команду <code>/lvlconf</code>\n"
        f"❌ Во время подтверждения уровня <b>заблокирована система отчётов</b>.\n\n"
    )
    await update.message.reply_text(message, reply_markup=get_back_to_exchange_keyboard(), parse_mode="HTML")
    
async def case(update, context):
    with open("obmen.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    message = (
        "📦️ <b>Кейсы.</b>\n\n"
        "💳 <b>MONEY CASE (25 💈)</b>\n"
        "Содержимое кейса: <b>от 100K 💳 до 100KK 💳</b>\n"
        "Для открытия кейса введите <code>/case 1</code>\n\n"
        "⚡ <b>EXP CASE (25 💈)</b>\n"
        "Содержимое кейса: <b>от 10 ⚡ до 1K ⚡</b>\n"
        "Для открытия кейса введите <code>/case 2</code>\n\n"
        "🧿 <b>COIN ACTIVE CASE (25 💈)</b>\n"
        "Содержимое кейса: <b>от 5 🧿 до 100 🧿</b>\n"
        "Для открытия кейса введите <code>/case 3</code>\n\n"
        "💈 <b>BOOST CASE (50 💈)</b>\n"
        "Содержимое кейса: <b>от 20 💈 до 200 💈</b>\n"
        "Для открытия кейса введите <code>/case 4</code>\n\n"
        f"🧈 <b>LEGENDARY CASE (111 💈)</b>\n"
        f"Содержимое кейса:\n"
        f"⚀ <b>от 100K 💳 до 100KK 💳</b>\n"
        f"⚁ <b>от 10 💈 до 100 💈</b>\n"
        f"⚂ <b>от 10 ⚡ до 1K ⚡</b>\n"
        f"⚃ <b>от 5 🧿 до 100 🧿</b>\n"
        f"Для открытия кейса введите <code>/lcase</code>\n\n"
    )
    await update.message.reply_text(message, reply_markup=get_back_to_exchange_keyboard(), parse_mode="HTML")

# Оповещение всех пользователей (функция уже есть в коде)
async def notify_all_users(context, text, parse_mode="HTML"):
    config = load_accounts()
    for user_id in config.sections():
        if user_id.isdigit():
            try:
                await context.bot.send_message(chat_id=int(user_id), text=text, parse_mode=parse_mode)
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

async def case_open(update, context):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    nick = user_info['nick'] if user_info else 'Неизвестный'
    args = context.args

    if not args or len(args) == 0 or not args[0].isdigit():
        await update.message.reply_text("❌ Укажите номер кейса: /case <номер>")
        return

    case_id = int(args[0])
    cases = {
        1: {
            "name": "MONEY CASE 💳",
            "cost": 25,
            "prizes": [
                (100_000, 35),
                (500_000, 25),
                (1_000_000, 20),
                (10_000_000, 15),
                (25_000_000, 4),
                (50_000_000, 0.99),
                (100_000_000, 0.01),
            ],
            "key": "personal_account",
            "emoji": "💳"
        },
        2: {
            "name": "EXP CASE ⚡",
            "cost": 25,
            "prizes": [
                (10, 35),
                (25, 25),
                (50, 20),
                (100, 15),
                (250, 4),
                (500, 0.99),
                (1000, 0.01),
            ],
            "key": "exp",
            "emoji": "⚡"
        },
        3: {
            "name": "COIN ACTIVE CASE 🧿",
            "cost": 25,
            "prizes": [
                (5, 35),
                (10, 25),
                (20, 20),
                (30, 15),
                (40, 4),
                (50, 0.99),
                (100, 0.01),
            ],
            "key": "ball",
            "emoji": "🧿"
        },
        4: {
            "name": "BOOST CASE 💈",
            "cost": 50,
            "prizes": [
                (20, 35),
                (40, 25),
                (50, 20),
                (65, 15),
                (80, 4),
                (100, 0.99),
                (200, 0.01),
            ],
            "key": "osk",
            "emoji": "💈"
        }
    }

    if case_id not in cases:
        await update.message.reply_text("❌ Неверный номер кейса!")
        return

    case = cases[case_id]
    key = case["key"]
    cost = case["cost"]
    case_name = case["name"]
    emoji = case["emoji"]

    # Проверка количества бустов у пользователя
    boosts = int(user_info.get("osk", 0))
    if boosts < cost:
        await update.message.reply_text(f"❌ Для открытия кейса нужно {cost} 💈, а у вас только {boosts} 💈.")
        return

    # Рулетка по шансам
    pool = []
    for value, chance in case["prizes"]:
        pool += [value] * int(chance * 100)  # умножаем на 100 для большей точности

    prize = random.choice(pool)

    # Начисление приза
    config = load_accounts()
    sec = config[str(user_id)]
    sec["osk"] = str(boosts - cost)
    sec[key] = str(int(sec.get(key, 0)) + prize)
    save_accounts(config)

    # Сообщение пользователю
    await update.message.reply_text(
        f"🎉 Вы открыли <b>{case_name}</b> и получили <b>{prize} {emoji}</b>!",
        parse_mode="HTML"
    )

    # Оповещение всех для крупного приза
    rare_chances = [4, 0.99, 0.01]
    for i, (value, chance) in enumerate(case["prizes"]):
        if value == prize and chance in rare_chances:
            await notify_all_users(
                context,
                (
                    f"🔥 ВАУ-момент! <b>{nick}</b> стал счастливым обладателем редчайшего дропа!\n"
                    f"Из кейса <b>{case_name}</b> выпало <b>{prize} {emoji}</b>!\n"
                    f"👏 От всей команды — браво!"
                ),
                parse_mode="HTML"
            )
            break
        
def load_characteristic(ch_id):
    config = configparser.ConfigParser(interpolation=None)
    config.read(CHARACTERISTICS_FILE, encoding="utf-8")
    ch_id = str(int(str(ch_id).strip()))
    if ch_id in config.sections():
        data = config[ch_id]
        return {
            "name": data.get("name", ""),
            "required_boosts": int(data.get("required_boosts", 0)),
            "ball": int(data.get("ball", 0)),
            "exp": int(data.get("exp", 0)),
            "money": int(data.get("money", 0)),
            "exp_multiplier": float(data.get("exp_multiplier", 1.0)),
            "limit": int(data.get("limit", 0)),
            "limitiz": int(data.get("limitiz", 0)),
        }
    return None

def save_characteristic_limitiz(ch_id, new_limitiz):
    config = configparser.ConfigParser(interpolation=None)
    config.read(CHARACTERISTICS_FILE, encoding="utf-8")
    ch_id = str(int(str(ch_id).strip()))
    if ch_id in config.sections():
        config[ch_id]["limitiz"] = str(new_limitiz)
        with open(CHARACTERISTICS_FILE, "w", encoding="utf-8") as f:
            config.write(f)

async def buych(update, context):
    user_id = str(update.effective_user.id)
    user_info = get_user_info(user_id)

    # Проверка аргумента
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("❌ Неверный формат команды! Используйте: /buych <номер_характеристики>")
        return

    ch_id = str(int(context.args[0].strip()))
    ch_data = load_characteristic(ch_id)
    if not ch_data:
        config = configparser.ConfigParser()
        config.read(CHARACTERISTICS_FILE, encoding="utf-8")
        await update.message.reply_text(
            f"❌ Характеристика с таким номером не найдена!\n"
            f"Доступные ID: {', '.join(config.sections())}"
        )
        return

    # Проверка лимита характеристики
    limit = ch_data["limit"]
    limitiz = ch_data["limitiz"]
    if limit > 0 and limitiz >= limit:
        await update.message.reply_text(
            f"❌ Характеристика \"{ch_data['name']}\" закончилась!\n"
            f"Максимум покупок: {limit}."
        )
        return

    boosts = int(user_info.get("osk", 0))
    required_boosts = ch_data["required_boosts"]

    if boosts < required_boosts:
        await update.message.reply_text(
            f"❌ Недостаточно бустов!\n"
            f"Для покупки характеристики \"{ch_data['name']}\" нужно {required_boosts} 💈, а у вас только {boosts} 💈."
        )
        return

    # --- Обновление данных пользователя ---
    config_accounts = load_accounts()
    sec = config_accounts[user_id]
    sec["osk"] = str(boosts - required_boosts)
    sec["ball"] = str(int(sec.get("ball", 0)) + ch_data["ball"])
    sec["exp"] = str(int(sec.get("exp", 0)) + ch_data["exp"])
    sec["personal_account"] = str(int(sec.get("personal_account", 0)) + ch_data["money"])
    # Главное: меняем exp_multiplier
    sec["exp_multiplier"] = str(ch_data.get("exp_multiplier", 1.0))
    save_accounts(config_accounts)

    # --- Увеличение общего лимита в characteristics.ini ---
    new_limitiz = limitiz + 1
    save_characteristic_limitiz(ch_id, new_limitiz)

    await update.message.reply_text(
        f"✅️ Вы успешно купили характеристику: {ch_data['name']}!\n"
        f"💈 Списано бустов: {required_boosts} бустов\n"
        f"Осталось: {max(0, limit - new_limitiz) if limit > 0 else '∞'}"
    )

    # Уведомление админам > 2 уровня
    admin_ids = get_admins_ids(level_min=2)
    msg = (f"🅰 Покупка характеристики.\n"
           f"👤 Пользователь: {user_info.get('nick', user_id)}\n"
           f"💈 Списано бустов: {required_boosts}\n"
           f"Характеристика: {ch_data['name']} (ID: {ch_id})\n"
           f"Осталось: {max(0, limit - new_limitiz) if limit > 0 else '∞'}")
    for admin_id in admin_ids:
        if admin_id != int(user_id):
            try:
                await context.bot.send_message(admin_id, msg)
            except Exception:
                pass

async def buyboost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_info = get_user_info(user_id)

    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("❌ Неверный формат команды! Используйте: /buyboost <количество бустов>")
        return

    boost_count = int(context.args[0])
    if boost_count <= 0:
        await update.message.reply_text("❌ Количество бустов должно быть положительным числом.")
        return

    # Получаем актуальную цену покупки буста
    price_per_boost = context.bot_data.get('sell_price', 1_000_000)
    total_price = boost_count * price_per_boost

    personal_account = int(user_info.get('personal_account', 0))
    if personal_account < total_price:
        await update.message.reply_text(
            f"❌ Недостаточно средств на личном счете!\n"
            f"Требуется: {total_price} RUB\n"
            f"Ваш баланс: {personal_account} RUB"
        )
        return

    config_accounts = load_accounts()
    sec = config_accounts[user_id]
    sec["personal_account"] = str(personal_account - total_price)
    sec["osk"] = str(int(sec.get("osk", 0)) + boost_count)
    save_accounts(config_accounts)

    await update.message.reply_text(
        f"✅ Вы успешно купили {boost_count} буст(ов)!\n"
        f"💈 Ваш новый баланс бустов: {sec['osk']}\n"
        f"💳 Остаток на личном счете: {sec['personal_account']} RUB\n"
        f"📊 Цена за один буст (покупка): {price_per_boost} RUB"
    )

    admin_ids = get_admins_ids(level_min=2)
    msg = (f"🅰 Покупка бустов.\n"
           f"👤 Пользователь: {user_info.get('nick', user_id)}\n"
           f"💈 Куплено бустов: {boost_count}\n"
           f"💳 Списано: {total_price} RUB\n"
           f"Остаток: {sec['personal_account']} RUB")
    for admin_id in admin_ids:
        if admin_id != int(user_id):
            try:
                await context.bot.send_message(admin_id, msg)
            except Exception:
                pass

async def sellboost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_info = get_user_info(user_id)

    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("❌ Неверный формат команды! Используйте: /sellboost <количество бустов>")
        return

    boost_count = int(context.args[0])
    if boost_count <= 0:
        await update.message.reply_text("❌ Количество бустов должно быть положительным числом.")
        return

    current_boosts = int(user_info.get('osk', 0))
    if current_boosts < boost_count:
        await update.message.reply_text(
            f"❌ Недостаточно бустов для продажи!\n"
            f"У вас только {current_boosts} буст(ов)."
        )
        return

    # Получаем актуальную цену продажи буста
    price_per_boost = context.bot_data.get('buy_price', 250_000)
    receive_amount = boost_count * price_per_boost

    config_accounts = load_accounts()
    sec = config_accounts[user_id]
    sec["osk"] = str(current_boosts - boost_count)
    sec["personal_account"] = str(int(sec.get("personal_account", 0)) + receive_amount)
    save_accounts(config_accounts)

    await update.message.reply_text(
        f"✅ Вы успешно продали {boost_count} буст(ов)!\n"
        f"💈 Ваш новый баланс бустов: {sec['osk']}\n"
        f"💳 На ваш личный счёт зачислено: {receive_amount} RUB\n"
        f"📊 Цена за один буст (продажа): {price_per_boost} RUB"
    )

    admin_ids = get_admins_ids(level_min=2)
    msg = (f"🅰 Продажа бустов.\n"
           f"👤 Пользователь: {user_info.get('nick', user_id)}\n"
           f"💈 Продано бустов: {boost_count}\n"
           f"💳 Зачислено: {receive_amount} RUB\n"
           f"Остаток: {sec['personal_account']} RUB")
    for admin_id in admin_ids:
        if admin_id != int(user_id):
            try:
                await context.bot.send_message(admin_id, msg)
            except Exception:
                pass
            
# Ваши списки призов с шансами
money_prizes = [
    (100_000, 35),
    (500_000, 25),
    (1_000_000, 20),
    (10_000_000, 15),
    (25_000_000, 4),
    (50_000_000, 0.99),
    (100_000_000, 0.01)
]
exp_prizes = [
    (10, 35),
    (25, 25),
    (50, 20),
    (100, 15),
    (250, 4),
    (500, 0.99),
    (1000, 0.01)
]
coin_prizes = [
    (5, 35),
    (10, 25),
    (20, 20),
    (30, 15),
    (40, 4),
    (50, 0.99),
    (100, 0.01)
]
boost_prizes = [
    (10, 35),
    (20, 25),
    (25, 20),
    (30, 15),
    (40, 4),
    (50, 0.99),
    (100, 0.01)
]

rare_chances = [4, 0.99, 0.01]

def weighted_random(prizes):
    total = sum(weight for _, weight in prizes)
    r = random.uniform(0, total)
    upto = 0
    for value, weight in prizes:
        if upto + weight >= r:
            return value, weight
        upto += weight
    return prizes[-1]  # (value, weight)

async def lcase(update, context):
    user_id = str(update.effective_user.id)
    user_info = get_user_info(user_id)
    if not user_info:
        await update.message.reply_text("Ошибка: информация о вашем аккаунте не найдена.")
        return

    boosts = int(user_info.get("osk", 0))
    if boosts < 111:
        await update.message.reply_text("❌ Недостаточно бустов для открытия LEGENDARY CASE (нужно 111 💈).")
        return

    # Получаем награды и их шансы
    money, money_chance = weighted_random(money_prizes)
    exp, exp_chance = weighted_random(exp_prizes)
    activity, activity_chance = weighted_random(coin_prizes)
    boosts_reward, boosts_chance = weighted_random(boost_prizes)

    config = load_accounts()
    sec = config[user_id]
    sec["osk"] = str(boosts - 111 + boosts_reward)
    sec["personal_account"] = str(int(sec.get("personal_account", 0)) + money)
    sec["exp"] = str(int(sec.get("exp", 0)) + exp)
    sec["ball"] = str(int(sec.get("ball", 0)) + activity)
    save_accounts(config)

    nick = user_info.get('nick', user_id)
    case_name = "LEGENDARY CASE"

    # Сообщение пользователю о призах
    await update.message.reply_text(
        f"🎉 Вы открыли <b>{case_name}</b>!\n\n"
        f"Вам выпало:\n"
        f"💳 {money} RUB\n"
        f"💈 {boosts_reward} бустов\n"
        f"⚡ {exp} опыта\n"
        f"🧿 {activity} монет активности\n",
        parse_mode="HTML"
    )

    # Проверяем, есть ли хотя бы 1 редкий шанс
    rare_won = any(
        chance in rare_chances for chance in [money_chance, exp_chance, activity_chance, boosts_chance]
    )

    if rare_won:
        drop_message = (
            f"🧈 ЛЕГЕНДАРНЫЙ-момент! <b>{nick}</b> стал обладателем редчайшего дропа из легендарного кейса!\n"
            f"Из кейса <b>{case_name}</b> выпало:\n"
            f"💳 {money} RUB\n"
            f"💈 {boosts_reward} бустов\n"
            f"⚡ {exp} опыта\n"
            f"🧿 {activity} монет активности\n"
            f"👏 От всей команды — браво!"
        )
        # Сообщение всем пользователям
        all_users_config = load_accounts()
        for section in all_users_config.sections():
            if section.isdigit():
                try:
                    await context.bot.send_message(
                        chat_id=int(section),
                        text=drop_message,
                        parse_mode="HTML"
                    )
                except Exception:
                    pass

async def lvlconf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_info = get_user_info(user_id)
    current_level = int(user_info.get('level', 0)) if user_info else 0
    lvlconf_val = int(user_info.get('lvlconf', 0)) if user_info else 0
    boosts = int(user_info.get('osk', 0)) if user_info else 0

    confirm_costs = {10: 50, 11: 50, 12: 50, 13: 50, 14: 50, 15: 50, 16: 50, 17: 50, 18: 50, 19: 50, 20: 100, 21: 100, 22: 100, 23: 100, 24: 100, 25: 100, 26: 100, 27: 100, 28: 100, 29: 100, 30: 150, 31: 150, 32: 150, 33: 150, 34: 150, 35: 150, 36: 150, 37: 150, 38: 150, 39: 150, 40: 200, 41: 200, 42: 200, 43: 200, 44: 200, 45: 200, 46: 200, 47: 200, 48: 200, 49: 200, 50: 250, 51: 250, 52: 250, 53: 250, 54: 250, 55: 250, 56: 250, 57: 250, 58: 250, 59: 250, 60: 300, 61: 300, 62: 300, 63: 300, 64: 300, 65: 300, 66: 300, 67: 300, 68: 300, 69: 300, 70: 350, 71: 350, 72: 350, 73: 350, 74: 350, 75: 350, 76: 350, 77: 350, 78: 350, 79: 350, 80: 400, 81: 400, 82: 400, 83: 400, 84: 400, 85: 400, 86: 400, 87: 400, 88: 400, 89: 400, 90: 450, 91: 450, 92: 450, 93: 450, 94: 450, 95: 450, 96: 450, 97: 450, 98: 450, 99: 450, 100: 500}

    if lvlconf_val == 0 or current_level not in confirm_costs:
        await update.message.reply_text("✅ Подтверждение уровня не требуется или уровень не требует подтверждения.")
        return

    cost = confirm_costs[current_level]
    if boosts < cost:
        await update.message.reply_text(f"❌ Недостаточно бустов для подтверждения уровня! Требуется: {cost} 💈, у вас: {boosts} 💈")
        return

    config = load_accounts()
    sec = config[user_id]
    sec['osk'] = str(boosts - cost)
    sec['lvlconf'] = '0'  # подтверждение выполнено
    save_accounts(config)

    await update.message.reply_text(
        f"✅ Ваш {current_level} уровень успешно подтверждён!\n"
        f"💈 Списано: {cost} бустов.\n"
        f"Теперь вы можете подавать отчёты и пользоваться всеми функциями."
    )

# === Команда /aactive ===
async def aactive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)

    # Проверка уровня админа
    if not user_info or int(user_info.get("is_admin", "0")) <= 1:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return

    keyboard = [
        [InlineKeyboardButton("👑 Лидер семьи", callback_data="pos_Лидер семьи")],
        [InlineKeyboardButton("⭐ Старший заместитель", callback_data="pos_Старший заместитель")],
        [InlineKeyboardButton("🛡 Заместитель", callback_data="pos_Заместитель")],
        [InlineKeyboardButton("💎 XVIP", callback_data="pos_XVIP")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🅰 Глобальная активность за неделю. Выберите должность:", reply_markup=reply_markup)

# === Обработка нажатия кнопки ===
async def aactive_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    position = query.data.replace("pos_", "")  # Должность из callback_data

    config = load_accounts()
    players = []

    # Эмодзи для уровня
    level_emojis = [
        (range(0, 10), "🧸"),
        (range(10, 20), "🎓"),
        (range(20, 30), "🦾"),
        (range(30, 40), "🕶️"),
        (range(40, 50), "🍹"),
        (range(50, 60), "🚬"),
        (range(60, 70), "💼"),
        (range(70, 80), "⭐"),
        (range(80, 90), "🌟"),
        (range(90, 100), "💎"),
        (range(100, 101), "👑")
    ]

    def get_level_emoji(level):
        for level_range, emoji in level_emojis:
            if level in level_range:
                return emoji
        return "❔"

    def get_activity_level(ball: int) -> str:
        if ball >= 625:
            return "🟣 Превосходная"
        elif 500 <= ball < 625:
            return "🟡 Максимальная"
        elif 375 <= ball < 500:
            return "🟢 Средняя"
        elif 250 <= ball < 375:
            return "🔴 Минимальная"
        else:
            return "⚪ Недостаточная"

    # Собираем игроков выбранной должности
    for section in config.sections():
        if section.isdigit():
            user_id = int(section)
            user_info = get_user_info(user_id)
            if user_info and user_info.get("position") == position:
                players.append(user_info)

    # Сортируем по баллам
    players_sorted = sorted(players, key=lambda x: x["ball"], reverse=True)[:10]

    if not players_sorted:
        await query.edit_message_text(f"❌ Нет пользователей с должностью: {position}")
        return

    # Формируем сообщение
    message = f"📋 Активность ({position})\n\n"
    for player in players_sorted:
        nick = player.get("nick", "Неизвестный")
        level = player.get("level", 0)
        ball = player.get("ball", 0)
        lvl_emoji = get_level_emoji(level)
        act_level = get_activity_level(ball)

        message += (
            f"👤 {nick} {lvl_emoji}\n"
            f"📈 {act_level}\n"
            f"🧿 Монеты: {ball}\n\n"
        )

    await query.edit_message_text(message, parse_mode="HTML")
#########################################################
#РЕЖИМ ТЕХ. РАБОТ#
#########################################################

def set_maintenance_mode(enabled: bool):
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE)

    if "settings" not in config:
        config["settings"] = {}

    config["settings"]["maintenance"] = "1" if enabled else "0"

    with open(SETTINGS_FILE, "w") as f:
        config.write(f)

def is_maintenance_mode() -> bool:
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE)
    return config.get("settings", "maintenance", fallback="0") == "1"

async def check_access(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)

    # Если включены техработы
    if is_maintenance_mode():
        # Проверка: если админ 3 уровня — доступ открыт, но с уведомлением
        if user_info and int(user_info.get("is_admin", 0)) == 3:
            if update.message:
                await update.message.reply_text("⚙️ Внимание: сейчас включён режим технических работ.\nВы имеете доступ как администратор 3 уровня.")
            elif update.callback_query:
                await update.callback_query.message.reply_text("⚙️ Внимание: сейчас включён режим технических работ.\nВы имеете доступ как администратор 3 уровня.")
            return True
        else:
            # Остальные получают отказ + фото
            if update.message:
                try:
                    with open("techrab.png", "rb") as photo:
                        await update.message.reply_photo(photo=photo, caption="⚠️ Бот временно недоступен. Идут технические работы.")
                except FileNotFoundError:
                    await update.message.reply_text("⚠️ Бот временно недоступен. Идут технические работы.")
            elif update.callback_query:
                try:
                    with open("techrab.png", "rb") as photo:
                        await update.callback_query.message.reply_photo(photo=photo, caption="⚠️ Бот временно недоступен. Идут технические работы.")
                except FileNotFoundError:
                    await update.callback_query.message.reply_text("⚠️ Бот временно недоступен. Идут технические работы.")
            return False
    return True

async def send_technical_start_to_all_users(context: ContextTypes.DEFAULT_TYPE):
    config = load_accounts()
    keyboard = get_login_keyboard()
    message = "⚠️ Включен режим технических работ.\n\nℹ️ Доступ закрыт для всех.\n\nПосле завершения работ потребуется повторная авторизация."

    for user_id in config.sections():
        if user_id.isdigit():
            try:
                with open("techrab.png", "rb") as photo:
                    await context.bot.send_photo(
                        chat_id=int(user_id),
                        photo=photo,
                        caption=message,
                        reply_markup=keyboard
                    )
            except Exception as e:
                logging.error(f"Ошибка при отправке фото пользователю {user_id}: {e}")


async def send_technical_end_to_all_users(context: ContextTypes.DEFAULT_TYPE):
    config = load_accounts()
    keyboard = get_login_keyboard()
    message = "✅ Технические работы завершены.\n\nℹ️ Система снова доступна. Для продолжения пройдите авторизацию."

    for user_id in config.sections():
        if user_id.isdigit():
            try:
                with open("techrab.png", "rb") as photo:
                    await context.bot.send_photo(
                        chat_id=int(user_id),
                        photo=photo,
                        caption=message,
                        reply_markup=keyboard
                    )
            except Exception as e:
                logging.error(f"Ошибка при отправке фото пользователю {user_id}: {e}")


async def toggle_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)

    if int(user_info.get("is_admin", 0)) < 3:
        await query.answer("⛔ Недостаточно прав.")
        return

    if is_maintenance_mode():
        # Выключаем тех. работы
        set_maintenance_mode(False)
        await query.message.reply_text("✅ Технические работы завершены. Бот снова доступен.")
        # Отправляем уведомление всем пользователям
        await send_technical_end_to_all_users(context)
    else:
        # Включаем тех. работы
        set_maintenance_mode(True)
        await query.message.reply_text("⚠️ Включен режим технических работ.")
        # Отправляем уведомление всем пользователям
        await send_technical_start_to_all_users(context)

        

# Функция main – настройка и запуск бота
async def main():
    application = Application.builder().token(TOKEN).build()
    asyncio.create_task(price_updater(application))
    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("gift", gift))
    application.add_handler(CommandHandler("send", send))
    application.add_handler(CommandHandler("setpromocode", setpromocode))
    application.add_handler(CommandHandler("resetpromocode", resetpromocode))
    application.add_handler(CommandHandler("buyn", buyn))
    application.add_handler(CommandHandler("buych", buych))
    application.add_handler(CommandHandler("buyboost", buyboost))
    application.add_handler(CommandHandler("sellboost", sellboost))
    application.add_handler(CommandHandler("case", case_open))
    application.add_handler(CommandHandler("lcase", lcase))
    application.add_handler(CommandHandler("lvlconf", lvlconf))
    application.add_handler(conv_reg)
    # Обработчики регистрации
    application.add_handler(CallbackQueryHandler(admin, pattern="^admin$"))
    application.add_handler(CallbackQueryHandler(view_registrations, pattern="^view_registrations$"))
    application.add_handler(CallbackQueryHandler(reg_detail, pattern="^reg_detail_.*$"))
    application.add_handler(CallbackQueryHandler(reg_approve, pattern=r"^reg_approve_[a-zA-Z0-9]+$"))
    application.add_handler(CallbackQueryHandler(reg_reject, pattern="^reg_reject_.*"))
    application.add_handler(CallbackQueryHandler(delete_user_account, pattern="^delete_user_account_.*$"))
    application.add_handler(CommandHandler("aactive", aactive))
    application.add_handler(CallbackQueryHandler(aactive_callback, pattern="^pos_"))
    # Обработчики колбэков (заявки на вывод)
    application.add_handler(CallbackQueryHandler(handle_withdrawal_selection, pattern=r'^withdraw_\d+$'))
    application.add_handler(CallbackQueryHandler(confirm_withdraw_request, pattern=r"^confirm_withdraw$"))
    application.add_handler(CallbackQueryHandler(cancel_withdraw_request, pattern=r"^cancel_withdraw$"))
    application.add_handler(CallbackQueryHandler(view_withdrawal, pattern=r"^view_[a-zA-Z0-9]{8}$"))
    application.add_handler(CallbackQueryHandler(approve_withdrawal, pattern=r"^approve_[a-zA-Z0-9]{8}$"))
    application.add_handler(CallbackQueryHandler(reject_withdrawal, pattern=r"^reject_[a-zA-Z0-9]{8}$"))
    application.add_handler(CallbackQueryHandler(admin_withdrawals, pattern=r"^admin_withdrawals$"))
    # Обработчики колбэков (рассылки и др. функции администратора)
    application.add_handler(CallbackQueryHandler(manage_users, pattern="^show_users_|^back_to_positions|^edit_user_|^admin$"))
    application.add_handler(CallbackQueryHandler(mass_message, pattern='^mass_message$'))
    application.add_handler(CallbackQueryHandler(cancel_mass_message, pattern='^cancel_mass_message$'))
    application.add_handler(CallbackQueryHandler(single_message, pattern="^start_single_message$"))
    application.add_handler(CallbackQueryHandler(send_single_message, pattern="^single_user_"))
    application.add_handler(CallbackQueryHandler(cancel_single_message, pattern="^cancel_single_message$"))
    #NEW
    application.add_handler(CallbackQueryHandler(manage_users, pattern="^manage_users$"))
    application.add_handler(CallbackQueryHandler(change_nick, pattern="^change_nick_.*$"))
    application.add_handler(CallbackQueryHandler(add_warning, pattern="^add_warning_.*$"))
    application.add_handler(CallbackQueryHandler(remove_warning, pattern="^remove_warning_.*$"))
    application.add_handler(CallbackQueryHandler(change_ball, pattern="^change_ball_.*$"))
    application.add_handler(CallbackQueryHandler(add_ball, pattern="^add_ball$"))
    application.add_handler(CallbackQueryHandler(remove_ball, pattern="^remove_ball$"))
    application.add_handler(CallbackQueryHandler(change_personal_account, pattern="^change_personal_account_.*$"))
    application.add_handler(CallbackQueryHandler(add_account, pattern="^add_account$"))
    application.add_handler(CallbackQueryHandler(remove_account, pattern="^remove_account$"))
    application.add_handler(CallbackQueryHandler(set_position, pattern="^set_position_"))
    application.add_handler(CallbackQueryHandler(change_position, pattern="^change_position_"))
    application.add_handler(CallbackQueryHandler(set_position, pattern="^set_position_"))
    application.add_handler(CallbackQueryHandler(close_week_handler, pattern="^week_close"))
    application.add_handler(CallbackQueryHandler(close_week_handler, pattern="^week_close_(yes|no)$"))
    application.add_handler(CallbackQueryHandler(set_admin_rights_prompt, pattern="^set_admin_rights_.*$"))
    application.add_handler(CallbackQueryHandler(choose_admin_level, pattern="^set_admin_[0-3]$"))
    application.add_handler(CallbackQueryHandler(back_to_admin, pattern="^back_to_admin$"))
    application.add_handler(CallbackQueryHandler(exit_admin_panel, pattern="^exit_admin_panel$"))
    application.add_handler(CallbackQueryHandler(exit_admin_panel, pattern="^send_conversion_reminder$"))
    application.add_handler(CallbackQueryHandler(force_technical_exit, pattern="^force_technical_exit$")) #кнопка
    application.add_handler(CallbackQueryHandler(toggle_maintenance, pattern="^toggle_maintenance$")) #тех.работы
    application.add_handler(CallbackQueryHandler(change_rd, pattern="^change_rd$"))
    application.add_handler(CallbackQueryHandler(cancel_change_rd, pattern='^cancel_change_rd$'))
    application.add_handler(CallbackQueryHandler(handle_back_to_user_edit, pattern="^cancel_change_nick$"))
    # Обработчики системы отчетов
    application.add_handler(CallbackQueryHandler(admin_reports, pattern="^reports$"))
    application.add_handler(CallbackQueryHandler(view_report, pattern="^viewReport_"))
    application.add_handler(CallbackQueryHandler(approve_report, pattern="^approveReport_"))
    application.add_handler(CallbackQueryHandler(reject_report, pattern="^rejectReport_"))
    # история отчётов
    # Обработчик для истории отчетов
    application.add_handler(CallbackQueryHandler(report_history, pattern=r"^report_history_.*"))
    application.add_handler(CallbackQueryHandler(view_full_report, pattern=r"^viewreport_.*"))
    # Обработчики нажатия кнопок
    application.add_handler(CallbackQueryHandler(manage_users, pattern="^manage_users$"))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("Авторизация"), button_handler))
    # Новые обработчики
    application.add_handler(CallbackQueryHandler(manage_users, pattern="^manage_users$"))
    # Обработчики во время создания отчета
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CommandHandler("done", finish_report))
    application.add_handler(CommandHandler("cancel", cancel_report))
    application.add_handler(CommandHandler("rating", rating))
    # Добавление нового обработчика для кнопки "Статистика"
    application.add_handler(CallbackQueryHandler(statistics, pattern="^statistics_.*"))

    # Обработчик любых текстовых сообщений (должен идти последним)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    # Вызов функции обновления значений баллов
    logging.info("Бот успешно запущен!")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен вручную")
