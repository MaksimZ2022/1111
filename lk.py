import operator
import nest_asyncio
nest_asyncio.apply()
#🔵
import asyncio
import logging
import configparser
import os
import re
import shutil
import string
import random
import time
import httpx
import locale  # Импорт библиотеки locale
import configparser
import pytz
import uuid
import unicodedata
import math
from babel.numbers import format_decimal as format_number
from telegram.error import BadRequest
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from io import BytesIO
from typing import Dict, List, Tuple

# Removed requests, csv, StringIO imports
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, InputFile 
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler, CallbackContext
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# Токен бота (замените на актуальный перед запуском)
TOKEN = '8108534662:AAGITJNoOW2VQotLETnJAuJjVoOkpX2VzHA'  # ПЕРЕД запуском бота ОБНОВИТЬ токен

#ОСНОВНОЙ - 7738679454:AAFiCDandc9VFfE01D4LcYJo-Pd6aKXcATc
#ТЕСТОВЫЙ - 8108534662:AAGITJNoOW2VQotLETnJAuJjVoOkpX2VzHA

# Файл .ini для хранения всех данных бота

ACCOUNTS_FILE = "accounts.ini"
REPORTS_FILE = "reports.ini"
SIDE_FILE = "user_sides.ini"
WITHDRAWALS_FILE = "withdrawals.ini"
REGISTRATIONS_FILE = "registrations.ini"
SETTINGS_FILE = "settings.ini"
PROMO_FILE = "promo.ini"
PROMO_ACTIVATIONS_FILE = "promo_activations.ini"
REG_NAME, REG_REALNAME, REG_BIRTHDATE, REG_POSITION_MANUAL = range(4)
CHARACTERISTICS_FILE = "characteristics.ini"
PRICE_MIN = 500_000
PRICE_MAX = 550_000
DEPOSITS_FILE = "deposits.ini"
USER_CHARS_FILE = "user_characteristics.ini"
REWARDS_HISTORY_FILE = "rewards_history.ini"
RD_BONUS_FILE = "rd_bonus.ini"
EVO_COSTS = [250, 500, 1000]
EVO_MAX_LEVEL = 3
EVO_EXP_MULTIPLIERS = [1.25, 1.5, 2.0]
EVO_REPORT_COINS = [1000, 2000, 3000]  # За отчет после прохождения эволюции
EVO_REQUIRED_LEVELS = [50, 75, 100]
HISTORY_RESPECT_FILE = 'historyrespect.ini'
# --- Новые константы и вспомогательные функции для мастерской и суперприза ---
# Система суперприза — исправлённая версия по вашему ТЗ:
WORKSHOP_COST = 50
SUPERPRIZE_SECTION = "superprize"
SUPERPRIZE_INITIAL = 3000     # стартовая сумма суперприза (в снежинках), всегда начинается с 3000
SUPERPRIZE_CONTRIB_RATE = 0.10    # доля от стоимости открытия, которая идет в копилку
# Названия файлов (можно менять, но должны совпадать с теми, что используются в lk.py)
HAPPY_FILE = "happy.ini"
HAPPY_SECTION = "claimed"
LIMITS_FILE = "limitsvivod.ini"
ACCOUNTS_FILE = "accounts.ini"
SC_NAME, SC_DESC, SC_CHANCE, SC_COSTS, SC_EFFECTS, SC_UNIQUE, SC_CONFIRM = range(200, 207)
# Константы состояний для ConversationHandler при добавлении задания
(
    AT_TITLE,
    AT_COINS,
    AT_SNOW,
    AT_EXP,
    AT_DESC,
    AT_REPEAT,
    AT_CONFIRM
) = range(7)

TASKS_FILE = "tasks.ini"
USER_TASKS_FILE = "user_tasks.ini"
# === Конфигурация файлов ===
MOD_CDS_FILE = "module_cooldowns.ini"  # Для кулдаунов

# === Имена модулей ===
MOD_ELF_PROTECTION = "modelfzachita"  # Эльфийский оберег
MOD_LESHEY_TATIB = "tatibaleshego"   # Проделки Лешего
MOD_SNEGURKA_SHOP = "prilavoksnegurka"  # Снегурочка
MOD_BABA_YAGA_SHOP = "izbayagi"  # Баба Яга
MOD_MOROZ_BOX = "sdedmoroz"  # Шкатулка Деда Мороза
MOD_SKOSHEY_BOX = "skosheybesmerniy"  # Шкатулка Кощея
MOD_LEADER_SHOP = "prilavoklider"

# === Кулдауны (в секундах) ===
COOLDOWN_ELF_PROTECTION = 48 * 60 * 60
COOLDOWN_LESHEY_TATIB = 12 * 60 * 60
COOLDOWN_SNEGURKA_SHOP = 5 * 60
COOLDOWN_LEADER_SHOP = 5 * 60
COOLDOWN_BABA_YAGA_SHOP = 5 * 60
SDED_MOROZ_COOLDOWN = 72 * 60 * 60
SDED_MOROZ_COOLDOWN = 72 * 60 * 60  # 72 часа

# Настройки / константы (при необходимости измените)
ACCOUNTS_FILE = "accounts.ini"
SIDE_FILE = "user_sides.ini"
LIMITED_SETS_FILE = "limited_sets.ini"
LIMITED_SET_TOTAL = 50
# Дата и время релиза (MSK = UTC+3)
LIMITED_SETS_RELEASE_MSK = datetime(2025, 12, 21, 18, 0, tzinfo=timezone(timedelta(hours=3)))
# Поле бустов в accounts.ini
BOOST_FIELD = "osk"  # вы указали osk

# Ресурсы внутри набора (ключи в accounts.ini)
RESOURCE_LOSK = "losk"         # 📒 -> 25
RESOURCE_UOSK = "uosk"         # 📕 -> 50
RESOURCE_EV_STONES = "ev_stones"  # 🔥 -> 50
RESOURCE_T = "t"               # ❄️ -> 250

# Бонусные выпадения (ключ, шанс в %)
# Темный набор
DARK_BONUS_KEYS: List[Tuple[str, float]] = [
    ("skosheybesmerniy", 1.0),   # 1%
    ("izbayagi", 5.0),           # 5%
    ("tatibaleshego", 10.0),     # 10%
]
# Светлый набор
LIGHT_BONUS_KEYS: List[Tuple[str, float]] = [
    ("sdedmoroz", 1.0),          # 1%
    ("prilavoksnegurka", 5.0),   # 5%
    ("modelfzachita", 10.0),     # 10%
]

# Стоимость набора в бустах
SET_COST = 50

# -------------------------------------------------------------------------------
# Утилиты по работе с ini-файлами (accounts / sides / limited_sets)
# -------------------------------------------------------------------------------

MODULE_PRETTY_NAMES = {
    "izbayagi": "🧟‍ Торговая изба «Бабы Яги»",
    "tatibaleshego": "🧌 Модуль «Проделки Лешего»",
    "skosheybesmerniy": "🧛️ Шкатулка «Кощея Бессмертного»",
    "sdedmoroz": "🎅 Шкатулка «Деда Мороза»",
    "prilavoksnegurka": "🤶 Лавка Снегурочки",
    "modelfzachita": "🧝️ Модуль «Эльфийский оберег»",
    # при необходимости добавьте другие ключи, которые могут выпадать
}

def module_pretty_name(key: str) -> str:
    """
    Возвращает человекочитаемое имя для ключа модуля/предмета.
    Если ключ неизвестен — возвращает ключ в виде кода.
    """
    if not key:
        return ""
    return MODULE_PRETTY_NAMES.get(key, f"{key}")

def _ensure_file_exists(path: str, default_text: str = ""):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(default_text)


# --- accounts.ini ---
def load_accounts_cfg() -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    _ensure_file_exists(ACCOUNTS_FILE)
    try:
        cfg.read(ACCOUNTS_FILE, encoding="utf-8")
    except Exception:
        cfg = configparser.ConfigParser()
    return cfg


def save_accounts_cfg(cfg: configparser.ConfigParser):
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)


def _ensure_user_section_accounts(cfg: configparser.ConfigParser, uid_str: str):
    if uid_str not in cfg:
        cfg[uid_str] = {}


def _get_account_number(cfg_accounts: configparser.ConfigParser, uid: str, key: str) -> int:
    try:
        _ensure_user_section_accounts(cfg_accounts, uid)
        return int(float(cfg_accounts[uid].get(key, "0")))
    except Exception:
        return 0


def _add_to_account_field(cfg_accounts: configparser.ConfigParser, uid: str, key: str, amount: int):
    _ensure_user_section_accounts(cfg_accounts, uid)
    cur = _get_account_number(cfg_accounts, uid, key)
    cfg_accounts[uid][key] = str(int(cur) + int(amount))


# --- user_sides.ini ---
def load_user_sides() -> Dict[str, str]:
    """
    Читает user_sides.ini и возвращает {user_id_str: 'light'|'dark'}
    """
    cfg = configparser.ConfigParser()
    _ensure_file_exists(SIDE_FILE)
    try:
        cfg.read(SIDE_FILE, encoding="utf-8")
    except Exception:
        return {}
    res: Dict[str, str] = {}
    for sec in cfg.sections():
        try:
            val = cfg[sec].get("side", "").strip().lower()
            if not val:
                continue
            # распознаем русские и английские варианты
            if "свет" in val or "svet" in val or "light" in val:
                res[str(sec)] = "light"
            elif "темн" in val or "temn" in val or "dark" in val:
                res[str(sec)] = "dark"
            else:
                # если есть прочитанное значение — сохраним как есть
                res[str(sec)] = val
        except Exception:
            continue
    return res


def save_user_side(user_id: int, side: str):
    """
    Сохраняет сторону пользователя в user_sides.ini в нормализованном виде 'light'/'dark'
    """
    uid = str(user_id)
    val = (side or "").strip().lower()
    if "свет" in val or "svet" in val or "light" in val:
        val_norm = "light"
    elif "темн" in val or "temn" in val or "dark" in val:
        val_norm = "dark"
    else:
        val_norm = val or ""

    cfg = configparser.ConfigParser()
    if os.path.exists(SIDE_FILE):
        try:
            cfg.read(SIDE_FILE, encoding="utf-8")
        except Exception:
            cfg = configparser.ConfigParser()

    if uid not in cfg:
        cfg[uid] = {}
    cfg[uid]["side"] = val_norm
    with open(SIDE_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)

# -------------------------------------------------------------------------------
# Помощник: получить список админов уровня >= min_level
# Если в проекте есть своя функция get_admins_ids, можно заменить вызов.
# Здесь — попытка получить из accounts.ini поля admin_level (если есть).
# Формат: в секции пользователя accounts.ini ключ admin_level = 2
# -------------------------------------------------------------------------------
def _get_admins_ids_from_accounts(min_level: int = 2) -> List[int]:
    cfg = load_accounts_cfg()
    res: List[int] = []
    for sec in cfg.sections():
        try:
            lvl = cfg[sec].get("admin_level", None)
            if lvl is None:
                # возможно поле называется "level" или "rights" — можно добавить доп. проверки
                lvl = cfg[sec].get("level", cfg[sec].get("rights", None))
            if lvl is None:
                continue
            if _int_safe(lvl, 0) >= min_level:
                try:
                    res.append(int(sec))
                except Exception:
                    continue
        except Exception:
            continue
    return res

def get_user_side_normalized(user_id: int) -> str:
    sides = load_user_sides()
    sid = str(user_id)
    return sides.get(sid, "")

# --- limited_sets.ini ---
def load_limited_sets_cfg() -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    if not os.path.exists(LIMITED_SETS_FILE):
        # инициализация по умолчанию
        cfg["light"] = {"total": str(LIMITED_SET_TOTAL), "sold": "0"}
        cfg["dark"] = {"total": str(LIMITED_SET_TOTAL), "sold": "0"}
        with open(LIMITED_SETS_FILE, "w", encoding="utf-8") as f:
            cfg.write(f)
        return cfg
    try:
        cfg.read(LIMITED_SETS_FILE, encoding="utf-8")
    except Exception:
        cfg = configparser.ConfigParser()
    # гарантируем секции
    changed = False
    for s in ("light", "dark"):
        if s not in cfg:
            cfg[s] = {"total": str(LIMITED_SET_TOTAL), "sold": "0"}
            changed = True
    if changed:
        with open(LIMITED_SETS_FILE, "w", encoding="utf-8") as f:
            cfg.write(f)
    return cfg


def save_limited_sets_cfg(cfg: configparser.ConfigParser):
    with open(LIMITED_SETS_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)
        
def load_sides():
    config = configparser.ConfigParser()
    config.read(SIDE_FILE)
    return config

def save_side(user_id, side):
    config = load_sides()
    if not config.has_section(user_id):
        config.add_section(user_id)
    config[user_id]["side"] = side
    with open(SIDE_FILE, "w") as f:
        config.write(f)
        
def save_config(config: configparser.ConfigParser, file_path: str):
    with open(file_path, "w") as file:
        config.write(file)

def get_cooldown_end(user_id: str, module: str) -> datetime:
    """Возвращает время окончания кулдауна модуля."""
    config = load_config(MOD_CDS_FILE)
    if user_id in config and module in config[user_id]:
        return datetime.fromisoformat(config[user_id][module])
    return datetime.min

def set_cooldown(user_id: str, module: str, duration: int):
    """Устанавливает кулдаун для модуля."""
    config = load_config(MOD_CDS_FILE)
    if user_id not in config:
        config[user_id] = {}
    cooldown_end = datetime.now() + timedelta(seconds=duration)
    config[user_id][module] = cooldown_end.isoformat()
    save_config(config, MOD_CDS_FILE)

def is_module_available(user_id: str, module: str) -> bool:
    """Проверяет доступность модуля."""
    return datetime.now() >= get_cooldown_end(user_id, module)

def add_exp(user_id: str, amount: int):
    """Добавляет `exp` пользователю."""
    config = load_config(ACCOUNTS_FILE)
    if user_id not in config:
        config[user_id] = {}
    current_exp = int(config[user_id].get("exp", 0))
    config[user_id]["exp"] = str(current_exp + amount)
    save_config(config, ACCOUNTS_FILE)

# Человекочитаемые названия ресурсов (используются в сообщениях)
RESOURCE_NAMES = {
    "exp": "⚡ EXP",
    "ev_stones": "🔥 Респекты",
    "ball": "🧿 Монеты активности",
    "evball": "🪙 Монеты эволюции",
    "osk": "💈 Бусты",
    "t": "❄ Снежинки",
    "personal_account": "💳 RUB на личном счёте",
    "oosk": "📘 O‑осколки",
    "uosk": "📕 U‑осколки",
    "losk": "📒 L‑осколки"
}
        
def resource_pretty(key: str, amount: int) -> str:
    """Вернуть человекочитаемое представление ресурса с форматированием числа."""
    name = RESOURCE_NAMES.get(key, key)
    try:
        return f"{name}: {fmt(amount)}"
    except Exception:
        return f"{name}: {amount}"
    
CRAFT_FILE = "craft_items.ini"
# если в вашем файле нет глобальной переменной для cooldown — добавьте её
if '_last_craft_call' not in globals():
    _last_craft_call = {}
CRAFT_COOLDOWN = 1.0  # секунда между попытками одного пользователя

def _ensure_craft_file():
    if not os.path.exists(CRAFT_FILE):
        open(CRAFT_FILE, "a", encoding="utf-8").close()

def load_craft_items():
    """Возвращает configparser с рецептами (секции: '1','2',... )"""
    _ensure_craft_file()
    # Отключаем интерполяцию, чтобы '%' в описаниях не ломали запись/чтение
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read(CRAFT_FILE, encoding="utf-8")
    return cfg

def save_craft_items(cfg):
    with open(CRAFT_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)

def _parse_int(v):
    try:
        return int(v or 0)
    except Exception:
        return 0

def _parse_recipe_section(cfg, sec):
    """
    Возвращает dict:
      {
        'id': sec,
        'name': ...,
        'desc': ...,
        'chance': int (0..100),
        'costs': { field_name: int, ... },
        'effects': [effect_str, ...],
        'unique': True/False
      }
    Ожидаемые поля в секции:
      name, desc, chance,
      cost_exp, cost_ev_stones, cost_ball, cost_evball, cost_osk, cost_t,
      cost_personal_account, cost_oosk, cost_uosk, cost_losk
      effects = ;-separated list e.g. add_char:craft_1=1;inc_field:osk=50;set_field:ev_level=1
      unique = yes/no
    """
    data = cfg[sec]
    name = data.get("name", f"item_{sec}")
    desc = data.get("desc", "")
    chance = _parse_int(data.get("chance", "0"))
    costs = {
        "exp": _parse_int(data.get("cost_exp", "0")),
        "ev_stones": _parse_int(data.get("cost_ev_stones", "0")),
        "ball": _parse_int(data.get("cost_ball", "0")),
        "evball": _parse_int(data.get("cost_evball", "0")),
        "osk": _parse_int(data.get("cost_osk", "0")),
        "t": _parse_int(data.get("cost_t", "0")),
        "personal_account": _parse_int(data.get("cost_personal_account", "0")),
        "oosk": _parse_int(data.get("cost_oosk", "0")),
        "uosk": _parse_int(data.get("cost_uosk", "0")),
        "losk": _parse_int(data.get("cost_losk", "0")),
    }
    effects_raw = data.get("effects", "")
    effects = [e.strip() for e in effects_raw.split(";") if e.strip()]
    unique = data.get("unique", "no").strip().lower() in ("yes", "y", "true", "1")
    return {
        "id": sec,
        "name": name,
        "desc": desc,
        "chance": max(0, min(100, chance)),
        "costs": costs,
        "effects": effects,
        "unique": unique
    }

def _get_account_numeric(cfg_accounts, uid, key):
    # безопасно получать числовое поле (если нет — 0)
    try:
        return int(cfg_accounts[uid].get(key, "0") or 0)
    except Exception:
        return 0

def can_afford(cfg_accounts, uid, costs):
    """
    Проверяет, хватает ли у пользователя ресурсов.
    Возвращает (True, None) или (False, "пояснение")
    Сообщение о нехватке возвращается в удобном для пользователя виде,
    например: "Недостаточно респекты: нужно 100, у вас 37"
    """
    if not cfg_accounts.has_section(uid):
        return False, "Профиль не найден."

    for k, need in costs.items():
        if not need:
            continue
        have = _get_account_numeric(cfg_accounts, uid, k)
        if have < need:
            # читабельное имя ресурса
            pretty_name = RESOURCE_NAMES.get(k, k)
            return False, f"Недостаточно {pretty_name}: нужно {fmt(need)}, у вас {fmt(have)}"
    return True, None

def deduct_costs(cfg_accounts, uid, costs):
    """Списывает (модифицирует cfg_accounts) все переданные costs (целые)."""
    if not cfg_accounts.has_section(uid):
        cfg_accounts[uid] = {}
    for k, amt in costs.items():
        if not amt:
            continue
        prev = _get_account_numeric(cfg_accounts, uid, k)
        cfg_accounts[uid][k] = str(prev - int(amt))

def apply_effects(cfg_accounts, uid, effects):
    """
    Эффекты в формате:
      add_char:<key>=<value>
      set_field:<field>=<value>
      inc_field:<field>=<amount>
    Можно перечислять несколько через ';' — парсится ранее.
    Возвращает список текстовых описаний применённых эффектов.
    """
    applied = []
    if not cfg_accounts.has_section(uid):
        cfg_accounts[uid] = {}
    for eff in effects:
        if eff.startswith("add_char:"):
            # add_char:name=val
            rest = eff[len("add_char:"):].strip()
            if "=" in rest:
                key, val = rest.split("=", 1)
                key = key.strip()
                val = val.strip()
                cfg_accounts[uid][key] = val
                applied.append(f"Добавлено свойство {key} = {val}")
        elif eff.startswith("set_field:"):
            rest = eff[len("set_field:"):].strip()
            if "=" in rest:
                field, val = rest.split("=", 1)
                field = field.strip()
                val = val.strip()
                cfg_accounts[uid][field] = val
                applied.append(f"Установлено {field} = {val}")
        elif eff.startswith("inc_field:"):
            rest = eff[len("inc_field:"):].strip()
            if "=" in rest:
                field, val = rest.split("=", 1)
                field = field.strip()
                try:
                    inc = int(val.strip())
                except Exception:
                    inc = 0
                prev = _get_account_numeric(cfg_accounts, uid, field)
                cfg_accounts[uid][field] = str(prev + inc)
                applied.append(f"+{inc} к {field}")
        else:
            # неизвестный эффект — сохраняем в виде raw ключа (если хочется расширить)
            applied.append(f"Неопознанный эффект: {eff}")
    return applied

def load_limits():
    cfg = configparser.ConfigParser()
    if not os.path.exists(LIMITS_FILE):
        open(LIMITS_FILE, "a", encoding="utf-8").close()
    cfg.read(LIMITS_FILE, encoding="utf-8")
    return cfg

def save_limits(cfg):
    with open(LIMITS_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)

def _load_accounts_direct():
    """Простой reader accounts.ini — используется для вычисления blimit без circular import."""
    cfg = configparser.ConfigParser()
    if not os.path.exists(ACCOUNTS_FILE):
        open(ACCOUNTS_FILE, "a", encoding="utf-8").close()
    cfg.read(ACCOUNTS_FILE, encoding="utf-8")
    return cfg

def load_history_respect():
    config = configparser.ConfigParser()
    if not os.path.exists(HISTORY_RESPECT_FILE):
        open(HISTORY_RESPECT_FILE, "a", encoding="utf-8").close()
    config.read(HISTORY_RESPECT_FILE, encoding='utf-8')
    return config

def save_history_respect(config):
    with open(HISTORY_RESPECT_FILE, "w", encoding="utf-8") as f:
        config.write(f)

def find_user_id_by_nick(nick):
    accounts = load_accounts()
    for sec in accounts.sections():
        # сравнение без учета регистра, строго имя фамилия с пробелом
        if accounts[sec].get('nick', '').strip().lower() == nick.strip().lower():
            return sec
    return None

def fmt(num):
    try:
        return locale.format_string("%d", int(num), grouping=True).replace('\xa0', '.')
    except Exception:
        return str(num)

def load_happy():
    cfg = configparser.ConfigParser()
    if os.path.exists(HAPPY_FILE):
        try:
            cfg.read(HAPPY_FILE, encoding="utf-8")
        except Exception:
            cfg = configparser.ConfigParser()
    else:
        cfg.add_section(HAPPY_SECTION)
        with open(HAPPY_FILE, "w", encoding="utf-8") as hf:
            cfg.write(hf)
    if not cfg.has_section(HAPPY_SECTION):
        cfg.add_section(HAPPY_SECTION)
    return cfg

def save_happy(cfg):
    with open(HAPPY_FILE, "w", encoding="utf-8") as hf:
        cfg.write(hf)


def _ensure_file(path):
    if not os.path.exists(path):
        open(path, "a", encoding="utf-8").close()


def load_tasks_cfg():
    _ensure_file(TASKS_FILE)
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read(TASKS_FILE, encoding="utf-8")
    return cfg


def save_tasks_cfg(cfg):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)


def load_user_tasks_cfg():
    _ensure_file(USER_TASKS_FILE)
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read(USER_TASKS_FILE, encoding="utf-8")
    return cfg


def save_user_tasks_cfg(cfg):
    with open(USER_TASKS_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)


def generate_task_id():
    """Генерация 4-значного ID, проверка коллизий"""
    cfg = load_tasks_cfg()
    for _ in range(1000):
        tid = str(random.randint(1000, 9999))
        sec = f"task_{tid}"
        if not cfg.has_section(sec):
            return tid
    # в маловероятном случае — brute force scan
    i = 1000
    while i <= 9999:
        sec = f"task_{i}"
        if not cfg.has_section(sec):
            return str(i)
        i += 1
    raise RuntimeError("Не удалось сгенерировать уникальный ID задания")
        
DEFAULT_BASE_LIMIT = 80_000_000
EVOLUTION_BASES = {1: 130_000_000, 2: 205_000_000, 3: 305_000_000}
LEVEL_ADDITION_PER_LEVEL = 1_000_000
LEVEL_ADDITION_CAP = 100_000_000
LIMIT_UP_STZAM = 50_000_000
LIMIT_UP_LEADER = 50_000_000
LIMIT_UP_COMMERS = 100_000_000
LIMIT_UP_GRZAM = 50_000_000
LIMIT_UP_GRCHRAN = 100_000_000

def compute_blimit_for_user(user_id):
    """
    Рассчитать blimit:
      - base = DEFAULT_BASE_LIMIT (или EVOLUTION_BASES[ev_level], если там есть)
      - + LEVEL_ADDITION_PER_LEVEL * level (ограничено LEVEL_ADDITION_CAP)
      - + LIMIT_UP_STZAM если szam == 1
      - + LIMIT_UP_LEADER если lgrating == 1
      - + LIMIT_UP_COMMERS если COMMERS == 1
    Эффекты суммируются.
    """
    uid = str(user_id)
    acc = _load_accounts_direct()  # предполагается, что возвращает секции по uid

    # defaults
    level = 0
    ev_level = 0
    szam = 0
    lgrating = 0
    commers = 0

    try:
        if acc.has_section(uid):
            section = acc[uid]
            def safe_int(val):
                try:
                    return int(val or 0)
                except Exception:
                    return 0

            level = safe_int(section.get("level", 0))
            ev_level = safe_int(section.get("ev_level", 0))
            szam = safe_int(section.get("szam", 0))
            lgrating = safe_int(section.get("lgrating", 0))
            commers = safe_int(section.get("commers", 0))
            grzam = safe_int(section.get("grzam", 0))
            grchran = safe_int(section.get("grchran", 0))
    except Exception:
        # при ошибке чтения — оставить значения по умолчанию (0)
        pass

    # базовый лимит (заменяем, если есть эволюция)
    base = EVOLUTION_BASES.get(ev_level, DEFAULT_BASE_LIMIT)

    # прибавка за уровень с капом
    addition = level * LEVEL_ADDITION_PER_LEVEL
    if addition > LEVEL_ADDITION_CAP:
        addition = LEVEL_ADDITION_CAP

    # бонусы по характеристикам — суммируются независимо
    bonus = 0
    if commers == 1:
        bonus += LIMIT_UP_COMMERS
    if szam == 1:
        bonus += LIMIT_UP_STZAM
    if grzam == 2:
        bonus += LIMIT_UP_GRZAM
    if grchran == 2:
        bonus += LIMIT_UP_GRCHRAN   
    if lgrating == 1:
        bonus += LIMIT_UP_LEADER

    total = int(base + addition + bonus)
    return total

def ensure_limits_entry_for_user(user_id):
    """
    Убедиться, что в limitsvivod.ini есть секция для user_id и blimit актуален.
    Возвращает (blimit:int, tlimit:int)
    """
    uid = str(user_id)
    cfg = load_limits()
    updated = False
    blimit_calc = compute_blimit_for_user(uid)
    if not cfg.has_section(uid):
        cfg[uid] = {'blimit': str(blimit_calc), 'tlimit': '0'}
        updated = True
    else:
        try:
            cur = int(cfg[uid].get('blimit', '0'))
        except Exception:
            cur = 0
        if cur != blimit_calc:
            cfg[uid]['blimit'] = str(blimit_calc)
            updated = True
        # ensure tlimit numeric
        try:
            _ = int(cfg[uid].get('tlimit', '0'))
        except Exception:
            cfg[uid]['tlimit'] = '0'
            updated = True
    if updated:
        save_limits(cfg)
    return int(cfg[uid]['blimit']), int(cfg[uid]['tlimit'])

def get_user_limit_remaining(user_id):
    """
    Возвращает (blimit, tlimit, remaining)
    """
    blimit, tlimit = ensure_limits_entry_for_user(user_id)
    remaining = max(0, blimit - tlimit)
    return blimit, tlimit, remaining

def add_to_user_tlimit(user_id, amount):
    """
    Увеличить tlimit на amount (int)
    """
    uid = str(user_id)
    cfg = load_limits()
    if not cfg.has_section(uid):
        cfg[uid] = {'blimit': str(compute_blimit_for_user(uid)), 'tlimit': '0'}
    try:
        prev = int(cfg[uid].get('tlimit', '0'))
    except Exception:
        prev = 0
    cfg[uid]['tlimit'] = str(prev + int(amount))
    save_limits(cfg)

def reset_all_tlimits():
    """
    Сбросить tlimit для всех пользователей (вызывать при закрытии расчётной недели).
    """
    accounts = _load_accounts_direct()
    cfg = load_limits()
    changed = False
    for sec in accounts.sections():
        if not sec.isdigit():
            continue
        uid = sec
        blimit_calc = compute_blimit_for_user(uid)
        if not cfg.has_section(uid):
            cfg[uid] = {}
        cfg[uid]['blimit'] = str(blimit_calc)
        if cfg[uid].get('tlimit', '0') != '0':
            cfg[uid]['tlimit'] = '0'
            changed = True
    if changed:
        save_limits(cfg)
        
def load_rd_claims():
    """
    Хранение факта получения RD-бонуса выполняется в виде:
      [YYYY-MM-DD]
      123456789 = 2025-10-24 12:00:00
    где секция — дата расчётного дня.
    """
    cfg = configparser.ConfigParser()
    # обеспечить наличие файла на диске
    if not os.path.exists(RD_BONUS_FILE):
        open(RD_BONUS_FILE, "a", encoding="utf-8").close()
    cfg.read(RD_BONUS_FILE, encoding="utf-8")
    return cfg

def save_rd_claims(cfg):
    with open(RD_BONUS_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)
        
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
#система суперприза
def get_superprize_state():
    """
    Возвращает (current:int, initial:int).
    Инициализирует секцию, если в settings.ini её нет.
    По требованиям: всегда стартует с SUPERPRIZE_INITIAL и к ней добавляются вклады,
    нет никакой 'цели' — копилка растёт пока кто-то не выбьет суперприз,
    после выдачи копилка сбрасывается обратно к SUPERPRIZE_INITIAL.
    """
    cfg = load_settings()
    if not cfg.has_section(SUPERPRIZE_SECTION):
        cfg.add_section(SUPERPRIZE_SECTION)
        cfg[SUPERPRIZE_SECTION]['current'] = str(SUPERPRIZE_INITIAL)
        save_settings(cfg)
    try:
        current = int(cfg[SUPERPRIZE_SECTION].get('current', str(SUPERPRIZE_INITIAL)) or SUPERPRIZE_INITIAL)
    except Exception:
        current = SUPERPRIZE_INITIAL
    return current, SUPERPRIZE_INITIAL

def add_to_superprize(amount: int):
    """
    Добавляет amount (int) снежинок в копилку суперприза.
    Если секции нет — инициализируем с SUPERPRIZE_INITIAL и затем добавляем.
    """
    cfg = load_settings()
    if not cfg.has_section(SUPERPRIZE_SECTION):
        cfg.add_section(SUPERPRIZE_SECTION)
        cfg[SUPERPRIZE_SECTION]['current'] = str(SUPERPRIZE_INITIAL)
    try:
        cur = int(cfg[SUPERPRIZE_SECTION].get('current', str(SUPERPRIZE_INITIAL)) or SUPERPRIZE_INITIAL)
    except Exception:
        cur = SUPERPRIZE_INITIAL
    cfg[SUPERPRIZE_SECTION]['current'] = str(cur + int(amount))
    save_settings(cfg)

def reset_superprize():
    """
    Обнуляет копилку суперприза — устанавливает текущее значение обратно в SUPERPRIZE_INITIAL.
    (Нет никакой цели — всегда стартуем с SUPERPRIZE_INITIAL).
    """
    cfg = load_settings()
    if not cfg.has_section(SUPERPRIZE_SECTION):
        cfg.add_section(SUPERPRIZE_SECTION)
    cfg[SUPERPRIZE_SECTION]['current'] = str(SUPERPRIZE_INITIAL)
    save_settings(cfg)

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

def load_config(file_path: str) -> configparser.ConfigParser:
    """
    Чтение INI-файла с поддержкой явно заданной кодировки.
    Если файл не читается как UTF-8, пробуем Windows-1251.
    """
    config = configparser.ConfigParser()
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            config.read_file(file)  # Читаем как UTF-8 по умолчанию
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="windows-1251") as file:
            config.read_file(file)  # Переходим на Windows-1251 если UTF-8 не сработал
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

def load_user_chars():
    cfg = configparser.ConfigParser(interpolation=None)
    # при чтении не падает, если файла нет
    if not os.path.exists(USER_CHARS_FILE):
        open(USER_CHARS_FILE, "a", encoding="utf-8").close()
    cfg.read(USER_CHARS_FILE, encoding="utf-8")
    return cfg

def save_user_chars(cfg):
    with open(USER_CHARS_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)

def get_user_chars(user_id):
    """
    Возвращает mapping для секции user_characteristics.ini или None.
    Если секции нет — None (вызывать ensure_user_chars при необходимости).
    """
    uid = str(user_id)
    cfg = load_user_chars()
    if cfg.has_section(uid):
        return cfg[uid]
    return None

def ensure_user_chars(user_id):
    """
    Убедиться, что для user_id есть секция в user_characteristics.ini.
    Если нет — добавить секцию с дефолтными значениями.
    Возвращает загруженный config (после изменений).
    """
    uid = str(user_id)
    cfg = load_user_chars()
    if not cfg.has_section(uid):
        cfg[uid] = {
            "ed_rub": "0",
            "ed_exp": "0",
            "ed_activ": "0",
            "ed_bust": "0",
            "ew_rub": "0",
            "ew_exp": "0",
            "ew_activ": "0",
            "ew_bust": "0",
            "max_zp": "0",
            "exp_multiplier": "1.0"
        }
        save_user_chars(cfg)
    return cfg
        
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

# 📂 Работа с INI
def load_deposits():
    config = configparser.ConfigParser()
    config.read("deposits.ini", encoding="utf-8")
    return config

def save_deposits(config):
    with open("deposits.ini", "w", encoding="utf-8") as f:
        config.write(f)
    
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
def calculate_salary(ball, level, ev_level, warnings, position, lgrating):
    """
    Функция calculate_salary рассчитывает зарплату по формуле:
      salary = ball * daily_rate * (1 - 0.25 * warnings)
    При этом результат приводится к целому числу.
    """
    daily_rate = get_daily_rate_by_level(level, ev_level, position, lgrating)
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
        ev_level = int(sec.get('ev_level', '0'))  # Уровень пользователя, по умолчанию 0
        exp = int(sec.get('exp', '0'))  # Получение опыта
        position = sec.get('position', '')  # <-- ДОЛЖЕН идти ПЕРЕД вызовом get_daily_rate_by_level
        lgrating = int(sec.get('lgrating', '0'))
        daily_rate = get_daily_rate_by_level(level, ev_level, position, lgrating)
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
            't': sec.get('t', '0'),
            'ev_level': sec.get('ev_level', '0'),
            'evball': sec.get('evball', '0'),
            'ev_stones': sec.get('ev_stones', '0'),
            'lgrating': sec.get('lgrating', '0'),
            'piarvr': sec.get('piarvr', '0'),
            'mining': sec.get('mining', '0'),
            'oosk': sec.get('oosk', '0'),
            'uosk': sec.get('uosk', '0'),
            'losk': sec.get('losk', '0'),
            'comission': sec.get('losk', '0'),
            'commers': sec.get('commers', '0'),
        }
    return None

def get_daily_rate_by_level(level, ev_level, position, lgrating):
    """
    Рассчитывает ставку для заместителя на основе уровня, эволюции и позиции.
    :param level: Уровень заместителя (от 0 до 100)
    :param ev_level: Уровень эволюции (от 0 до 3)
    :param position: Должность пользователя (строка)
    :return: Ежедневная ставка в рублях
    """
    if level < 0 or level > 100:
        raise ValueError("Уровень должен быть в диапазоне от 0 до 100.")

    base_rate = 200_000  # Базовая ставка для уровня 0
    rate_increment = 3_000  # Увеличение ставки за каждый уровень
    evo_bonus = ev_level * 50_000

    # Бонус для старшего заместителя
    position_bonus = 50_000 if position == "Старший заместитель" else 0
    r_bonus = 50_000 if lgrating == 1 else 0

    return base_rate + (level * rate_increment) + evo_bonus + position_bonus + r_bonus

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
        [KeyboardButton("Отчёт"), KeyboardButton("Задания")],
        [KeyboardButton("Центр обмена"), KeyboardButton("Финансы")],
        [KeyboardButton("Мастерская"), KeyboardButton("Крафтинг")]
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

    # Приветствия по уровням
    if admin_level == -2:
        await update.message.reply_text(
            f"🐼‍ Рады приветствовать снова *{nick}*!\n"
            f"🟨 Вы авторизовались как XVIP.",
            parse_mode="Markdown"
        )
    elif admin_level == -1:
        await update.message.reply_text(
            f"🐼 Рады приветствовать снова *{nick}*!\n"
            f"⬜ Вы авторизовались как Гость. Для выдачи прав обратитесь к администратору бота.",
            parse_mode="Markdown"
        )
    elif admin_level == 0:
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

    # Показываем главное меню
    await update.message.reply_text("Ниже представлено главное меню. Выберите нужный вариант.", reply_markup=get_main_keyboard(user_id))

    # Проверяем, не получал ли пользователь уже новогодний бонус
    happy_cfg = load_happy()
    claimed = happy_cfg.has_option(HAPPY_SECTION, str(user_id)) and happy_cfg[HAPPY_SECTION].get(str(user_id))
    if not claimed:
        # Отправляем подсказку о команде /happy (показывается только если не получал бонус)
        messageee = "🎄 Забери новогодний бонус с помощью команды <code>/happy</code>."
        messageee_wrapped = f"<blockquote><b>{messageee}</b></blockquote>"
        await update.message.reply_text(messageee_wrapped, reply_markup=get_main_keyboard(user_id), parse_mode='HTML')
    # если already claimed — не показываем подсказку

async def happy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /happy — выдача разового новогоднего бонуса в зависимости от позиции.
    После получения пометка записывается в happy.ini — повторно получить нельзя.
    """
    from datetime import datetime as _dt  # явный локальный импорт, чтобы избежать конфликтов имен

    user = update.effective_user
    user_id = str(user.id)

    # Проверка доступа/регистрации
    accounts_cfg = load_accounts()
    if not accounts_cfg.has_section(user_id):
        await update.message.reply_text("❌ Профиль не найден. Пройдите регистрацию.")
        return

    happy_cfg = load_happy()
    if happy_cfg.has_option(HAPPY_SECTION, user_id):
        # Уже получал
        await update.message.reply_text(
            "🎁 Вы уже забрали свой новогодний бонус 🎄",
            reply_markup=get_back_keyboard()
        )
        return

    # Получаем уровень/должность пользователя
    user_info = get_user_info(int(user_id))
    admin_level = int(user_info.get('is_admin', 0)) if user_info else -1
    nick = user_info.get('nick') if user_info else (user.full_name or str(user_id))

    # Определяем бонусы по позиции
    bonuses = {
        3: (1000, 1000, 100),   # Лидер семьи
        2: (500, 500, 50),      # Старший заместитель
        0: (250, 250, 25),      # Заместитель
        1: (500, 500, 50),      # Хранитель
        -2: (100, 100, 10),     # XVIP
    }
    if admin_level not in bonuses:
        await update.message.reply_text(
            "❌ Для вашей позиции бонус не предусмотрен. С наступающим 🎄",
            reply_markup=get_back_keyboard()
        )
        return

    exp_amt, t_amt, osk_amt = bonuses[admin_level]

    # Записываем бонусы в accounts.ini
    try:
        def iget(cfg, uid, key):
            try:
                return int(cfg[uid].get(key, "0"))
            except Exception:
                return 0

        accounts_cfg = load_accounts()
        if not accounts_cfg.has_section(user_id):
            accounts_cfg.add_section(user_id)
        accounts_cfg[user_id]['exp'] = str(iget(accounts_cfg, user_id, 'exp') + exp_amt)
        accounts_cfg[user_id]['t'] = str(iget(accounts_cfg, user_id, 't') + t_amt)
        accounts_cfg[user_id]['osk'] = str(iget(accounts_cfg, user_id, 'osk') + osk_amt)
        save_accounts(accounts_cfg)
    except Exception:
        await update.message.reply_text("❌ Ошибка при начислении бонуса. Попробуйте позже.")
        return

    # Пометка в happy.ini — сохраняем время и позицию
    timestamp = _dt.now().strftime("%Y-%m-%d %H:%M:%S")
    happy_cfg[HAPPY_SECTION][user_id] = f"{timestamp}|level={admin_level}"
    save_happy(happy_cfg)

    # Праздничное поздравление (индивидуально по позиции)
    role_names = {
        3: "Лидер семьи",
        2: "Старший заместитель",
        0: "Заместитель",
        1: "Хранитель",
        -2: "XVIP"
    }
    role_name = role_names.get(admin_level, "Участник")

    congrats_text = (
        f"🎄 Поздравляем, <b>{nick}</b>! 🎄\n\n"
        f"🛷 <b>Вы получили новогодний бонус как {role_name}.</b>\n\n"
        f"→ ❄️ Снежинок: <b>{t_amt}</b>\n"
        f"→ ⚡ Опыт: <b>{exp_amt}</b>\n"
        f"→ 💈 Бустов: <b>{osk_amt}</b>\n\n"
        f"Пусть новый год принесёт удачу, радость и много волшебных моментов ✨"
    )

    await update.message.reply_text(congrats_text, parse_mode="HTML", reply_markup=get_back_keyboard())


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
    if not user_info:
        await update.message.reply_text("Информация о пользователе не найдена.", reply_markup=get_back_keyboard())
        return

    # Вспомогательные функции
    def safe_int(value, default=0):
        try:
            return int(value or 0)
        except Exception:
            return default

    def fmt(num):
        try:
            return locale.format_string("%d", int(num), grouping=True).replace('\xa0', '.')
        except Exception:
            try:
                return str(int(float(num)))
            except Exception:
                return "0"

    current_level = safe_int(user_info.get('level', 0))
    ev_level = safe_int(user_info.get('ev_level', 0))
    current_exp = safe_int(user_info.get('exp', 0))
    required_exp = 350 + (current_level * 7)

    predicted_payment_formatted = fmt(user_info.get('predicted_payment', 0))
    daily_rate_formatted = fmt(user_info.get('daily_rate', 0))
    personal_account_formatted = fmt(user_info.get('personal_account', 0))
    position = user_info.get('position', '')

    evball = safe_int(user_info.get('evball', 0))
    ev_stones = safe_int(user_info.get('ev_stones', 0))
    warnings = user_info.get('warnings', '0') or '0'

    # Основное сообщение — статистика пользователя
    message = (
        f"👤 Никнейм: {user_info.get('nick','')}\n"
        f"🔮 Реальное имя: {user_info.get('realname','')}\n"
        f"🎂 Дата рождения: {user_info.get('daterod','')}\n"
        f"💼 Должность: {user_info.get('position','')}\n"
        f"🧗 Уровень: {current_level}\n"
        f"🧧 Эволюция: {ev_level}\n"
        f"⚡ Очки опыта: {current_exp} из {required_exp}\n"
        f"🔥 Респекты: {ev_stones}\n"
        f"💰 Ставка за монету: {daily_rate_formatted} RUB\n"
        f"⚠︎ Предупреждения: {warnings}\n"
        f"🧿 Монеты активности: {user_info.get('ball', 0)}\n"
        f"🪙 Монеты эволюции: {evball}\n"
        f"💈 Бусты: {user_info.get('osk', 0)}\n"
        f"❄️ Снежинки: {user_info.get('t', 0)}\n"
        f"💸 Зарплата: {predicted_payment_formatted} RUB\n"
        f"💳 Личный счет: {personal_account_formatted} RUB\n"
    )

    # Отправляем фото (если есть)
    try:
        with open("stats.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
    except Exception:
        pass

    # Отправляем основное сообщение (статистика)
    await update.message.reply_text(message, reply_markup=get_back_keyboard())

    # ------- Блок льгот в том же сообщении --------
    benefits_count = 0
    stavka_count = 0
    benefit_lines = []

    # Лидер рейтинга
    lgrating = int(user_info.get('lgrating', 0))
    if lgrating == 1:
        benefits_count += 1
        stavka_count += 25
        benefit_lines.append("<b>🏆 Лидер рейтинга — действует</b>")

    # Старший заместитель
    if position == "Старший заместитель":
        benefits_count += 1
        stavka_count += 25
        benefit_lines.append("<b>🌟 Старший заместитель — действует</b>")

    # Эволюция I
    if ev_level >= 1:
        benefits_count += 1
        stavka_count += 25
        benefit_lines.append("<b>🀄 Эволюция первая — действует</b>")

    # Эволюция II
    if ev_level >= 2:
        benefits_count += 1
        stavka_count += 25
        benefit_lines.append("<b>🎴 Эволюция вторая — действует</b>")

    # Эволюция III
    if ev_level >= 3:
        benefits_count += 1
        stavka_count += 25
        benefit_lines.append("<b>🃏 Эволюция третья — действует</b>")

    if ev_level >= 100: #заменить после добавления лампы джина 
        benefits_count += 1
        stavka_count += 0
        benefit_lines.append("<b>🧞 Эволампа джина — действует</b>")
        
    piarvr = int(user_info.get('piarvr', 0))
    if piarvr == 1:
        benefits_count += 1
        stavka_count += 0
        benefit_lines.append("<b>🎤 Пиарщик VIP ADV — действует</b>")

    commers = int(user_info.get('commers', 0))
    if commers == 1:
        benefits_count += 1
        stavka_count += 0
        benefit_lines.append("<b>📈 Коммерсант — действует</b>")

    mining = int(user_info.get('mining', 0))
    if mining == 1:
        benefits_count += 1
        stavka_count += 0
        benefit_lines.append("<b>🕹 Семейный майнинг — действует</b>")

    if benefits_count > 0:
         benefits_info = (
             "Вы получаете следующие виды льгот:\n"
             + "\n".join(benefit_lines)
         )
    else:
        benefits_info = "У Вас нет льгот."

    rd = get_rd()
    rd1 = rd - timedelta(days=6)
    today = datetime.now().date()
        
    msg_benefits = (
        "💽 <b>Расчётный день и льготы.</b>\n"
        f"📅 Расчётная неделя: <b>{rd1.strftime('%d.%m.%Y')} - {rd.strftime('%d.%m.%Y')}</b>\n"
        f"💼 Ближайший расчётный день: <b>{rd.strftime('%d.%m.%Y')}</b>\n"
        f"🏵 Ваши льготы: <b>{benefits_count}</b>\n"
        f"💰 Прибавка к базовой ставке: <b>{stavka_count}%</b>\n\n"
        f"{benefits_info}"
        "\n\n<i>Примечание: информация о премуществах всех видов льгот доступна с помощью команды /lg</i>"
    )

    await update.message.reply_text(msg_benefits, reply_markup=get_back_keyboard(), parse_mode='HTML')

# Рейтинг (команда "Рейтинг")
async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем топ игроков
    top_players = get_top_players()

    # Эмодзи и соответствия уровней / рангов / эволюции
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

    rank_emojis = {
        "Старший заместитель": "🟥 Старший заместитель",
        "Лидер семьи": "🟥 Лидер семьи",
        "Хранитель": "🟫 Хранитель",
        "Заместитель": "🔳 Заместитель",
        "XVIP": "🟨 XVIP",
        "Гость": "⬜ Гость"
    }

    evo_emojis = {
        1: "🀄",
        2: "🎴",
        3: "🃏"
    }

    def get_activity_level(ball: int) -> str:
        if ball >= 875:
            return "🟣 Превосходная активность"
        elif 700 <= ball < 875:
            return "🟡 Максимальная активность"
        elif 525 <= ball < 700:
            return "🟢 Средняя активность"
        elif 350 <= ball < 525:
            return "🔴 Минимальная активность"
        else:
            return "⚪ Недостаточная активность"

    def get_level_emoji(level: int) -> str:
        for level_range, emoji in level_emojis:
            if level in level_range:
                return emoji
        return "❔"

    def get_rank_emoji(rank: str) -> str:
        return rank_emojis.get(rank, "⬜ Гость")

    # Загружаем accounts для поиска ev_level по никам в топе (если доступен)
    try:
        accounts_cfg = load_accounts()
    except Exception:
        accounts_cfg = None

    # Попытка отправить изображение рейтинга (если есть)
    try:
        with open("rating.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
    except Exception:
        pass

    # Формируем сообщение с топом
    if not top_players:
        leaderboard_message = "<b>🏆 На данный момент нет пользователей в рейтинге.</b>\n"
        await update.message.reply_text(leaderboard_message, reply_markup=get_back_keyboard(), parse_mode='HTML')
        # Прекращаем, если нет топа
        return
    else:
        message = "<b>🏆 Лидеры рейтинга за расчётную неделю.</b>\n\n"
        emojis = ["🥇", "🥈", "🥉"]

        for i, player in enumerate(top_players[:3]):
            # ожидаем, что player = (nick, ball, level, position)
            try:
                nick, ball, level, position = player
            except Exception:
                continue

            # Поиск ev_level для игрока в accounts_cfg (если доступен)
            ev_level = 0
            if accounts_cfg is not None:
                try:
                    for sec in accounts_cfg.sections():
                        if not sec.isdigit():
                            continue
                        try:
                            sec_nick = accounts_cfg[sec].get('nick', '')
                        except Exception:
                            sec_nick = ''
                        if sec_nick and sec_nick.lower() == str(nick).lower():
                            try:
                                ev_level = int(accounts_cfg[sec].get('ev_level', '0') or 0)
                            except Exception:
                                ev_level = 0
                            break
                except Exception:
                    ev_level = 0

            # Приоритет эволюции над обычным эмодзи уровня
            try:
                lvl_int = int(level or 0)
            except Exception:
                lvl_int = 0

            if ev_level > 0:
                level_emoji = evo_emojis.get(ev_level, get_level_emoji(lvl_int))
            else:
                level_emoji = get_level_emoji(lvl_int)

            activity_str = get_activity_level(int(ball or 0))
            rank_str = get_rank_emoji(position)

            if i == 0:
                message += f"{emojis[i]} <b>{nick} {level_emoji}</b>\n<b>{rank_str}</b>\n<b>{activity_str}</b>\n<b>🧿 {ball}</b>\n\n"
            else:
                message += f"{emojis[i]} {nick} {level_emoji}\n{rank_str}\n{activity_str}\n🧿 {ball}\n\n"

        # Отправляем сформированный топ (без наград — награды отправим после персональной секции)
        await update.message.reply_text(message, reply_markup=get_back_keyboard(), parse_mode='HTML')

    # ===== Персональная секция (показатели пользователя) =====
    user_id = update.effective_user.id
    try:
        user_info = get_user_info(user_id)
    except Exception:
        user_info = None

    if not user_info:
        await update.message.reply_text("Информация о пользователе не найдена.", reply_markup=get_back_keyboard())
        return

    # Определяем эмодзи уровня пользователя (ev_level приоритетен)
    try:
        points = int(user_info.get('ball', 0) or 0)
    except Exception:
        points = 0
    try:
        user_level = int(user_info.get('level', 0) or 0)
    except Exception:
        user_level = 0
    try:
        ev_level_user = int(user_info.get('ev_level', 0) or 0)
    except Exception:
        ev_level_user = 0

    if ev_level_user > 0:
        user_level_emoji = evo_emojis.get(ev_level_user, get_level_emoji(user_level))
    else:
        user_level_emoji = get_level_emoji(user_level)

    if points >= 875:
        user_activity_level = "🟣 Превосходная"
    elif 700 <= points < 875:
        user_activity_level = "🟡 Максимальная"
    elif 525 <= points < 700:
        user_activity_level = "🟢 Средняя"
    elif 350 <= points < 525:
        user_activity_level = "🔴 Минимальная"
    else:
        user_activity_level = "⚪ Недостаточная"

    # Сообщение с личными показателями
    personal_message = (
        "📋 Ваши показатели.\n"
        f"👤 Никнейм: {user_info.get('nick', 'Неизвестный')} {user_level_emoji}\n"
        f"⚖️ Активность: {user_activity_level}\n"
        f"🧿 Монеты активности: {points}\n"
    )

    # Отправляем персональную информацию
    await update.message.reply_text(personal_message, reply_markup=get_back_keyboard())

    # ===== Награды (правила расчётного дня) — отправляем после персональной секции =====
    awards_message = (
        "ℹ️ Правилами установлены награды расчётного дня:\n\n"
        "🥇 место - 💽 Лидер рейтинга (льгота) — требуется превосходная активность.\n"
        "🥈 место - 500 ❄️ + 500 ⚡ + 25 🔥 — требуется максимальная активность.\n"
        "🥉 место - 250 ❄️ + 250 ⚡ + 10 🔥 — требуется средняя активность.\n"
    )
    awards_message = f"<blockquote><b>{awards_message}</b></blockquote>"
    await update.message.reply_text(awards_message, reply_markup=get_back_keyboard(), parse_mode='HTML')

    # Доп. сообщение только для админов > 1 уровня
    try:
        if int(user_info.get("is_admin", "0") or 0) > 1:
            await update.message.reply_text(
                "🅰 Для просмотра глобальной активности по всем должностям используйте команду: <code>/aactive</code>",
                parse_mode="HTML",
                reply_markup=get_back_keyboard()
            )
    except Exception:
        pass

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
        keyboard.append([InlineKeyboardButton("💰 Заявки на пополнения", callback_data="admin_deposits")])
        keyboard.append([InlineKeyboardButton("💰 Заявки на вывод", callback_data="admin_withdrawals")])

    # Кнопка для администраторов с уровнем 3
    if admin_level >= 3:
        keyboard.append([InlineKeyboardButton("🅿 Технический рестарт", callback_data="force_technical_exit")])
        keyboard.append([InlineKeyboardButton("🔧 Технические работы", callback_data="toggle_maintenance")])
        keyboard.append([InlineKeyboardButton("🎆 Обновление", callback_data="new_obnova")])
        keyboard.append([InlineKeyboardButton("🎷 Рейтинг (итоги)", callback_data="rating_results")])

    keyboard.append([InlineKeyboardButton("🚪 Выйти", callback_data="exit_admin_panel")])

    # Определение эмодзи для уровня администратора
    level_emoji = '1️⃣' if admin_level == 1 else '2️⃣' if admin_level == 2 else '3️⃣'

    # Отправка клавиатуры с кнопками
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(f"🅰 Вы успешно вошли в панель администратора.\n📟 Команды: /ahelp\n\nВаш уровень прав: {level_emoji}", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(f"🅰 Вы успешно вошли в панель администратора.\n📟 Команды: /ahelp\n\nВаш уровень прав: {level_emoji}", reply_markup=reply_markup)
        
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
            f"Для подтверждения уровня посетите Центр обмена → Функции → Подтверждение уровня и выполните <code>/lvlconf</code>.",
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
    messagee = ("ℹ️ Награда за отчёты - 🧿 монеты активности и(или) 💈 бусты.")
    messagee = f"<blockquote><b>{messagee}</b></blockquote>"
    messageee = ("🏮 Забери ежедневный бонус с помощью команды <code>/bonus</code>.")
    messageee = f"<blockquote><b>{messageee}</b></blockquote>"
    await update.message.reply_text(messagee, reply_markup=get_back_keyboard(), parse_mode='HTML')
    await update.message.reply_text(messageee, reply_markup=get_back_keyboard(), parse_mode='HTML')

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
        elif text == "Финансы":
            await update.message.reply_text(
                "Выберите тип финансовой операции:",
                reply_markup=get_main_finance()
            )
        elif text == "Пополнение счёта":
            await request_deposit(update, context)
        elif text == "Вывод средств":
            await request_withdrawal(update, context)
        elif text == "Рейтинг":
            await rating(update, context)
        elif text == "Задания":
            await tasks_command(update, context)
        elif text == "Мастерская":
            await workshop(update, context)
        elif text == "Раскалывание":
            await merge_pumpkins(update, context)
        elif text == "Праздничный крафт":
            await craft(update, context)
        elif text == "Награды":
            await items(update, context)    
        elif text == "История наград":
            await reward_history(update, context)
        elif text == "Центр обмена":
            await active(update, context)
        elif text == "Обычные наборы":
            await usual_sets(update, context)  
        elif text == "Ресурсные наборы":
            await seasonal_sets(update, context)
        elif text == "Уровневые наборы":
            await lvl_sets(update, context)
        elif text == "Лимитированные наборы":
            await limited_sets(update, context)
        elif text == "Функции":
            await get_main_function(update, context)    
        elif text == "Подтверждение уровня":
            await pod(update, context)
        elif text == "Эволюция":
            await ev(update, context)
        elif text == "Эволавка":
            await characteristics(update, context)    
        elif text == "Снятие предупреждения":
            await pred(update, context)
        elif text == "Крафтинг":
            await verstak(update, context)
        elif text == "Ресурсы":
            await verstak1(update, context)
        elif text == "Льготы":
            await verstak2(update, context)
        elif text == "Предметы":
            await verstak3(update, context)
        elif text == "Крафтовые наборы":
            await verstak4(update, context)
        elif text == "Назад в меню крафтинга":
            await verstak(update, context)    
        elif text == "Назад в центр обмена":
            await active(update, context)
        elif text == "Назад в мастерскую":
            await workshop(update, context)
        elif text == "Назад в меню выбора функций":
            await get_main_function(update, context)
        elif text == "☀️ Светлая сторона":
            await svetlaya_storona(update, context)
        elif text == "🖤 Темная сторона":
            await temnaya_storona(update, context)
        elif text == "⬅️ Назад в мастерскую":
            await workshop(update, context)
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

async def request_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("vivod.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)

    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    if not user_info:
        await update.message.reply_text("Ошибка: Информация о пользователе не найдена.")
        return

    # Проверки предупреждений
    try:
        warnings = int(user_info.get('warnings', 0) or 0)
    except (TypeError, ValueError):
        warnings = 0

    if warnings >= 1:
        await update.message.reply_text(
            "🔒 Система вывода заблокирована!\n\n"
            f"⚠️ У вас {warnings} предупреждение(й). Вывод средств будет доступен после снятия предупреждений."
        )
        return

    # Проверка специальных прав (max_zp)
    try:
        user_chars = get_user_chars(user_id)
        has_max_zp = str(user_chars.get('max_zp', '0')).strip() == "1" if user_chars else False
    except Exception:
        has_max_zp = False

    rd = get_rd()
    if not has_max_zp:
        if not rd:
            await update.message.reply_text("🔴 Расчётный день не установлен. Вывод средств временно недоступен.")
            return

        rd1 = rd - timedelta(days=6)
        today = datetime.now().date()

        if today != rd.date():
            await update.message.reply_text(
                "🔴 Вывод средств доступен только в расчётный день.\n\n"
                f"⚖️ Расчётная неделя.\n"
                f"📅 Период: {rd1.strftime('%d.%m.%Y')} - {rd.strftime('%d.%m.%Y')}\n"
                f"💽 Ближайший расчётный день: {rd.strftime('%d.%m.%Y')}"
            )
            return

    # Баланс — всегда целый
    try:
        balance = int(float(user_info.get('personal_account', 0) or 0))
    except (TypeError, ValueError):
        balance = 0

    # ---------------------------
    #     ЛИМИТЫ + ЗАЩИТА ОТ ОШИБОК
    # ---------------------------

    try:
        blimit, tlimit, remaining = get_user_limit_remaining(user_id)
    except Exception:
        blimit, tlimit, remaining = 0, 0, 0

    # Все значения — целые
    blimit = int(blimit or 0)
    tlimit = int(tlimit or 0)
    remaining = int(remaining or 0)

    # Реально доступно: минимум из баланса и лимита
    available_now = max(0, min(balance, remaining))

    if available_now <= 0:
        await update.message.reply_text(
            "🔒 Вы достигли лимита вывода на эту расчётную неделю или ваш баланс равен нулю.\n"
            f"🛑 Ваш недельный лимит: {fmt(blimit)} RUB\n"
            "Попробуйте позже после закрытия недели или пополните баланс."
        )
        return

    # ---------------------------
    #     КНОПКИ % ОТ БАЛАНСА
    # ---------------------------

    amounts = {}
    for pct in (25, 50, 75, 100):
        amt = int(balance * pct / 100)
        amounts[pct] = amt

    keyboard = []

    for pct in (25, 50, 75, 100):
        amt = amounts[pct]
        if amt <= 0:
            continue

        if amt > available_now:
            keyboard.append([
                InlineKeyboardButton(
                    f"Вывести {pct}% ({fmt(amt)}) — недоступно (лимит)",
                    callback_data=f"withdraw_blocked_{pct}"
                )
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(
                    f"Вывести {pct}% ({fmt(amt)})",
                    callback_data=f"withdraw_{pct}"
                )
            ])

    keyboard.append([InlineKeyboardButton("Ввести сумму вручную", callback_data="withdraw_custom")])

    info = (
        f"⛩️ Вывод средств доступен.\n"
        f"🧮 Сегодня расчётный день или у вас есть льгота, позволяющая выводить без ограничений.\n"
        f"💳 Баланс: {fmt(balance)} RUB\n"
        f"🔒 Недельный лимит: {fmt(blimit)} RUB\n"
        f"📌 Уже использовано: {fmt(tlimit)} RUB\n"
        f"🟢 Доступно для вывода сейчас: {fmt(available_now)} RUB\n\n"
        "Лимит на вывод зависит от уровня и эволюции члена старшего состава, а также льгот которые дают расширенный лимит.\n"
        "Выберите один из вариантов или введите сумму вручную."
    )

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(info, reply_markup=reply_markup)



async def start_custom_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_info = get_user_info(user_id)
    if not user_info:
        await query.message.edit_text("Ошибка: профиль не найден.")
        return

    blimit, tlimit, remaining = get_user_limit_remaining(user_id)
    try:
        balance = float(user_info.get('personal_account', 0) or 0)
    except Exception:
        balance = 0.0

    if remaining <= 0:
        await query.message.edit_text(
            "🔒 Вы достигли лимита вывода на эту расчётную неделю.\n"
            f"🛑 Ваш недельный лимит: {fmt(blimit)} RUB"
        )
        return

    context.user_data['awaiting_withdraw_amount'] = True
    context.user_data['withdraw_context'] = {
        'balance': balance,
        'remaining': remaining,
        'blimit': blimit,
        'tlimit': tlimit
    }

    await query.message.edit_text(
        f"✏️ Введите сумму вывода в RUB (максимум доступно {fmt(int(min(balance, remaining)))} RUB).\n\n"
        "Отменить — нажмите кнопку Отмена.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отменить", callback_data="cancel_withdraw")]])
    )

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

    # Поддерживаем оба варианта: context.user_data может хранить данные
    # прямо в корне (как вы делаете в start_custom_withdrawal),
    # или в виде вложенного словаря по user_id (если где-то ещё используется).
    def _cleanup_dict(d: dict):
        req_id = d.pop("request_id", None)
        d.pop("awaiting_withdraw_amount", None)
        d.pop("withdraw_context", None)
        return req_id

    req_id = None
    # Вариант: вложенный по user_id
    if user_id in context.user_data and isinstance(context.user_data[user_id], dict):
        req_id = _cleanup_dict(context.user_data[user_id])
        # если вложенный словарь опустел — удалим его совсем
        if not context.user_data[user_id]:
            context.user_data.pop(user_id, None)
    else:
        # Вариант: ключи на верхнем уровне
        req_id = _cleanup_dict(context.user_data)

    # Если была сохранённая заявка — удалим её (функция remove_request предполагается у вас)
    if req_id:
        try:
            remove_request(req_id)
        except Exception:
            # логируем/игнорируем ошибку удаления заявки, чтобы не ломать UX
            pass

    # Сообщение пользователю
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
            # после save_accounts(accounts_config)
        try:
            add_to_user_tlimit(user_id, amount)
        except Exception as e:
            logging.error(f"Ошибка при обновлении tlimit для {user_id}: {e}")
    else:
        await query.message.edit_text("❌ Пользователь не найден.")
        return
    
    # Удаляем заявку из файла
    config.remove_section(sec_name)
    with open(WITHDRAWALS_FILE, "w", encoding="utf-8") as f:
        config.write(f)
    
    # Уведомляем пользователя об одобрении заявки
    await context.bot.send_message(user_id, f"✅ Ваш вывод {amount} RUB одобрен, отпишите в чат XVIP (для 7-ых рангов) и не забудьте обязательно заполнить бюджет семьи с пометкой о снятии зарплаты (для 9-ых рангов)!")
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
        f"🅰 Новая заявка на вывод!\n"
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
    accounts = load_accounts()  # Загружаем аккаунты для быстрого доступа
    reports = [sec for sec in config.sections() if sec.startswith("report_") and config[sec].get("status", "pending") == "pending"]
    if not reports:
        await query.message.edit_text("📋 Нет отчетов, ожидающих проверки.")
        return
    text = "📋 Активные отчеты:\n"
    keyboard = []
    for sec in reports:
        nick = config[sec].get("nick", "Неизвестный")
        user_id = config[sec].get("user_id")
        # Получаем должность из accounts.ini
        position = "Неизвестная должность"
        if user_id and accounts.has_section(user_id):
            position = accounts[user_id].get("position", "Неизвестная должность")
        rid = sec[len("report_"):]
        text += f'\n🔹 Отчёт от должности {position}, никнейм: {nick} (ID отчёта: {rid})'
        keyboard.append([InlineKeyboardButton(f"ID отчёта: {rid}", callback_data=f"viewReport_{rid}")])
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
        await send_conversion_reminder(update, context, report_user_id=user_id)

        # Уведомляем администратора и запрашиваем количество принятых человек
        context.user_data['approve_report_id'] = report_id
        context.user_data['approve_user_id'] = user_id
        await query.message.edit_text(
            f"🕓 Отчёт ID {report_id} от {nick} подтверждён частично.\n"
        )
    except Exception as e:
        logging.error(f"Ошибка при подтверждении отчета {report_id}: {e}")
        await query.message.edit_text("❌ Не удалось подтвердить отчет.")
        
async def send_conversion_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE, report_user_id: int):
    # Достаём должность автора отчёта, точно как в approve_report
    author_info = get_user_info(report_user_id)
    author_position = author_info["position"] if author_info and "position" in author_info else "Неизвестно"

    # Отладка
    print(f"DEBUG: report_user_id={report_user_id}, author_info={author_info}, author_position={author_position}")

    # Если XVIP
    if author_position.strip().lower() == "xvip":
        image_filename = "xvip.png"
        caption = (
            f"🅰 Член старшего состава ранга XVIP "
            f"(должность: {author_position}).\n\n"
            "Система выдачи активности скорректирована на фото, "
            "введите количество монет активности согласно перечню:"
        )
    else:
        image_filename = "otchet.png"
        caption = (
            f"🅰 Должность автора отчёта: {author_position}.\n\n"
            "Необходимо ввести в чат количество монет активности для начисления согласно перечню:"
        )

    # Путь до картинки
    image_path = os.path.join(os.path.dirname(__file__), image_filename)
    if os.path.exists(image_path):
        await update.effective_message.reply_photo(
            photo=open(image_path, "rb"),
            caption=caption
        )
    else:
        await update.effective_message.reply_text(f"❌ Изображение {image_filename} не найдено!")
    
#Обработчик для ввода количества принятых человек
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
                admin_osk = int(config[str(admin_id)].get('t', '0'))
                config[str(admin_id)]['t'] = str(admin_osk + 5)  # выдаем 5 осколка админку за принятый отчёт

            if config.has_section(str(user_id)):
                user_data = config[str(user_id)]
                user_ball = int(user_data.get('ball', '0'))
                user_data['ball'] = str(user_ball + personnel_count)

                ev_level = int(user_data.get('ev_level', 0))
                evball = int(user_data.get('evball', 0))
                 # Определяем сколько начислять монет эволюции
                evo_bonus = [1000, 2000, 3000][ev_level - 1] if 1 <= ev_level <= 3 else 0
                user_data['evball'] = str(evball + evo_bonus)
                save_accounts(config)  # чтобы записалось

                if evo_bonus > 0:
                    try:
                        await context.bot.send_message(user_id, f"🪙 Вам начислено {evo_bonus} монет эволюции за одобренный отчёт по системе эволюции.")
                    except Exception: pass

                # Начисляем опыт и проверяем повышение уровня
                user_chars = get_user_chars(user_id)
                if user_chars:
                    exp_multiplier = float(user_chars.get('exp_multiplier', '1.0'))
                else:
                    # если секции нет — создаём дефолтную
                    ensure_user_chars(user_id)
                    exp_multiplier = 1.0
                current_exp = int(user_data.get('exp', '0'))
                current_level = int(user_data.get('level', '0'))
                required_exp = 350 + (current_level * 7)

                # Начисляем EXP
                exp_gained = int(personnel_count * exp_multiplier)
                new_exp = current_exp + exp_gained

                # Уведомляем пользователя о начисленных EXP
                exp_message = f"⚡ Вам начислено {exp_gained} очков опыта (EXP)."
                if exp_multiplier > 1.0:
                    percent_increase = (exp_multiplier - 1.0) * 100
                    exp_message += (
                        f"\n💽 У вас действует льгота, которая увеличивает получаемые EXP на {percent_increase:.0f}%."
                        f"\n💡 Данная льгота является постоянной."
                    )
                await context.bot.send_message(
                    user_id,
                    exp_message
                )
                
                # Проверяем повышение уровня
                level_up = False  # Флаг для отслеживания повышения уровня
                while new_exp >= required_exp and current_level < 100:
                    new_exp -= required_exp
                    current_level += 1
                    # --> вот тут вставить!
                    if current_level in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
                        user_data['lvlconf'] = '1'
                    required_exp = 350 + (current_level * 7)
                    level_up = True  # Уровень повышен

                # Обновляем ставку
                new_rate = 200_000 + (current_level * 3_000)

                # Сохраняем обновления
                user_data['exp'] = str(new_exp)
                user_data['level'] = str(current_level)
                user_data['daily_rate'] = str(new_rate)
                save_accounts(config)

                # **Добавляем осколки пользователю** ПРАЗДНИЧНАЯ СИСТЕМА - ПОТОМ УДАЛИТЬ
                current_shards = int(user_data.get('t', '0'))
                user_data['t'] = str(current_shards + (1 * personnel_count))  # 5 тыква за за каждый отчет
                save_accounts(config)

                # Уведомляем пользователя о повышении уровня
                if level_up:
                    await context.bot.send_message(
                        user_id,
                        f"🎉 Поздравляем! Вы повысили уровень до {current_level}.\n"
                        f"⚡ Ваши очки опыта: {new_exp} из {required_exp}.\n"
                        f"💰 Ваша новая ставка: {new_rate} RUB.\n\n"
                        f"ℹ️ При достижении 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 уровней Вам доступны уровневые наборы в центре обмена."
                    )

                    # Уведомляем администраторов 2 и 3 уровня
                    admin_ids = [admin_id for admin_id in load_admin_ids() if int(config[admin_id].get('is_admin', '0')) >= 2]
                    for admin_id in admin_ids:
                        await context.bot.send_message(
                            admin_id,
                            f"🅰 Пользователь {user_data['nick']} повысил уровень до {current_level}.\n"
                            f"💰 Новая ставка: {new_rate} RUB."
                        )

            # Уведомление пользователя о подтверждении отчета и начислении баллов
            admin_info = get_user_info(update.effective_user.id)
            admin_position = admin_info.get("position", "Админ")
            admin_nick = admin_info.get("nick", "Админ")
            current_t = 1 * personnel_count
            try:
                await context.bot.send_message(user_id, f"✅ {admin_position} {admin_nick} подтвердил Ваш отчёт (ID: {report_id}). Вам начислено {personnel_count} 🧿 и дополнительно {current_t} ❄️ от праздничной мастерской.")
            except Exception as e:
                logging.error(f"Не удалось уведомить пользователя {user_id} о подтверждении отчета {report_id}: {e}")

            # Уведомление о завершении
            await update.message.reply_text("🅰 Отчёт подтвержден! Вы получили 2 🧿 за модерацию отчёта и дополнительно 5 ❄️ от праздничной мастерской.")
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
                    admin_info = get_user_info(update.effective_user.id)
                    admin_position = admin_info.get("position", "Админ")
                    admin_nick = admin_info.get("nick", "Админ")
                    await context.bot.send_message(user_id, f"❌ {admin_position} {admin_nick} отклонил Ваш отчёт (ID {report_id}). Причина: {reason}")
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
    
    # Обработка обновления
    if 'new_obnova' in context.user_data:
        config = load_accounts()
        user_sections = [sec for sec in config.sections() if sec.isdigit()]
        successes = 0
        for sec in user_sections:
            try:
            # Сначала фото
                with open("obnova.png", "rb") as photo:
                    await context.bot.send_photo(chat_id=int(sec), photo=photo)
                 # Затем текст
                await context.bot.send_message(chat_id=int(sec), text=message_text)
                successes += 1
            except Exception as e:
                logging.error(f"Ошибка при отправке обнова пользователю {sec}: {e}")
        await update.message.reply_text(f"Рассылка обновления завершена. Отправлено {successes} сообщений.")
        context.user_data.pop('new_obnova', None)
        return

    # Вставить в начало handle_text_message, сразу после получения message_text
    if context.user_data.get('awaiting_withdraw_amount'):
        text = message_text.strip().replace(',', '.')
        user_id = update.effective_user.id
        try:
            amount = round(float(text), 2)
        except Exception:
            await update.message.reply_text("❌ Неверный формат суммы. Введите число, например: 1250000")
            return

        if amount <= 0:
            await update.message.reply_text("❌ Введите сумму больше нуля.")
            return

        ctx = context.user_data.get('withdraw_context', {})
        balance = float(ctx.get('balance', 0))
        remaining = float(ctx.get('remaining', 0))
        blimit = int(ctx.get('blimit', 0))
        tlimit = int(ctx.get('tlimit', 0))

        if amount > balance:
            await update.message.reply_text(f"❌ У вас недостаточно средств на балансе. Ваш баланс: {fmt(int(balance))} RUB.")
            return

        if amount > remaining:
            await update.message.reply_text(f"❌ Сумма превышает доступный недельный лимит ({fmt(int(remaining))} RUB). Введите другую сумму.")
            return

        request_id = str(uuid4())[:8]
        remaining_balance = round(balance - amount, 2)
        nick = get_user_info(user_id).get('nick', '')

        context.user_data[user_id] = {
            "request_id": request_id,
            "amount": amount,
            "remaining_balance": remaining_balance,
            "nick": nick
        }

        await save_request(request_id, nick, amount, remaining_balance, user_id, context)

        context.user_data.pop('awaiting_withdraw_amount', None)
        context.user_data.pop('withdraw_context', None)

        keyboard = [
            [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_withdraw")],
            [InlineKeyboardButton("❌ Отменить", callback_data="cancel_withdraw")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"🔔 Подтверждение заявки на вывод\n\n"
            f"👤 Ник: {nick}\n"
            f"💸 Сумма вывода: {amount} RUB\n"
            f"💳 Остаток после вывода: {remaining_balance} RUB\n\n"
            "Если всё верно — нажмите Подтвердить.",
            reply_markup=reply_markup
        )
        return

    # --- 4. Пользователь вводит сумму пополнения ---
    if context.user_data.get("awaiting_deposit_amount"):
        await process_deposit_amount(update, context)
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
    config = load_reports()
    pending_count = len([r for r in config.sections() if config[r].get("status") == "pending"])
    admin_ids_filtered = load_admin_ids()  # Ensure this function returns only admin IDs with levels 2 and 3
    for admin_id in admin_ids_filtered:
        try:
            await context.bot.send_message(
                admin_id,
                f"🅰 Новый отчёт от пользователя {nick} (ID: {report_id}).\n"
                f"⚠ В ожидании проверки: <b>{pending_count}</b> отчёта(ов).\n"
                "Проверьте панель администратора для просмотра.",
                parse_mode="HTML"
            )
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

    # Отправляем фото
    with open("reg.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)

    # Проверяем существующий аккаунт
    if accounts.has_section(str(user_id)):
        await update.message.reply_text("Вы уже зарегистрированы. Для входа используйте кнопку «Авторизация».")
        context.user_data.pop('registration_in_progress', None)
        return ConversationHandler.END

    # Проверяем наличие заявки в registrations.ini
    try:
        config = configparser.ConfigParser()
        config.read(REGISTRATIONS_FILE, encoding="utf-8")
        
        for section in config.sections():
            if str(config[section].get('user_id', '')) == str(user_id):
                await update.message.reply_text(
                    "❌ Ваша заявка уже отправлена и ожидает модерации! Ожидайте решения администратора бота."
                )
                context.user_data.pop('registration_in_progress', None)
                return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text("Произошла ошибка при проверке заявок.")
        return ConversationHandler.END

    # Запускаем регистрацию
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
    ev_level = int(config[reg_id].get('ev_level', '0'))
    lgrating = int(config[reg_id].get('lgrating', '0'))
    daily_rate = get_daily_rate_by_level(level, ev_level, position, lgrating)

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
        'evball': '0',
        'pop': '0',
        'osk': '0',
        'level': '0',
        'exp': '0',
        'lvlconf': '0',
        't': '0',
        'ev_stones': '0',
        'ev_level': '0',
        'lgrating': '0',
        'evball': '0',
        'oosk': '0',
        'uosk': '0',
        'losk': '0',
        'comission': '0'
    }
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        accounts.write(f)

    ensure_user_chars(user_id)

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
                ensure_user_chars(user_id)
                ch_cfg = load_user_chars()
                if not ch_cfg.has_section(user_id):
                     ch_cfg.add_section(user_id)
                ch_cfg[user_id]['exp_multiplier'] = "1.25"  # Повышенная выдача EXP
                ch_cfg[user_id]['max_zp'] = "1"            # Разрешение свободного вывода средств
                save_user_chars(ch_cfg)
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
        await query.message.edit_text(
            f"Предупреждение добавлено. Теперь предупреждений: {warnings}.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]])
        )
        user_info = get_user_info(user_id)

        # Отправка фото пользователю
        try:
            with open("warn.png", "rb") as photo:
                await context.bot.send_photo(chat_id=int(user_id), photo=photo)
        except Exception:
            pass  # Если файла нет — игнорируем

        await context.bot.send_message(
            user_id,
            f"⚠️ Вам выдано предупреждение. Теперь у вас {warnings} предупреждений."
        )
        await context.bot.send_message(
            admin_ids[0],
            f"⚠️ Пользователю {user_info['nick']} выдано предупреждение. Теперь у него {warnings} предупреждений."
        )
    else:
        await query.message.edit_text(
            "Ошибка: Пользователь не найден.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]])
        )

async def remove_warning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = context.user_data.get('user_id')
    config = load_accounts()
    if config.has_section(user_id):
        warnings = max(0, int(config[user_id].get('warnings', '0')) - 1)
        config[user_id]['warnings'] = str(warnings)
        save_accounts(config)
        await query.message.edit_text(
            f"Предупреждение снято. Теперь предупреждений: {warnings}.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]])
        )
        user_info = get_user_info(user_id)

        # Отправка фото пользователю
        try:
            with open("warn.png", "rb") as photo:
                await context.bot.send_photo(chat_id=int(user_id), photo=photo)
        except Exception:
            pass  # Если файла нет — игнорируем

        await context.bot.send_message(
            user_id,
            f"✅ С вас снято предупреждение. Теперь у вас {warnings} предупреждений."
        )
        await context.bot.send_message(
            admin_ids[0],
            f"✅ С пользователя {user_info['nick']} снято предупреждение. Теперь у него {warnings} предупреждений."
        )
    else:
        await query.message.edit_text(
            "Ошибка: Пользователь не найден.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data=f"edit_user_{user_id}")]])
        )

 
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
        ev_level = int(user_info.get('ev_level', '0'))
        current_exp = int(user_info.get('exp', '0'))
        required_exp = 350 + (current_level * 7)
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
            f"🧧 Эволюция: {ev_level}\n"
            f"⚡ Очки опыта: {current_exp} из {required_exp}\n"
            f"🔥 Респекты: {user_info['ev_stones']}\n"
            f"💰 Ставка за монету: {daily_rate_formatted} RUB\n"
            f"⚠️ Предупреждения: {user_info['warnings']}\n"
            f"🧿 Монеты активности: {user_info['ball']}\n"
            f"🪙 Монеты эволюции: {user_info['evball']}\n"
            f"💈 Бусты: {user_info['osk']}\n"
            f"❄️ Снежинки: {user_info['t']}\n"
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
            ev_level = int(config[section].get('ev_level', '0'))  # Получаем уровень пользователя
            position = config[section].get('position', '')  # <-- вот эта строка
            lgrating = int(config[section].get('lgrating', '0'))
            
            daily_rate = get_daily_rate_by_level(level, ev_level, position, lgrating)
            salary = ball * daily_rate * (1 - 0.25 * warnings)  # Формула расчёта зарплаты
            salary = int(salary)  # Округляем до целого числа
            
            current_account = int(config[section].get('personal_account', '0'))
            new_account = current_account + salary
            config[section]['personal_account'] = str(new_account)
            config[section]['ball'] = "0"  # Обнуляем монеты активности
            
            nick = config[section].get('nick', 'Неизвестный')
            notifications.append((int(section), nick, salary))
    
    save_accounts(config)
    # Сбрасываем tlimit всех пользователей
    try:
        reset_all_tlimits()
    except Exception as e:
        logging.error(f"Ошибка при сбросе недельных лимитов: {e}")
    
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

    promo_code = context.args[0].strip().lower()  # приводим промокод к нижнему регистру и убираем пробелы

    logging.info(f"Пользователь ввёл промокод: {promo_code}")

    # Чтение файла промокодов
    promo_config = configparser.ConfigParser()
    promo_config.optionxform = str  # Отключаем автоматическое изменение регистра (опционов)
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

    # Проверка на использование промокода (используем оригинальное имя секции!)
    activation_config = configparser.ConfigParser()
    try:
        activation_config.read(PROMO_ACTIVATIONS_FILE, encoding="utf-8")
    except Exception as e:
        logging.error(f"Ошибка чтения файла активаций промокодов: {e}")
        await update.message.reply_text("❌ Произошла ошибка при доступе к истории активаций.")
        return

    # Сравниваем с оригинальным именем секции — так, как вы его записываете в файл активаций
    if activation_config.has_section(str(user_id)) and original_promo_code in activation_config[str(user_id)]:
        await update.message.reply_text("❌ Вы уже активировали этот промокод.")
        return

    # Получаем данные промокода
    promo_data = promo_config[original_promo_code]

    # Начисление бонусов
    ball_bonus = int(promo_data.get('ball', 0))
    money_bonus = int(promo_data.get('money', 0))
    exp_bonus = int(promo_data.get('exp', 0))
    shards_bonus = int(promo_data.get('shards', 0))  # Новый параметр для осколков
    t_bonus = int(promo_data.get('t', 0))
    ev_stones_bonus = int(promo_data.get('ev_stones', 0))
    evball_bonus = int(promo_data.get('evball', 0))
    
    config = load_accounts()
    if config.has_section(str(user_id)):
        user_section = config[str(user_id)]
        user_section['ball'] = str(int(user_section.get('ball', '0')) + ball_bonus)
        user_section['personal_account'] = str(int(user_section.get('personal_account', '0')) + money_bonus)
        user_section['exp'] = str(int(user_section.get('exp', '0')) + exp_bonus)
        user_section['osk'] = str(int(user_section.get('osk', '0')) + shards_bonus)  # Добавляем осколки
        user_section['t'] = str(int(user_section.get('t', '0')) + t_bonus)
        user_section['ev_stones'] = str(int(user_section.get('ev_stones', '0')) + ev_stones_bonus)
        user_section['evball'] = str(int(user_section.get('evball', '0')) + evball_bonus)
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

    # Формируем сообщение для пользователя (маленькая правка: перенос строки между строками)
    message = "✅ Промокод успешно активирован!\n"
    if ball_bonus > 0:
        message += f"🧿 Монеты активности: {ball_bonus}\n"
    if money_bonus > 0:
        message += f"💰 Деньги: {money_bonus} RUB\n"
    if exp_bonus > 0:
        message += f"⚡ EXP: {exp_bonus}\n"
    if shards_bonus > 0:
        message += f"💈 Бусты: {shards_bonus}\n"
    if t_bonus > 0:
        message += f"❄️ Снежинки: {t_bonus}\n"
    if ev_stones_bonus > 0:
        message += f"🔥 Респекты: {ev_stones_bonus}\n"
    if evball_bonus > 0:
        message += f"🪙 Монеты эволюции: {evball_bonus}"

    await update.message.reply_text(message)

    # Уведомление только админам 3 уровня (is_admin == 3)
    try:
        accounts_cfg = load_accounts()
        admin_level_3_ids = []
        for sec in accounts_cfg.sections():
            if not sec.isdigit():
                continue
            try:
                if int(accounts_cfg[sec].get('is_admin', '0')) == 3:
                    admin_level_3_ids.append(int(sec))
            except ValueError:
                continue

        for admin_id in admin_level_3_ids:
            try:
                await context.bot.send_message(
                    admin_id,
                    f"🅰 Пользователь {user_info.get('nick','<no-nick>')} активировал промокод {original_promo_code}.\n"
                    f"🧿 Монеты активности: {ball_bonus}\n"
                    f"💰 Деньги: {money_bonus} RUB\n"
                    f"⚡ EXP: {exp_bonus}\n"
                    f"❄️ Снежинки: {t_bonus}\n"
                    f"💈 Бусты: {shards_bonus}\n"
                    f"🔥 Респекты: {ev_stones_bonus}\n"
                    f"🪙 Монеты эволюции: {evball_bonus}"
                )
            except Exception as e:
                logging.error(f"Ошибка при отправке уведомления админу {admin_id}: {e}")
    except Exception as e:
        logging.error(f"Ошибка при попытке уведомить админов уровня 3: {e}")

async def setpromocode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    
    # Проверка прав администратора
    if int(user_info.get('is_admin', 0)) < 3:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    # Проверка аргументов
    if len(context.args) != 8:
        await update.message.reply_text(
            "❌ Неверный формат команды. Используйте: /setpromocode [PROMO] [ball] [money] [exp] [shards] [tikvi] [ev_stones] [evball]"
        )
        return
    
    promo_code, ball, money, exp, shards, t, ev_stones, evball = context.args
    try:
        ball = int(ball)
        money = int(money)
        exp = int(exp)
        shards = int(shards)  # Новый параметр для осколков
        t = int(t)
        ev_stones = int(ev_stones)
        evball = int(evball)
        
    except ValueError:
        await update.message.reply_text("❌ Все бонусы (монеты активности, деньги, EXP, бусты, снежинки, респекты, монеты эволюции) должны быть целыми числами.")
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
    promo_config[promo_code]['t'] = str(t)
    promo_config[promo_code]['ev_stones'] = str(ev_stones)
    promo_config[promo_code]['evball'] = str(evball)
    
    with open(PROMO_FILE, "w", encoding="utf-8") as f:
        promo_config.write(f)
    
    # Уведомление пользователя
    await update.message.reply_text(
        f"✅ Промокод {promo_code} успешно создан!\n"
        f"🧿 Монеты активности: {ball}\n"
        f"💰 Деньги: {money} RUB\n"
        f"⚡ EXP: {exp}\n"
        f"💈 Бусты: {shards}\n"
        f"❄️ Снежинки: {t}\n"
        f"🔥 Респекты: {ev_stones}\n"
        f"🪙 Монеты эволюции: {evball}"
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
    if len(context.args) < 8:
        await update.message.reply_text(
            "❌ Неверный формат команды. Используйте: /send <никнейм> <монеты активности> <бусты> <опыт> <снежинки> <деньги> <респекты> <монеты эволюции>"
        )
        return

    # Извлекаем никнейм, монеты активности, осколки, опыт и деньги из аргументов
    *nick_parts, activity_coins, shards, exp, t, money, ev_stones, evball = context.args
    target_nick = " ".join(nick_parts)  # Объединяем части никнейма с пробелами

    try:
        activity_coins = int(activity_coins)
        shards = int(shards)
        exp = int(exp)
        t = int(t)
        money = int(money)
        ev_stones = int(ev_stones)
        evball = int(evball)
    except ValueError:
        await update.message.reply_text(
            "❌ Количество монет активности, бустов, опыта, денег, респектов и монет эволюции должно быть числом."
        )
        return

    # Проверка на положительные значения (включаем все валюты)
    if any(v < 0 for v in (activity_coins, shards, exp, t, money, ev_stones, evball)):
        await update.message.reply_text(
            "❌ Количество монет активности, бустов, опыта, снежинок, денег, респектов и монет эволюции должно быть положительным числом."
        )
        return

    # Базовая комиссия в процентах
    BASE_COMMISSION = 10

    # Получение информации об отправителе
    sender_id = str(update.effective_user.id)
    accounts = load_accounts()

    if not accounts.has_section(sender_id):
        await update.message.reply_text("❌ Ошибка: информация о вашем аккаунте не найдена.")
        return

    sender_info = accounts[sender_id]
    # 🏚 Проверка Торговой избы Бабы Яги
    izba_state = sender_info.get("izbayagi", "0")
    izba_active = izba_state == "2"
    sender_activity_coins = int(sender_info.get("ball", 0))
    sender_shards = int(sender_info.get("osk", 0))
    sender_exp = int(sender_info.get("exp", 0))
    sender_t = int(sender_info.get("t", 0))
    sender_personal_account = int(sender_info.get("personal_account", 0))
    sender_ev_stones = int(sender_info.get("ev_stones", 0))
    sender_evball = int(sender_info.get("evball", 0))

    # Read sender commission reduction (field name 'comission' as you used)
    try:
        sender_comission_reduction = int(sender_info.get("comission", 0))
    except ValueError:
        sender_comission_reduction = 0
    # Clamp 0..BASE_COMMISSION
    sender_comission_reduction = max(0, min(BASE_COMMISSION, sender_comission_reduction))
    sender_comm_pct = max(0, BASE_COMMISSION - sender_comission_reduction)
    # 🏚 Активная изба Бабы Яги — комиссия 0%
    if izba_active:
        sender_comm_pct = 0

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

    recipient_info = accounts[recipient_id]
    recipient_activity_coins = int(recipient_info.get("ball", 0))
    recipient_shards = int(recipient_info.get("osk", 0))
    recipient_exp = int(recipient_info.get("exp", 0))
    recipient_t = int(recipient_info.get("t", 0))
    recipient_personal_account = int(recipient_info.get("personal_account", 0))
    recipient_ev_stones = int(recipient_info.get("ev_stones", 0))
    recipient_evball = int(recipient_info.get("evball", 0))

    # Read recipient commission reduction
    try:
        recipient_comission_reduction = int(recipient_info.get("comission", 0))
    except ValueError:
        recipient_comission_reduction = 0
    recipient_comission_reduction = max(0, min(BASE_COMMISSION, recipient_comission_reduction))
    recipient_comm_pct = max(0, BASE_COMMISSION - recipient_comission_reduction)

    # Helper to compute fees (rounding: commission amounts округляются "в большую сторону" => math.ceil)
    def fee_amount(amount: int, pct: int) -> int:
        if amount <= 0 or pct <= 0:
            return 0
        return math.ceil(amount * pct / 100.0)

    # Для каждой валюты считаем необходимые комиссии и итоговые суммы для проверки баланса
    # Sender must cover: amount + sender_fee
    # Recipient receives: amount - recipient_fee (may be 0)
    # We will collect fees per-currency to show in message / admins
    currencies = [
        ("🧿 Монеты активности", activity_coins, "ball"),
        ("💈 Бусты", shards, "osk"),
        ("⚡️ Опыт", exp, "exp"),
        ("❄️ Снежинки", t, "t"),
        ("💳 Деньги", money, "personal_account"),
        ("🔥 Респекты", ev_stones, "ev_stones"),
        ("🪙 Монеты эволюции", evball, "evball"),
    ]

    # current balances dict for sender to check generically
    sender_balances = {
        "ball": sender_activity_coins,
        "osk": sender_shards,
        "exp": sender_exp,
        "t": sender_t,
        "personal_account": sender_personal_account,
        "ev_stones": sender_ev_stones,
        "evball": sender_evball,
    }

    recipient_balances = {
        "ball": recipient_activity_coins,
        "osk": recipient_shards,
        "exp": recipient_exp,
        "t": recipient_t,
        "personal_account": recipient_personal_account,
        "ev_stones": recipient_ev_stones,
        "evball": recipient_evball,
    }

    # Accumulate computed numbers
    computed = []
    for label, amount, key in currencies:
        s_fee = fee_amount(amount, sender_comm_pct)  # sender pays this extra
        r_fee = fee_amount(amount, recipient_comm_pct)  # recipient loses this
        sender_total_needed = amount + s_fee
        recipient_gets = max(0, amount - r_fee)  # ensure non-negative
        computed.append({
            "label": label,
            "key": key,
            "amount": amount,
            "sender_fee": s_fee,
            "recipient_fee": r_fee,
            "sender_total_needed": sender_total_needed,
            "recipient_gets": recipient_gets,
        })

    # Проверка, хватает ли ресурсов у отправителя (для каждой валюты)
    insufficient_msgs = []
    for item in computed:
        key = item["key"]
        need = item["sender_total_needed"]
        if sender_balances.get(key, 0) < need:
            insufficient_msgs.append(f"❌ У вас недостаточно {item['label']} для перевода (нужно {need}, доступно {sender_balances.get(key,0)}).")

    if insufficient_msgs:
        # Отправляем первое сообщение (или все) — соберём все ошибки в одно
        await update.message.reply_text("\n".join(insufficient_msgs))
        return

    # 🎲 Шанс Бабы Яги (10%) — ресурсы уходят в избу
    if izba_active and random.random() < 0.10:
        BABA_YAGA_ID = "999999999"  # системный аккаунт Бабы Яги

        if not accounts.has_section(BABA_YAGA_ID):
            accounts.add_section(BABA_YAGA_ID)

        baba = accounts[BABA_YAGA_ID]

        # Инициализация полей
        for key in sender_balances.keys():
            baba.setdefault(key, "0")

        # Списываем ресурсы у отправителя и передаём Бабе Яге
        for item in computed:
            key = item["key"]
            amt = item["amount"]
            sender_info[key] = str(sender_balances[key] - amt)
            baba[key] = str(int(baba[key]) + amt)

        save_accounts(accounts)

        await update.message.reply_text(
            "☠️ <b>Баба Яга вмешалась в сделку!</b>\n\n"
            "🏚 Торговая изба забрала все ресурсы.\n"
            "Получатель ничего не получил.",
            parse_mode="HTML"
        )
        return

    # Выполняем списание и зачисление
    # Update sender_info and recipient_info fields (strings)
    for item in computed:
        key = item["key"]
        amt = item["amount"]
        s_fee = item["sender_fee"]
        r_get = item["recipient_gets"]

        # Update sender
        new_sender_value = sender_balances[key] - (amt + s_fee)
        sender_info[key] = str(new_sender_value)
        # Update recipient
        new_recipient_value = recipient_balances[key] + r_get
        recipient_info[key] = str(new_recipient_value)

    # Сохранение изменений в accounts.ini
    save_accounts(accounts)

    # Построение сообщения отправителю с деталями комиссий
    sender_lines = ["✅ Вы успешно выполнили перевод:"]
    for item in computed:
        if item["amount"] == 0:
            continue  # не показываем нулевые переводы
        sender_lines.append(
            f"{item['label']}: отправлено {item['amount']}, комиссия отправителя +{item['sender_fee']}, комиссия получателя -{item['recipient_fee']}, получатель получит {item['recipient_gets']}\n"
        )
    sender_lines.append(f"Комиссия базовая: {BASE_COMMISSION}%. Ваша скидка: {sender_comission_reduction}%, итоговая для вас: {sender_comm_pct}%. Получатель имеет скидку: {recipient_comission_reduction}%, итоговая для получателя: {recipient_comm_pct}%.")

    await update.message.reply_text("\n".join(sender_lines))

    # Уведомление получателя
    try:
        recipient_msg_lines = [
            f"💱 Вы получили перевод от {sender_info.get('nick', 'Неизвестно')}!",
            ""
        ]
        for item in computed:
            if item["amount"] == 0:
                continue
            recipient_msg_lines.append(
                f"{item['label']}: от {item['amount']} вы получили {item['recipient_gets']} (списано комиссии {item['recipient_fee']})\n"
            )
        recipient_msg_lines.append(f"Комиссия базовая: {BASE_COMMISSION}%. Ваша скидка: {recipient_comission_reduction}%, итоговая для получателя: {recipient_comm_pct}%.")

        await context.bot.send_message(
            chat_id=int(recipient_id),
            text="\n".join(recipient_msg_lines),
        )
    except Exception as e:
        logging.error(f"Ошибка при уведомлении пользователя {recipient_id}: {e}")

    # Уведомление администраторов 2 уровня и выше (включаем информацию о комиссиях)
    for section in accounts.sections():
        try:
            admin_level = int(accounts[section].get("is_admin", 0))
        except Exception:
            admin_level = 0
        if admin_level >= 2:  # Проверка уровня администратора
            try:
                admin_lines = [
                    f"🅰 Уведомление о переводе.",
                    f"👤 Отправитель: {sender_info.get('nick', 'Неизвестно')} (id {sender_id})",
                    f"👤 Получатель: {recipient_info.get('nick', 'Неизвестно')} (id {recipient_id})",
                    ""
                ]
                for item in computed:
                    if item["amount"] == 0:
                        continue
                    admin_lines.append(
                        f"{item['label']}: отправлено {item['amount']}, списано с отправителя (включая комиссию) {item['sender_total_needed']}, комиссия отправителя {item['sender_fee']}, получатель получил {item['recipient_gets']}, комиссия получателя {item['recipient_fee']}\n"
                    )
                admin_lines.append(f"Комиссия базовая: {BASE_COMMISSION}%. Скидка отправителя: {sender_comission_reduction}%, итоговая для отправителя: {sender_comm_pct}%. Скидка получателя: {recipient_comission_reduction}%, итоговая для получателя: {recipient_comm_pct}%.")

                await context.bot.send_message(
                    chat_id=int(section),
                    text="\n".join(admin_lines),
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
            "ev_stones": int(data.get("ev_stones", 0)),
            "money": int(data.get("money", 0)),
            "t": int(data.get("t", 0)),
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
    sec["ev_stones"] = str(int(sec.get("ev_stones", 0)) + set_data["ev_stones"])
    sec["t"] = str(int(sec.get("t", 0)) + set_data["t"])
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
        f"🔥 ➕ {set_data['ev_stones']} респектов\n"
        f"❄️ ➕ {set_data['t']} снежинок\n"
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
           f"🧿 ➕{set_data['ball']} | ⚡ ➕{set_data['exp']} | 🔥 ➕{set_data['ev_stones']} | 💳 ➕{set_data['money']} RUB | ❄️ ➕{set_data['t']} снежинок\n"
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

def get_main_exchange_keyboard(user_id=None):
    user_info = get_user_info(user_id) if user_id else None
    position = user_info.get("position", "") if user_info else ""

    keyboard = [
        [KeyboardButton("Наборы")],
        [KeyboardButton("Функции")],
        [KeyboardButton("Эволавка")],
        [KeyboardButton("Назад")]
    ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_main_nabors_keyboard():
    keyboard = [
        [KeyboardButton("Обычные наборы")],
        [KeyboardButton("Ресурсные наборы")],
        [KeyboardButton("Уровневые наборы")],
        [KeyboardButton("Лимитированные наборы")],
        [KeyboardButton("Назад в центр обмена")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_main_finance():
    keyboard = [
        [KeyboardButton("Пополнение счёта")],
        [KeyboardButton("Вывод средств")],
        [KeyboardButton("Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def get_main_function(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("Подтверждение уровня")],
        [KeyboardButton("Снятие предупреждения")],
        [KeyboardButton("Эволюция")],
        [KeyboardButton("Назад в центр обмена")]
    ]
    await update.message.reply_text("Выберите функцию:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

def get_back_to_exchange_keyboard():
    # Кнопка Назад, возвращающая в центр обмена
    keyboard = [[KeyboardButton("Назад в центр обмена")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_to_function_keyboard():
    # Кнопка Назад, возвращающая в меню функций
    keyboard = [[KeyboardButton("Назад в меню выбора функций")]]
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
    await update.message.reply_text(message, reply_markup=get_main_exchange_keyboard(update.effective_user.id), parse_mode="HTML")

async def usual_sets(update, context):
    with open("nabor.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    message = (
        f"🎁 <b>Обычные наборы.</b>\n\n"
        f"💼 <b>Рейтинговый набор максимальный (300 💈):</b>\n"
        f"В набор входит: 200 🧿 350 ⚡ 50КК 💳\n"
        f"Для покупки введите <code>/buyn 1</code>\n\n"
        f"🕶 <b>Рейтинговый набор средний (150 💈):</b>\n"
        f"В набор входит: 100 🧿 175 ⚡ 25КК 💳\n"
        f"Для покупки введите <code>/buyn 2</code>\n\n"
        f"🧸 <b>Рейтинговый набор минимальный (75 💈):</b>\n"
        f"В набор входит: 50 🧿 100 ⚡ 10КК 💳\n"
        f"Для покупки введите <code>/buyn 3</code>\n\n"
    )
    await update.message.reply_text(message, reply_markup=get_back_to_nabors_keyboard(), parse_mode="HTML")
    
async def seasonal_sets(update, context):
    with open("nabor.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    message = (
        f"🧱 <b>Ресурсные наборы.</b>\n\n"
        f"💳 <b>Денежный набор (50 💈):</b>\n"
        f"В набор входит: 25КК 💳\n"
        f"Для покупки введите <code>/buyn 4</code>\n\n"
        f"🧿 <b>Монетный набор (50 💈):</b>\n"
        f"В набор входит: 50 🧿\n"
        f"Для покупки введите <code>/buyn 5</code>\n\n"
        f"⚡ <b>Набор опыта (50 💈):</b>\n"
        f"В набор входит: 250 ⚡\n"
        f"Для покупки введите <code>/buyn 6</code>\n\n"
        f"🔥 <b>Набор респектов (50 💈):</b>\n"
        f"В набор входит: 25 🔥\n"
        f"Для покупки введите <code>/buyn 18</code>\n\n"
    )
    await update.message.reply_text(message, reply_markup=get_back_to_nabors_keyboard(), parse_mode="HTML")

def _int_safe(value, default=0) -> int:
    try:
        return int(float(value))
    except Exception:
        return int(default)


def _now_msk() -> datetime:
    # текущее время в MSK (UTC+3)
    return datetime.now(tz=timezone.utc).astimezone(timezone(timedelta(hours=3)))


async def limited_sets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
            "⏳ Лимитированных наборов нет в наличии.\n"
            "Ожидайте пополнения, а после выхода покупайте самые выгодные наборы в боте."
        )
    return
    with open("limitki.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    """
    Меню лимитированных наборов (только команды /buys и /buyt)
    """
    cfg_sets = load_limited_sets_cfg()
    light_total = _int_safe(cfg_sets["light"].get("total", LIMITED_SET_TOTAL))
    light_sold = _int_safe(cfg_sets["light"].get("sold", 0))
    dark_total = _int_safe(cfg_sets["dark"].get("total", LIMITED_SET_TOTAL))
    dark_sold = _int_safe(cfg_sets["dark"].get("sold", 0))

    text_light = (
        f"💎 <b>Лимитированные наборы.</b>\n\n"
        "🎄 <b>Светлый набор (50 💈)</b>\n"
        f"Наличие: {light_total - light_sold} из {light_total} штук.\n"
        "В наборе: 25 📒 50 📕 50 🔥 250 ❄️\n"
        "При покупке могут выпасть новейшие модули и предметы светлой стороны.\n"
        "Введите для покупки: /buys"
    )

    text_dark = (
        "🖤 <b>Тёмный набор (50 💈)</b>\n"
        f"Наличие: {dark_total - dark_sold} из {dark_total} шт.\n"
        "В наборе: 25 📒 50 📕 50 🔥 250 ❄️\n"
        "При покупке могут выпасть новейшие модули и предметы тёмной стороны.\n"
        "Введите для покупки: /buyt"
    )

    info = (
        f"{text_light}\n\n{text_dark}\n\n"
        "⏳ <i>Важно: наборы доступны с 21.12.2025 18:00 МСК - покупка доступна только для пользователей, у которых выбрана сторона (светлая или тёмная) в Крафтинг -> Праздничный крафт.</i>"
    )

    await update.message.reply_text(info, reply_markup=get_back_to_nabors_keyboard(), parse_mode="HTML")


async def buys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _process_purchase(update, context, "light")


async def buyt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _process_purchase(update, context, "dark")


async def _process_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE, which: str):
    """
    which: 'light' or 'dark'
    """
    user = update.effective_user
    if user is None:
        return

    uid = user.id
    uid_str = str(uid)

    # load limited sets
    cfg_sets = load_limited_sets_cfg()
    sec = cfg_sets[which]
    total = _int_safe(sec.get("total", LIMITED_SET_TOTAL))
    sold = _int_safe(sec.get("sold", 0))
    remaining = total - sold
    if remaining <= 0:
        await update.message.reply_text("❌ Извините, лимитированные наборы этого типа закончились.")
        return

    # check date / side
    now = _now_msk()
    release = LIMITED_SETS_RELEASE_MSK
    if now < release:
        await update.message.reply_text(
            "⏳ Покупки лимитированных наборов временно закрыты для всех.\n"
            "Доступ откроется 21.12.2025 18:00 МСК."
        )
        return

    user_side = get_user_side_normalized(uid)
    if not user_side:
        await update.message.reply_text(
            "❌ У вас не выбрана сторона. Чтобы купить лимитированные наборы, "
            "выберите сторону в мастерской (праздничные крафты) — свет или тьма."
        )
        return

    if user_side != which:
        await update.message.reply_text(
            "❌ Нельзя открыть этот набор — у вас выбрана другая сторона."
        )
        return

    # load accounts
    cfg_accounts = load_accounts_cfg()
    _ensure_user_section_accounts(cfg_accounts, uid_str)

    cur_boosts = _get_account_number(cfg_accounts, uid_str, BOOST_FIELD)
    cost = SET_COST
    if cur_boosts < cost:
        await update.message.reply_text("❌ Недостаточно бустов. Требуется 50 бустов.")
        return

    # Списание бустов
    cfg_accounts[uid_str][BOOST_FIELD] = str(cur_boosts - cost)

    # Начисление стандартного набора
    _add_to_account_field(cfg_accounts, uid_str, RESOURCE_LOSK, 25)
    _add_to_account_field(cfg_accounts, uid_str, RESOURCE_UOSK, 50)
    _add_to_account_field(cfg_accounts, uid_str, RESOURCE_EV_STONES, 50)
    _add_to_account_field(cfg_accounts, uid_str, RESOURCE_T, 250)

    # Рандомные бонусы
    bonuses_gotten: List[Tuple[str, float]] = []

    def roll(pct: float) -> bool:
        return random.random() * 100.0 < float(pct)

    if which == "dark":
        for key, pct in DARK_BONUS_KEYS:
            if roll(pct):
                cfg_accounts[uid_str][key] = "1"
                bonuses_gotten.append((key, pct))
    else:
        for key, pct in LIGHT_BONUS_KEYS:
            if roll(pct):
                cfg_accounts[uid_str][key] = "1"
                bonuses_gotten.append((key, pct))

    # сохранить accounts и увеличить sold
    save_accounts_cfg(cfg_accounts)

    sec["sold"] = str(sold + 1)
    save_limited_sets_cfg(cfg_sets)

    # Формируем сообщение пользователю
    if which == "light":
        header = "🎄 Вы купили [LIMITED] Светлый набор."
        style_text = "✨ Новогодняя радость — всё светлое и праздничное."
    else:
        header = "🖤 Вы купили [LIMITED] Тёмный набор."
        style_text = "🌑 Мрачная сила впадает в вас..."

    got_text = (
        f"{header}\n"
        f"{style_text}\n"
        f"Вы получили:\n"
        f"25 📒 50 📕 50 🔥 250 ❄️\n"
    )

    if bonuses_gotten:
        got_text += "🎁 Бонусы, что выпали:\n"
        for k, pct in bonuses_gotten:
            got_text += f"- {module_pretty_name(k)} — шанс {pct}%\n"
    else:
        got_text += "Бонусы: ничего не выпало в этот раз.\n"

    got_text += f"Наличие осталось: {int(sec['total']) - int(sec['sold'])} из {sec['total']}."

    await update.message.reply_text(got_text, parse_mode="HTML")

    # --- Уведомление только админам 3 уровня ---
    try:
        admin_level_3_ids = []

        for section in cfg_accounts.sections():
            if not section.isdigit():
                continue
            try:
                if int(cfg_accounts[section].get("is_admin", "0")) == 3:
                    admin_level_3_ids.append(int(section))
            except ValueError:
                continue

        if admin_level_3_ids:
            if bonuses_gotten:
                admin_bonuses = ", ".join(
                    module_pretty_name(k) for k, _ in bonuses_gotten
                )
            else:
                admin_bonuses = "нет"

            username = f"@{user.username}" if user.username else user.full_name

            for admin_id in admin_level_3_ids:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=(
                            f"🅰 <b>Покупка лимитированного набора</b>\n"
                            f"👤 Пользователь: {uid} — {username}\n"
                            f"📦 Набор: {'Светлый' if which == 'light' else 'Тёмный'} за 50 💈\n"
                            f"🎁 Бонусы: {admin_bonuses}"
                        ),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logging.error(
                        f"Ошибка при отправке уведомления админу {admin_id}: {e}"
                    )

    except Exception as e:
        logging.error(
            f"Ошибка при попытке уведомить админов уровня 3: {e}"
        )

async def lvl_sets(update, context):
    with open("nabor.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    message = (
        f"🗽 <b>Уровневые наборы.</b>\n\n"
        f"👑 <b>Набор за 100 уровень (ID: 17)</b>\n"
        f"Состав: 500 🧿 100 🔥 100КК 💳\n\n"
        f"💎 <b>Набор за 90 уровень (ID: 16)</b>\n"
        f"Состав: 450 🧿 90 🔥 90КК 💳\n\n"
        f"🌟 <b>Набор за 80 уровень (ID: 15)</b>\n"
        f"Состав: 400 🧿 80 🔥 80КК 💳\n\n"
        f"⭐ <b>Набор за 70 уровень (ID: 14)</b>\n"
        f"Состав: 350 🧿 70 🔥 70КК 💳\n\n"
        f"💼 <b>Набор за 60 уровень (ID: 13)</b>\n"
        f"Состав: 300 🧿 60 🔥 60КК 💳\n\n"
        f"🚬 <b>Набор за 50 уровень (ID: 12)</b>\n"
        f"Состав: 250 🧿 50 🔥 50КК 💳\n\n"
        f"🍹 <b>Набор за 40 уровень (ID: 11)</b>\n"
        f"Состав: 200 🧿 40 🔥 40КК 💳\n\n"
        f"🕶 <b>Набор за 30 уровень (ID: 10)</b>\n"
        f"Состав: 150 🧿 30 🔥 30КК 💳\n\n"
        f"🦾 <b>Набор за 20 уровень (ID: 9)</b>\n"
        f"Состав: 100 🧿 20 🔥 20КК 💳\n\n"
        f"🎓 <b>Набор за 10 уровень (ID: 8)</b>\n"
        f"Состав: 50 🧿 10 🔥 10КК 💳\n\n"
        f"<i>Наборы предоставляются бесплатно, свяжитесь с лидером семьи при достижении уровня для получения доступа к набору, а после введите /buyn [ID набора].</i>\n\n"
    )
    await update.message.reply_text(message, reply_markup=get_back_to_nabors_keyboard(), parse_mode="HTML")
    
async def characteristics(update, context):
    user_id = str(update.effective_user.id)
    user_info = get_user_info(user_id)

    current_ev_level = int(user_info.get("ev_level", 0)) if user_info else 0
    if current_ev_level <= 0:
        await update.message.reply_text(
            "⛔ У вас нет доступа к эволавке, доступ открыт только у пользователей с эволюцией."
        )
        return

    accounts_cfg = load_accounts()
    craft_cfg = load_craft_items()

    # бонус крафта
    craftup = 0
    if accounts_cfg.has_section(user_id):
        try:
            craftup = int(accounts_cfg[user_id].get("craftup", 0))
        except Exception:
            craftup = 0

    def get_final_chance(recipe_id: str) -> int:
        if craft_cfg.has_section(recipe_id):
            try:
                base = int(craft_cfg[recipe_id].get("chance", 0))
            except Exception:
                base = 0
            return min(100, base + craftup)
        return 0

    # Фото
    try:
        with open("evolavka.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
    except FileNotFoundError:
        pass

    message = (
        "🕌 <b>Эволавка.</b>\n"
        "🧧‍ <b>У вас есть доступ к эволавке.</b>\n"
        f"🎟 Ваш уровень эволюции: <b>{current_ev_level}</b>\n\n"

        "⛩️ <b>Наборы.</b>\n"
        "🌍 <b>Эвонабор максимальный (500К 🪙):</b>\n"
        "В набор входит: 1000 🧿 1000 ⚡ 100КК 💳\n\n"

        "🕋 <b>Эвонабор средний (250К 🪙):</b>\n"
        "В набор входит: 500 🧿 500 ⚡ 50КК 💳\n\n"

        "⛲ <b>Эвонабор минимальный (125К 🪙):</b>\n"
        "В набор входит: 250 🧿 250 ⚡ 25КК 💳\n\n"

        "🏰 <b>Крафты.</b>\n"
        f"🧾 <b>Грамота хранителя (📟 шанс — {get_final_chance('15')}%):</b>\n"
        "🧱 Требование: 25 📒 25 🔥 50К 🪙 50 💈\n"
        "Информация о предмете <code>/craft info 15</code>\n"
        "Для крафта введите <code>/craft 15</code>\n\n"

        "<i>Предметы эволавки уникальны, для покупки свяжитесь с лидером семьи.</i>"
    )

    await update.message.reply_text(
        message,
        reply_markup=get_back_to_exchange_keyboard(),
        parse_mode="HTML"
    )


async def pod(update, context):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    current_level = int(user_info.get('level', 0)) if user_info else 0
    lvlconf = int(user_info.get('lvlconf', 0)) if user_info else 0
    ev_level = int(user_info.get('ev_level', 0)) if user_info else 0

    # Если пользователь эволюционировал — подтверждение бесплатно
    confirm_status = "☑️ Не требуется" if lvlconf == 0 else "❗️ Требуется"

    # Словарь стоимости подтверждения по уровням
    confirm_costs = {10: 50, 20: 100, 30: 150, 40: 200, 50: 250, 60: 300, 70: 350, 80: 400, 90: 450, 100: 500}

    # Определение стоимости для текущего уровня
    if ev_level > 0:
        cost_str = "🔔 Стоимость подтверждения: <b>бесплатно (эволюционные льготы)</b>\n"
    else:
        if current_level in confirm_costs:
            cost_str = f"🔔 Стоимость подтверждения: <b>{confirm_costs[current_level]} 💈</b>\n"
        else:
            cost_str = ""

    try:
        with open("pod.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
    except Exception:
        pass

    message = (
        f"☑️ <b>Подтверждение уровня.</b>\n"
        f"Ваш текущий уровень: <b>{current_level}</b>\n"
        f"Статус подтверждения: <b>{confirm_status}</b>\n"
        f"{cost_str}"
        f"Подтверждение уровня — это сохранение ранжировки уровня путем оплаты.\n\n"
        f"☑ Для подтверждения уровня введите команду <code>/lvlconf</code>\n"
        f"❌ Во время подтверждения уровня <b>заблокирована система отчётов</b>.\n\n"
    )
    await update.message.reply_text(message, reply_markup=get_back_to_function_keyboard(), parse_mode="HTML")

# Оповещение всех пользователей (функция уже есть в коде)
async def notify_all_users(context, text, parse_mode="HTML"):
    config = load_accounts()
    for user_id in config.sections():
        if user_id.isdigit():
            try:
                await context.bot.send_message(chat_id=int(user_id), text=text, parse_mode=parse_mode)
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
        
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
            "ed_rub": int(data.get("ed_rub", 0)),
            "ed_exp": int(data.get("ed_exp", 0)),
            "ed_activ": int(data.get("ed_activ", 0)),
            "ed_bust": int(data.get("ed_bust", 0)),
            "ew_rub": int(data.get("ew_rub", 0)),
            "ew_exp": int(data.get("ew_exp", 0)),
            "ew_activ": int(data.get("ew_activ", 0)),
            "ew_bust": int(data.get("ew_bust", 0)),
            "max_zp": int(data.get("max_zp", 0)),
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
    try:
        ensure_user_chars(user_id)
        user_chars = load_user_chars()

        # обновляем exp_multiplier только если характеристика задаёт отличное от 1.0
        ch_exp_mult = float(ch_data.get("exp_multiplier", 1.0))
        if ch_exp_mult != 1.0:
            user_chars[user_id]['exp_multiplier'] = str(ch_exp_mult)
        skip_keys = {"name", "required_boosts", "limit", "limitiz", "ball", "exp", "money", "exp_multiplier"}
        for k, v in ch_data.items():
            if k in skip_keys:
                continue
            try:
                intval = int(v)
            except Exception:
                continue
            if intval != 0:
                user_chars[user_id][k] = str(intval)

        save_user_chars(user_chars)
    except Exception as e:
        logging.error(f"Ошибка при сохранении характеристик пользователя {user_id}: {e}")

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

async def lvlconf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_info = get_user_info(user_id)
    current_level = int(user_info.get('level', 0)) if user_info else 0
    lvlconf_val = int(user_info.get('lvlconf', 0)) if user_info else 0
    boosts = int(user_info.get('osk', 0)) if user_info else 0
    ev_level = int(user_info.get('ev_level', 0)) if user_info else 0

    # Стоимости подтверждения по уровням
    confirm_costs = {
        10: 50, 11: 50, 12: 50, 13: 50, 14: 50, 15: 50, 16: 50, 17: 50, 18: 50, 19: 50,
        20: 100, 21: 100, 22: 100, 23: 100, 24: 100, 25: 100, 26: 100, 27: 100, 28: 100, 29: 100,
        30: 150, 31: 150, 32: 150, 33: 150, 34: 150, 35: 150, 36: 150, 37: 150, 38: 150, 39: 150,
        40: 200, 41: 200, 42: 200, 43: 200, 44: 200, 45: 200, 46: 200, 47: 200, 48: 200, 49: 200,
        50: 250, 51: 250, 52: 250, 53: 250, 54: 250, 55: 250, 56: 250, 57: 250, 58: 250, 59: 250,
        60: 300, 61: 300, 62: 300, 63: 300, 64: 300, 65: 300, 66: 300, 67: 300, 68: 300, 69: 300,
        70: 350, 71: 350, 72: 350, 73: 350, 74: 350, 75: 350, 76: 350, 77: 350, 78: 350, 79: 350,
        80: 400, 81: 400, 82: 400, 83: 400, 84: 400, 85: 400, 86: 400, 87: 400, 88: 400, 89: 400,
        90: 450, 91: 450, 92: 450, 93: 450, 94: 450, 95: 450, 96: 450, 97: 450, 98: 450, 99: 450,
        100: 500
    }

    # Если подтверждение не требуется для этого пользователя и он НЕ имеет эволюции — выходим
    if lvlconf_val == 0 and ev_level == 0:
        await update.message.reply_text("✅ Подтверждение уровня не требуется или уровень не требует подтверждения.")
        return

    # Если уровень не в таблице и у пользователя нет эволюции — выходим
    if current_level not in confirm_costs and ev_level == 0:
        await update.message.reply_text("✅ Подтверждение уровня не требуется или уровень не требует подтверждения.")
        return

    # Определяем стоимость: если есть эволюция — бесплатно
    cost = 0 if ev_level > 0 else confirm_costs.get(current_level, 0)

    # Проверка баланса (требуется только если cost > 0)
    if cost > 0 and boosts < cost:
        await update.message.reply_text(f"❌ Недостаточно бустов для подтверждения уровня! Требуется: {cost} 💈, у вас: {boosts} 💈")
        return

    # Сохраняем изменения: списываем бусты (если требуется) и снимаем требование подтверждения
    config = load_accounts()
    sec = config[user_id]
    if cost > 0:
        sec['osk'] = str(boosts - cost)
    # устанавливаем lvlconf = '0' (подтверждение выполнено)
    sec['lvlconf'] = '0'
    save_accounts(config)

    # Ответ пользователю: разный текст если подтверждение было бесплатным
    if ev_level > 0:
        # Эмодзи указываем бесплатное подтверждение по эволюции
        await update.message.reply_text(
            f"✅ Ваш {current_level} уровень успешно подтверждён!\n"
            f"🧧 Подтверждение выполнено бесплатно благодаря эволюционным привилегиям (уровень эволюции: {ev_level}).\n"
            f"Теперь вы можете подавать отчёты и пользоваться всеми функциями.",
        )
    else:
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

    # Эмодзи для уровней эволюции (приоритет над обычными)
    evo_emojis = {
        1: "🀄",
        2: "🎴",
        3: "🃏"
    }

    def get_level_emoji(level: int) -> str:
        for level_range, emoji in level_emojis:
            if level in level_range:
                return emoji
        return "❔"

    def get_activity_level(ball: int) -> str:
        if ball >= 875:
            return "🟣 Превосходная"
        elif 700 <= ball < 875:
            return "🟡 Максимальная"
        elif 525 <= ball < 700:
            return "🟢 Средняя"
        elif 350 <= ball < 525:
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

        # Определяем ev_level (эволюцию) пользователя
        ev_level = 0
        try:
            for sec in config.sections():
                if not sec.isdigit():
                    continue
                sec_nick = config[sec].get('nick', '')
                if sec_nick == nick:
                    ev_level = int(config[sec].get('ev_level', '0') or 0)
                    break
        except Exception:
            ev_level = 0

        # Приоритет: если есть ev_level, используем его эмодзи
        if ev_level > 0:
            lvl_emoji = evo_emojis.get(ev_level, get_level_emoji(level))
        else:
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

#############ОБНОВА АДМИН РАССЫЛКА#############
async def new_obnova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    message_text = "Введите текст для рассылки об обновлении:"
    keyboard = [[InlineKeyboardButton("Отменить", callback_data="cancel_new_obnova")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(message_text, reply_markup=reply_markup)
    context.user_data['new_obnova'] = True

# Отмена рассылки обновления
async def cancel_new_obnova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if 'new_obnova' in context.user_data:
        del context.user_data['new_obnova']
    await query.message.edit_text("❌ Рассылка обновления отменена.")
    
###############СНЯТИЕ ПРЕДОВ#################
async def pred(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    warnings = int(user_info.get('warnings', 0)) if user_info else 0
    boosts = int(user_info.get('osk', 0)) if user_info else 0
    warning_emoji = "⚠️"
    boosts_emoji = "💈"

    # Сначала отправляем фото (замени "warn.png" на свое изображение)
    try:
        with open("warn.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
    except Exception:
        pass  # если файла нет, просто пропускаем

    message = (
        f"{warning_emoji} <b> Снятие предупреждения.</b>\n\n"
        f"❗ У вас сейчас <b>{warnings}</b> предупреждений.\n"
        f"🔔 Стоимость снятия одного предупреждения — <b>100 {boosts_emoji}</b> бустов.\n\n"
        f"На вашем балансе: <b>{boosts} {boosts_emoji}</b>.\n\n"
        f"🪔 Для снятия предупреждения используйте команду: <code>/removewarn</code>"
    )
    await update.message.reply_text(message, parse_mode="HTML", reply_markup=get_back_to_function_keyboard())

async def removewarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    if not user_info:
        await update.message.reply_text("⛔ Ошибка: Информация о вашем аккаунте не найдена.")
        return

    warnings = int(user_info.get('warnings', 0))
    boosts = int(user_info.get('osk', 0))

    if warnings <= 0:
        await update.message.reply_text("⛔ У вас нет предупреждений для снятия.")
        return

    if boosts < 100:
        await update.message.reply_text("⛔ Недостаточно бустов для снятия предупреждения (нужно 100 💈).")
        return

    # Снимаем предупреждение и списываем бусты
    config = load_accounts()
    sec = config[str(user_id)]
    sec['warnings'] = str(warnings - 1)
    sec['osk'] = str(boosts - 100)
    save_accounts(config)

    await update.message.reply_text(
        f"✅ Одно предупреждение снято! Осталось: {warnings - 1} ⚠️\n"
        f"Списано 100 💈 бустов. Баланс: {boosts - 100} 💈"
    )

    # Уведомить всех админов (всех уровней)
    admins = [int(sec) for sec in config.sections() if sec.isdigit() and int(config[sec].get('is_admin', 0)) >= 1]
    for admin_id in admins:
        if admin_id != user_id:
            try:
                await context.bot.send_message(
                    admin_id,
                    f"🅰 Пользователь {user_info['nick']} снял предупреждение за 100 💈 бустов. Осталось: {warnings - 1} ⚠️"
                )
            except Exception:
                pass

###############БОНУСНАЯ СИСТЕМА#################
async def bonus(update, context):
    user_id = str(update.effective_user.id)
    user_info = get_user_info(user_id)
    if not user_info:
        await update.message.reply_text("Ошибка: информация о вашем аккаунте не найдена.")
        return

    position = user_info.get("position", "").strip().lower()
    if position in ["хранитель"]:
        await update.message.reply_text("❌ Ваш ранг не позволяет получать ежедневный бонус.")
        return

    # Проверяем дату последнего бонуса
    config = load_accounts()
    sec = config[user_id]
    today_str = datetime.now().strftime("%Y-%m-%d")
    last_bonus = sec.get("last_bonus", "")

    if last_bonus == today_str:
        await update.message.reply_text("⏳ Вы уже получили ежедневный бонус сегодня! Приходите завтра.")
        return

    # Определяем редкость
    roll = random.randint(1, 100)
    if roll <= 1:
        rarity = "legendary"
    elif roll <= 5:
        rarity = "rare"
    else:
        rarity = "common"

    # Призы по редкости
    common_prizes = [
        ("ball", 1, "🧿 1 монета активности"),
        ("ball", 2, "🧿 2 монеты активности"),
        ("ball", 3, "🧿 3 монеты активности"),
        ("exp", 1, "⚡ 1 EXP"),
        ("exp", 2, "⚡ 2 EXP"),
        ("exp", 3, "⚡ 3 EXP"),
        ("osk", 1, "💈 1 буст"),
        ("personal_account", 100000, "💳 100.000 RUB"),
        ("personal_account", 250000, "💳 250.000 RUB"),
        ("personal_account", 500000, "💳 500.000 RUB"),
    ]
    rare_prizes = [
        ("ball", 5, "🧿 5 монет активности"),
        ("ball", 10, "🧿 10 монет активности"),
        ("exp", 10, "⚡ 10 EXP"),
        ("exp", 20, "⚡ 20 EXP"),
        ("exp", 30, "⚡ 30 EXP"),
        ("osk", 3, "💈 3 буста"),
        ("osk", 5, "💈 5 бустов"),
        ("personal_account", 1000000, "💳 1.000.000 RUB"),
        ("personal_account", 3000000, "💳 3.000.000 RUB"),
    ]
    legendary_prizes = [
        ("ball", 25, "🧿 25 монет активности"),
        ("exp", 50, "⚡ 50 EXP"),
        ("exp", 100, "⚡ 100 EXP"),
        ("osk", 10, "💈 10 бустов"),
        ("osk", 20, "💈 20 бустов"),
        ("osk", 30, "💈 30 бустов"),
        ("personal_account", 5000000, "💳 5.000.000 RUB"),
        ("personal_account", 10000000, "💳 10.000.000 RUB"),
    ]

    if rarity == "legendary":
        prize = random.choice(legendary_prizes)
    elif rarity == "rare":
        prize = random.choice(rare_prizes)
    else:
        prize = random.choice(common_prizes)

    key, amount, desc = prize

    # --- Применяем основной приз ---
    sec[key] = str(int(sec.get(key, 0)) + amount)

    # --- Собираем и применяем дополнительные бонусы из характеристик ---
    extras_lines = []
    try:
        user_chars = load_user_chars()
    except Exception:
        user_chars = None

    if user_chars and user_chars.has_section(user_id):
        # читаем набор возможных ежедневных бонусов из user_characteristics.ini
        ed_rub = int(user_chars[user_id].get("ed_rub", "0"))
        ed_exp = int(user_chars[user_id].get("ed_exp", "0"))
        ed_activ = int(user_chars[user_id].get("ed_activ", "0"))
        # некоторые варианты ранее назывались ad_bust, поддерживаем оба
        ed_bust = int(user_chars[user_id].get("ed_bust", user_chars[user_id].get("ad_bust", "0")))

        if ed_rub:
            prev = int(sec.get("personal_account", "0"))
            sec["personal_account"] = str(prev + ed_rub)
            # форматируем число удобно для вывода
            try:
                formatted = format_number(ed_rub, locale="ru_RU")
            except Exception:
                formatted = f"{ed_rub}"
            extras_lines.append(f"💳 +{formatted} RUB")

        if ed_exp:
            prev = int(sec.get("exp", "0"))
            sec["exp"] = str(prev + ed_exp)
            extras_lines.append(f"⚡ +{ed_exp} EXP")

        if ed_activ:
            prev = int(sec.get("ball", "0"))
            sec["ball"] = str(prev + ed_activ)
            extras_lines.append(f"🧿 +{ed_activ} монет активности")

        if ed_bust:
            prev = int(sec.get("osk", "0"))
            sec["osk"] = str(prev + ed_bust)
            extras_lines.append(f"💈 +{ed_bust} бустов")

    # Ставим отметку о получении бонуса и сохраняем все изменения одним вызовом
    sec["last_bonus"] = today_str
    save_accounts(config)

    # --- Отправляем основное сообщение о призе ---
    header = "🏮 Ваш ежедневный бонус"
    if rarity == "legendary":
        header = "🎉 <b>Легендарный ежедневный бонус!</b>"
    elif rarity == "rare":
        header = "✨ <b>Редкий ежедневный бонус!</b>"

    main_text = f"{header}\n\n<b>{desc}</b>\n"
    await update.message.reply_text(main_text, parse_mode="HTML")

    # --- Если есть дополнительные бонусы от характеристик — отправляем отдельным сообщением ---
    if extras_lines:
        extras_text = "\n".join(extras_lines)
        char_msg = (
            "🎁 <b>Бонусы от приобретённых характеристик</b>\n\n"
            "🔮 У вас активны уникальные характеристики из Центра обмена — вам дополнительно начислено:\n\n"
            f"{extras_text}\n\n"
            "ℹ️ Эти бонусы связаны с приобретёнными характеристиками и выдаются ежедневно вместе с основным бонусом."
        )
        await update.message.reply_text(char_msg, parse_mode="HTML")

    # Оповещение всех пользователей при легендарном бонусе (как было раньше)
    if rarity == "legendary":
        notify_text = (
            f"🎉 <b>ВАУ! Кто-то получил легендарный ежедневный бонус!</b>\n"
            f"📸 Пользователь: <b>{user_info['nick']}</b>\n"
            f"🏮 Бонус: <b>{desc}</b>"
        )
        all_accounts = load_accounts()
        for uid in all_accounts.sections():
            if uid.isdigit() and uid != user_id:
                try:
                    await context.bot.send_message(chat_id=int(uid), text=notify_text, parse_mode="HTML")
                except Exception:
                    pass
                
##########################################ФУНКЦИЯ ЗАКРЫТИЯ НЕДЕЛЮ - ОПРЕДЕЛЕНИЕ ПОБЕДИТЕЛЕЙ######################
async def rating_results_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    top_players = get_top_players()
    context.user_data["rating_confirm_stage"] = 1
    context.user_data["rating_top"] = top_players
    text = "<b>🏆 Итоги рейтинга недели</b>\n\n"
    emojis = ["🥇", "🥈", "🥉"]
    for i, (nick, ball, level, position) in enumerate(top_players):
        text += f"{emojis[i]} <b>{nick}</b> ({ball} 🧿) — {position}\n"
    text += "\n<b>Условия награждения:</b>\n"
    text += "🥇 — 300 💈 1000 ⚡ за превосходную активность (≥875)\n"
    text += "🥈 — 200 💈 500 ⚡ за максимальную активность (≥700)\n"
    text += "🥉 — 100 💈 250 ⚡ за среднюю активность (≥525)\n"
    text += "\nНажмите <b>Подтвердить</b> 3 раза для выдачи наград."
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="rating_confirm_yes")],
        [InlineKeyboardButton("❌ Отменить", callback_data="rating_confirm_no")]
    ]
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def rating_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data.split("_")[-1]
    if action == "no":
        context.user_data.pop("rating_confirm_stage", None)
        context.user_data.pop("rating_top", None)
        await query.message.edit_text("Операция отменена. Возврат в панель администратора.")
        await admin(update, context)
        return

    # если yes
    context.user_data["rating_confirm_stage"] += 1
    stage = context.user_data["rating_confirm_stage"]
    if stage < 4:
        keyboard = [
            [InlineKeyboardButton("✅ Подтвердить", callback_data="rating_confirm_yes")],
            [InlineKeyboardButton("❌ Отменить", callback_data="rating_confirm_no")]
        ]
        await query.message.edit_text(
            f"Подтвердите действие {stage}/3 для выдачи наград рейтинга.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # --- ЭТАП НАГРАЖДЕНИЯ ---
    top_players = context.user_data.get("rating_top", [])
    config = load_accounts()
    results = []
    emojis = ["🥇", "🥈", "🥉"]
    prizes = [300, 200, 100]
    # Добавляем призы EXP для 1..3 мест: 1 место = 1000, 2 место = 500, 3 место = 250
    exp_prizes = [1000, 500, 250]
    min_balls = [875, 700, 525]
    levels = ["превосходная", "максимальная", "средняя"]

    for idx, (nick, ball, level, position) in enumerate(top_players):
        user_id = None
        for sec in config.sections():
            if config[sec].get("nick", "") == nick:
                user_id = sec
                break
        if user_id is None:
            results.append(f"{emojis[idx]} <b>{nick}</b> — ❌ Не найден в базе!")
            continue
        prize = prizes[idx]
        min_ball = min_balls[idx]
        lvlname = levels[idx]
        if ball >= min_ball:
            # Выдаём бусты и EXP
            config[user_id]["osk"] = str(int(config[user_id].get("osk", 0)) + prize)
            exp_amount = exp_prizes[idx]
            config[user_id]["exp"] = str(int(config[user_id].get("exp", 0)) + exp_amount)
            save_accounts(config)
            # Сообщение участнику (бусты + опыт)
            try:
                await context.bot.send_message(
                    chat_id=int(user_id),
                    text=f"{emojis[idx]} Поздравляем! Вы заняли {idx+1} место в недельном рейтинге, получили {prize} 💈 бустов и {exp_amount} ⚡ опыта за {lvlname} активность."
                )
            except Exception:
                pass
            results.append(f"{emojis[idx]} <b>{nick}</b> — {prize} 💈, {exp_amount} ⚡ (условие: {lvlname} активность ✅)")
        else:
            results.append(f"{emojis[idx]} <b>{nick}</b> — ❌ Приз не выдан (условие: {lvlname} активность, у вас {ball} 🧿)")
    rd = get_rd()
    rd1 = rd - timedelta(days=6)
    today = datetime.now().date()
    final_text = f"<b>🏆 ИТОГИ-недели!\nПодведены итоги рейтинга за расчётную неделю (период {rd1.strftime('%d.%m.%Y')} - {rd.strftime('%d.%m.%Y')}).</b>\n\n" + "\n".join(results)
    await notify_all_users_with_photo(context, "itog.png", final_text, parse_mode="HTML")
    await query.message.edit_text("Готово! Итоговое сообщение отправлено всем пользователям.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="admin")]]))

    context.user_data.pop("rating_confirm_stage", None)
    context.user_data.pop("rating_top", None)

async def notify_all_users_with_photo(context, photo_path, text, parse_mode="HTML"):
    config = load_accounts()
    for user_id in config.sections():
        if user_id.isdigit():
            try:
                with open(photo_path, "rb") as photo:
                    await context.bot.send_photo(chat_id=int(user_id), photo=photo)
                await context.bot.send_message(chat_id=int(user_id), text=text, parse_mode=parse_mode)
            except Exception as e:
                logging.error(f"Ошибка при отправке фото/сообщения пользователю {user_id}: {e}")

##############################################СИСТЕМА ДЕПОЗИТОВ########################
async def request_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("popoln.png", "rb") as photo:
        keyboard = [
            [InlineKeyboardButton("💰 Подать заявку", callback_data="deposit_start")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_photo(
            photo=photo,
            caption="📥 Пополнение счёта возможно только через заявку, пополните бюджет семьи в игре, подайте заявку на пополнение и ожидайте зачисления средств на личный счёт.\n\n"
                    "Нажмите кнопку ниже, чтобы подать заявку.",
            reply_markup=reply_markup
        )

async def start_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Отправляем новое сообщение, а не edit_text (иначе ошибка BadRequest)
    await query.message.reply_text("💰 Введите сумму пополнения (в рублях):")

    # Флаг, что ждём число от пользователя
    context.user_data["awaiting_deposit_amount"] = True

async def process_deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_deposit_amount"):
        try:
            amount = int(update.message.text.strip())  # Преобразуем в целое число
            if amount <= 0:
                await update.message.reply_text("❌ Введите положительное число.")
                return
        except ValueError:
            await update.message.reply_text("❌ Введите корректное целое число.")
            return

        user_id = update.effective_user.id
        nick = update.effective_user.username or update.effective_user.full_name

        # Загружаем файл deposits.ini
        config = load_deposits()
        request_id = str(int(time.time()))  # уникальный ID заявки (по времени)
        sec_name = f"deposit_{request_id}"

        config[sec_name] = {
            "user_id": str(user_id),
            "nick": nick,
            "amount": str(amount),  # сохраняем как целое число
            "status": "pending"
        }
        save_deposits(config)

        await update.message.reply_text(
            f"📋 Ваша заявка на пополнение {amount} RUB создана и ожидает подтверждения администратором."
        )
        await notify_admin_about_new_depozit(nick, amount, context)

        # Сбрасываем флаг
        context.user_data["awaiting_deposit_amount"] = False

async def notify_admin_about_new_depozit(nick: str, amount: float, context: ContextTypes.DEFAULT_TYPE):
    # Получаем список администраторов с уровнем >= 2
    admin_ids_filtered = load_admin_ids()  # load_admin_ids должна возвращать список ID (строк или чисел) для is_admin >= 2
    if not admin_ids_filtered:
        return

    message = (
        f"🅰 Новая заявка на пополнение!\n"
        f"👤 Пользователь: {nick}\n"
        f"💸 Сумма пополнения: {amount} RUB\n"
        f"Проверьте заявку в админ-панели для окончательного подтверждения или отклонения."
    )
    
    # Отправляем уведомление каждому администратору из списка
    for admin_id in admin_ids_filtered:
        try:
            await context.bot.send_message(admin_id, message)
            print(f"Уведомление отправлено админу {admin_id}")
        except Exception as e:
            print(f"Ошибка при отправке уведомления админу {admin_id}: {e}")
            
async def admin_deposits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    config = load_deposits()

    # Собираем все заявки со статусом "pending"
    requests = [sec for sec in config.sections() if sec.startswith("deposit_") and config[sec].get("status") == "pending"]

    if not requests:
        await query.message.edit_text("📋 Нет заявок на пополнение, ожидающих подтверждения.")
        return

    text = "📋 Активные заявки на пополнение:\n"
    keyboard = []
    for sec in requests:
        nick = config[sec].get("nick", "Неизвестный")
        amount = config[sec].get("amount", "0")
        text += f"\n🔹 {nick} — {amount} RUB"
        req_id = sec[len("deposit_"):]
        keyboard.append([InlineKeyboardButton(f"ID заявки: {req_id}", callback_data=f"viewdep_{req_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def view_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    request_id = query.data.split("_")[1]
    config = load_deposits()
    sec_name = f"deposit_{request_id}"

    if not config.has_section(sec_name):
        await query.message.edit_text("❌ Заявка не найдена.")
        return

    user_id = int(config[sec_name]["user_id"])
    amount = config[sec_name]["amount"]
    nick = config[sec_name]["nick"]

    text = f"Заявка на пополнение {amount} RUB от {nick}\nID заявки: {request_id}\nВыберите действие:"
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data=f"approvedep_{request_id}")],
        [InlineKeyboardButton("❌ Отклонить", callback_data=f"rejectdep_{request_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def approve_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    request_id = query.data.split("_")[1]
    config = load_deposits()
    sec_name = f"deposit_{request_id}"

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
        new_balance = personal_account + amount
        accounts_config[user_section]['personal_account'] = str(new_balance)
        save_accounts(accounts_config)
    else:
        await query.message.edit_text("❌ Пользователь не найден.")
        return

    config[sec_name]["status"] = "approved"
    save_deposits(config)

    # Уведомляем пользователя
    try:
        await context.bot.send_message(user_id, f"✅ Ваше пополнение {amount} RUB подтверждено!")
    except:
        pass

    await query.message.edit_text(f"✅ Заявка на пополнение {amount} RUB для {nick} подтверждена.")

async def reject_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    request_id = query.data.split("_")[1]
    config = load_deposits()
    sec_name = f"deposit_{request_id}"

    if not config.has_section(sec_name):
        await query.message.edit_text("❌ Заявка не найдена.")
        return

    user_id = int(config[sec_name]["user_id"])
    amount = config[sec_name]["amount"]
    nick = config[sec_name]["nick"]

    config[sec_name]["status"] = "rejected"
    save_deposits(config)

    try:
        await context.bot.send_message(user_id, f"❌ Ваше пополнение {amount} RUB отклонено.")
    except:
        pass

    await query.message.edit_text(f"❌ Заявка на пополнение {amount} RUB для {nick} отклонена.")

##########MASTERSKAYA####################
async def workshop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_path = "prazdnik.png"

    # Получаем состояние суперприза: (current, target)
    try:
        # Если в модуле уже есть эта функция — используем её
        sp_current, sp_target = get_superprize_state()
    except Exception:
        # Иначе читаем settings.ini прямо
        try:
            cfg = load_settings()
            if not cfg.has_section("superprize"):
                sp_current = 0
                sp_target = 1000
            else:
                sp_current = int(cfg["superprize"].get("current", "0") or 0)
                sp_target = int(cfg["superprize"].get("target", "1000") or 1000)
        except Exception:
            sp_current = 0
            sp_target = 1000

    # Формируем строку состояния суперприза для подписи
    try:
        # форматируем с разделителем тысяч, если доступна locale/format_number
        sp_display = f"{sp_current:,}".replace(",", ".")
        sp_target_display = f"{sp_target:,}".replace(",", ".")
    except Exception:
        sp_display = str(sp_current)
        sp_target_display = str(sp_target)

    superprize_line = f"🏺 Суперприз: {sp_display} ❄️\n\n"

    try:
        # Пытаемся открыть основное фото мастерской
        with open(photo_path, "rb") as photo:
            await update.message.reply_photo(
                photo,
                caption=(
                    "🎄 *Праздничная мастерская* 🎄\n\n"
                    "Эта система, которая позволяет расколоть собранные снежинки и получить ценные награды.\n"
                    "Система активна с 03.12.2025 до 15.01.2026 включительно.\n\n"
                    "❄️ *Стоимость раскалывания*: 50 снежинок.\n"
                    "🎁 *Призовой пул*: призы различной уникальности (хлам, обычные, уникальные и легендарные призы), а также *бесплатную ЭВОЛЮЦИЮ и СУПЕРПРИЗ.*\n\n"
                    + superprize_line +
                    "Минимальный суперприз - *3.000 снежинок*, при этом каждое раскалывание снежинок вносит в суперприз 5 снежинок.\n\n"
                    "⬇️ Выберите действие ниже:"
                ),
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup(
                    [
                        [KeyboardButton("Раскалывание"), KeyboardButton("Награды")],
                        [KeyboardButton("История наград")],
                        [KeyboardButton("Назад")],
                    ],
                    resize_keyboard=True,
                    one_time_keyboard=False,
                ),
            )

    except FileNotFoundError:
        # Файл не найден — отправляем фото-заглушку и сообщение о закрытии мастерской
        fallback_photo = "workshop_closed.png"  # ← добавьте свой файл сюда
        try:
            with open(fallback_photo, "rb") as ph:
                await update.message.reply_photo(
                    ph,
                    caption=(
                        "🎄 *Мастерская временно недоступна!*\n\n"
                        "❄️ На данный момент праздничная мастерская закрыта.\n"
                        "✨ Ожидайте новогоднего обновления."
                    ),
                    parse_mode="Markdown",
                )
        except FileNotFoundError:
            # Если даже фото-заглушки нет — текстом (последний уровень)
            await update.message.reply_text(
                "🎄 Мастерская временно недоступна!\n"
                "✨ Ожидайте новогоднего обновления."
            )
            
async def items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "🎄 При раскалывании снежинок можно получить награды различной редкости (хлам, обычное, уникальное, легендарное), а также бесплатную ЭВОЛЮЦИЮ и СУПЕРПРИЗ.\n\n"
    await update.message.reply_text(message, parse_mode='HTML')
    # Пути к изображениям
    image_paths = ["prizhm1.png"]

    for path in image_paths:
        try:
            with open(path, "rb") as img:
                await update.message.reply_photo(photo=InputFile(img))
        except FileNotFoundError:
            await update.message.reply_text(f"⚠️ Файл {path} не найден.")

async def reward_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    rewards_history_path = "rewards_history.ini"
    rewards_history = configparser.ConfigParser()

    # Чтение файла с кодировкой utf-8
    try:
        with open(rewards_history_path, "r", encoding="utf-8") as history_file:
            rewards_history.read_file(history_file)
    except FileNotFoundError:
        await update.message.reply_text("📜 История наград отсутствует. Вы ещё не раскалывали снежинки")
        return

    if not rewards_history.has_section(str(user_id)):
        await update.message.reply_text("📜 История наград пуста. Вы ещё не раскалывали снежинок.")
        return

    # Формируем читаемый текст истории наград
    history_text = "📜 *История наград:*\n\n"
    for unique_id, entry in rewards_history[str(user_id)].items():
        try:
            # Каждая запись имеет формат "временная метка - описание награды"
            timestamp, reward = entry.split(" - ", 1)
            history_text += f"- {timestamp}: {reward}\n"
        except ValueError:
            # Если формат записи нарушен, пропускаем её
            continue

    if history_text.strip() == "📜 *История наград:*":
        # Если история пуста после формирования, уведомляем пользователя
        await update.message.reply_text("📜 История наград пуста. Вы ещё не раскалывали снежинки.")
    else:
        # Разбиваем текст на части, если он превышает лимит длины сообщения Telegram
        message_limit = 4096
        messages = [history_text[i:i + message_limit] for i in range(0, len(history_text), message_limit)]

        # Отправляем каждую часть пользователю
        for message in messages:
            await update.message.reply_text(message, parse_mode="Markdown")

async def _send_photo_bytes(bot, chat_id, data: bytes, caption: str = None, parse_mode: str = None):
    """Фоновая задача: отправляет фото (BytesIO) и ловит ошибки."""
    bio = BytesIO(data)
    bio.name = "photo.png"
    try:
        await bot.send_photo(chat_id=int(chat_id), photo=bio, caption=caption, parse_mode=parse_mode)
    except Exception as e:
        logging.exception(f"Ошибка при отправке фото {chat_id}: {e}")

def send_photo_nonblocking(bot, chat_id, file_path: str, caption: str = None, parse_mode: str = None):
    """
    Неблокирующая отправка фото:
      - чтение файла выполняется в отдельном потоке (asyncio.to_thread)
      - затем создаётся фоновая задача для отправки (asyncio.create_task)
    """
    async def _prepare_and_send():
        try:
            # читаем файл в отдельном потоке, чтобы не блокировать event loop
            data = await asyncio.to_thread(lambda: open(file_path, "rb").read())
        except Exception as e:
            logging.warning(f"Не удалось прочитать файл {file_path}: {e}")
            return
        await _send_photo_bytes(bot, chat_id, data, caption=caption, parse_mode=parse_mode)

    # запустим подготовительную таску без await — вернётся мгновенно
    asyncio.create_task(_prepare_and_send())

# Таймаут для открытия мастерской (секунды) — не чаще одного раза в 3 секунды
WORKSHOP_COOLDOWN = 2
_last_workshop_call = {}  # map: user_id (str) -> last_call_time (float)

# Основная функция
# --- Обновлённая функция merge_pumpkins (мастерская) ---
async def merge_pumpkins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Праздничная мастерская — раскол снежинок (обновлённая версия).

    Логика:
      - Стоимость открытия: WORKSHOP_COST (50) — снимается со счёта user's 't' (снежинки).
      - В суперприз добавляется int(WORKSHOP_COST * SUPERPRIZE_CONTRIB_RATE) снежинок.
      - Генерируется случайное число 0..2000, по которому определяется редкость:
          0..999   -> Хлам
          1000..1899 -> Обычное
          1900..1989 -> Уникальное
          1990..2000 -> Легендарное
      - Для легендарного дополнительно случайно выбирается между:
          - обычная легенда (большая награда),
          - суперприз (выдаёт накопленное и сбрасывает в SUPERPRIZE_INITIAL),
          - новогодняя эволюция (повышение ev_level, если возможно).
      - История наград записывается в REWARDS_HISTORY_FILE.
      - При легендарной выдаче рассылается поздравление через notify_all_users.
    """
    user = update.effective_user
    user_id = str(user.id)
    chat_id = update.effective_chat.id

    # Проверка cooldown — не чаще одного раза в WORKSHOP_COOLDOWN секунд
    now = time.time()
    last = _last_workshop_call.get(user_id, 0)
    if now - last < WORKSHOP_COOLDOWN:
        # Красивое новогоднее уведомление об ожидании
        await update.message.reply_text(
            "✨ Идёт раскалывание снежинок — не спешите ✨\n"
        )
        return
    # фиксируем время успешного запуска (блокирует повторные клики на короткий период)
    _last_workshop_call[user_id] = now

    accounts_cfg = load_accounts()
    if not accounts_cfg.has_section(user_id):
        await update.message.reply_text("❌ Ошибка: профиль не найден в accounts.ini.")
        return

    # Текущие снежинки пользователя
    try:
        current_t = int(accounts_cfg[user_id].get("t", "0"))
    except Exception:
        current_t = 0

    if current_t < WORKSHOP_COST:
        await update.message.reply_text(f"❄ Недостаточно снежинок. Требуется {WORKSHOP_COST} ❄ для попытки.")
        return

    # Списываем стоимость открытия
    current_t -= WORKSHOP_COST
    accounts_cfg[user_id]["t"] = str(current_t)
    save_accounts(accounts_cfg)

    # Рассчитываем вклад в суперприз и добавляем
    contrib = int(WORKSHOP_COST * SUPERPRIZE_CONTRIB_RATE)
    if contrib <= 0 and WORKSHOP_COST > 0:
        contrib = 1
    add_to_superprize(contrib)

    # Генерируем код для определения редкости
    code = random.randint(0, 2000)
    if 0 <= code <= 999:
        rarity = "Хлам"
    elif 1000 <= code <= 1899:
        rarity = "Обычное"
    elif 1900 <= code <= 1989:
        rarity = "Уникальное"
    else:
        rarity = "Легендарное"

    prize_texts = []
    comment = ""
    legendary_broadcast = False

    # Утилита для прибавления целого значения к полю в accounts.ini
    def add_to_account_field(cfg, uid, key, amount):
        try:
            prev = int(cfg[uid].get(key, "0"))
        except Exception:
            prev = 0
        cfg[uid][key] = str(prev + int(amount))

    # Обычные реализации пулов (можно расширять; здесь — примеры по ТЗ)
    if rarity == "Хлам":
        # Выбираем случайный тип хлама
        choice = random.choice(["t", "ball", "exp", "osk", "ev_stones", "money"])
        if choice == "t":
            amt = random.randint(1, 25)
            add_to_account_field(accounts_cfg, user_id, "t", amt)
            prize_texts.append(f"→ ❄️ {amt} снежинок")
        elif choice == "ball":
            amt = random.randint(1, 5)
            add_to_account_field(accounts_cfg, user_id, "ball", amt)
            prize_texts.append(f"→ 🧿 {amt} монет активности")
        elif choice == "exp":
            amt = random.randint(1, 25)
            add_to_account_field(accounts_cfg, user_id, "exp", amt)
            prize_texts.append(f"→ ⚡ {amt} EXP")
        elif choice == "osk":
            amt = random.randint(1, 5)
            add_to_account_field(accounts_cfg, user_id, "osk", amt)
            prize_texts.append(f"→ 💈 {amt} буст(ов)")
        elif choice == "ev_stones":
            amt = random.randint(1, 5)
            add_to_account_field(accounts_cfg, user_id, "ev_stones", amt)
            prize_texts.append(f"→ 🔥 {amt} респект(ов)")
        else:
            amt = random.randint(100_000, 500_000)
            add_to_account_field(accounts_cfg, user_id, "personal_account", amt)
            prize_texts.append(f"→ 💳 {amt:,}".replace(",", ".") + " RUB")
        comment = "«Снежинки раскололись, подарок нашёлся! Пусть и скромный, зато с новогодним настроением!»"

    elif rarity == "Обычное":
        choice = random.choice(["t", "ball", "exp", "osk", "ev_stones", "money", "oosk"])
        if choice == "t":
            amt = random.randint(50, 100)
            add_to_account_field(accounts_cfg, user_id, "t", amt)
            prize_texts.append(f"→ ❄️ {amt} снежинок")
        elif choice == "ball":
            amt = random.randint(10, 25)
            add_to_account_field(accounts_cfg, user_id, "ball", amt)
            prize_texts.append(f"→ 🧿 {amt} монет активности")
        elif choice == "exp":
            amt = random.randint(50, 100)
            add_to_account_field(accounts_cfg, user_id, "exp", amt)
            prize_texts.append(f"→ ⚡ {amt} EXP")
        elif choice == "osk":
            amt = random.randint(10, 25)
            add_to_account_field(accounts_cfg, user_id, "osk", amt)
            prize_texts.append(f"→ 💈 {amt} буст(ов)")
        elif choice == "ev_stones":
            amt = random.randint(10, 25)
            add_to_account_field(accounts_cfg, user_id, "ev_stones", amt)
            prize_texts.append(f"→ 🔥 {amt} респект(ов)")
        elif choice == "money":
            amt = random.randint(500_000, 2_500_000)
            add_to_account_field(accounts_cfg, user_id, "personal_account", amt)
            prize_texts.append(f"→ 💳 {amt:,}".replace(",", ".") + " RUB")
        else:  # oosk
            amt = random.randint(25, 100)
            add_to_account_field(accounts_cfg, user_id, "oosk", amt)
            prize_texts.append(f"→ 📘 {amt} O-осколков")
        comment = "«Вот это новогодний сюрприз! Хороший улов — праздник будет ярким!»"

    elif rarity == "Уникальное":
        choice = random.choice(["t", "ball", "exp", "osk", "ev_stones", "money", "uosk"])
        if choice == "t":
            amt = random.randint(250, 500)
            add_to_account_field(accounts_cfg, user_id, "t", amt)
            prize_texts.append(f"→ ❄️ {amt} снежинок")
        elif choice == "ball":
            amt = random.randint(50, 250)
            add_to_account_field(accounts_cfg, user_id, "ball", amt)
            prize_texts.append(f"→ 🧿 {amt} монет активности")
        elif choice == "exp":
            amt = random.randint(250, 500)
            add_to_account_field(accounts_cfg, user_id, "exp", amt)
            prize_texts.append(f"→ ⚡ {amt} EXP")
        elif choice == "osk":
            amt = random.randint(50, 100)
            add_to_account_field(accounts_cfg, user_id, "osk", amt)
            prize_texts.append(f"→ 💈 {amt} буст(ов)")
        elif choice == "ev_stones":
            amt = random.randint(50, 250)
            add_to_account_field(accounts_cfg, user_id, "ev_stones", amt)
            prize_texts.append(f"→ 🔥 {amt} респект(ов)")
        elif choice == "money":
            amt = random.randint(25_000_000, 50_000_000)
            add_to_account_field(accounts_cfg, user_id, "personal_account", amt)
            prize_texts.append(f"→ 💳 {amt:,}".replace(",", ".") + " RUB")
        else:
            amt = random.randint(25, 100)
            add_to_account_field(accounts_cfg, user_id, "uosk", amt)
            prize_texts.append(f"→ 📕 {amt} U-осколков")
        comment = "«Очарование новогодней магии! Такой подарок встретишь не каждый год — гордитесь своей удачей!»"

    else:  # Легендарное
        # Выбираем тип легенды: большая легенда / суперприз / новогодняя эволюция
        legend_choice = random.choices(
            ["legend_normal", "superprize", "evolution"],
            weights=[85, 10, 5],
            k=1
        )[0]

        if legend_choice == "superprize":
            sp_current = get_superprize_state()  # возвращает текущее значение (int)
            award_amount = int(sp_current)
            if award_amount <= 0:
                # аварийный запасной приз
                backup_amt = 50_000_000
                add_to_account_field(accounts_cfg, user_id, "personal_account", backup_amt)
                prize_texts.append(f"→ 🏺 Суперприз был пуст — запасной приз: {backup_amt:,} RUB".replace(",", "."))
            else:
                add_to_account_field(accounts_cfg, user_id, "t", award_amount)
                prize_texts.append(f"→ 🏺 Суперприз! Вам начислено {award_amount} ❄️")
            # сброс копилки до начального значения
            reset_superprize()
            comment = "«Вы разбудили зимнюю легендарную магию! Этот приз — настоящее сокровище Нового года. Гордитесь своим везением!»"
            legendary_broadcast = True

        elif legend_choice == "evolution":
            cfg = accounts_cfg
            cur_ev = int(cfg[user_id].get('ev_level', '0'))
            if cur_ev < EVO_MAX_LEVEL:
                cur_ev += 1
                cfg[user_id]['ev_level'] = str(cur_ev)
                prize_texts.append(f"→ 🎅 Новогодняя эволюция! Уровень эволюции теперь {cur_ev}")
            else:
                bonus = 500
                add_to_account_field(cfg, user_id, "osk", bonus)
                prize_texts.append(f"→ 🎅 Эволюция уже максимальна — вы получили {bonus} 💈")
            comment = "«Вы разбудили зимнюю легендарную магию! Этот приз — настоящее сокровище Нового года. Гордитесь своим везением!»"
            legendary_broadcast = True

        else:  # legend_normal — расширенный пул легендарных призов
            choice = random.choice([
                "t", "ball", "exp", "osk", "ev_stones",
                "personal_account", "losk"
            ])
            if choice == "t":
                amt = random.randint(1000, 1500)
                add_to_account_field(accounts_cfg, user_id, "t", amt)
                prize_texts.append(f"→ ❄️ {amt} снежинок (легендарный приз)")
            elif choice == "ball":
                amt = random.randint(500, 750)
                add_to_account_field(accounts_cfg, user_id, "ball", amt)
                prize_texts.append(f"→ 🧿 {amt} монет активности (легендарный приз)")
            elif choice == "exp":
                amt = random.randint(1000, 5000)
                add_to_account_field(accounts_cfg, user_id, "exp", amt)
                prize_texts.append(f"→ ⚡ {amt} EXP (легендарный приз)")
            elif choice == "osk":
                amt = random.randint(200, 250)
                add_to_account_field(accounts_cfg, user_id, "osk", amt)
                prize_texts.append(f"→ 💈 {amt} буст(ов) (легендарный приз)")
            elif choice == "ev_stones":
                amt = random.randint(500, 1000)
                add_to_account_field(accounts_cfg, user_id, "ev_stones", amt)
                prize_texts.append(f"→ 🔥 {amt} респект(ов) (легендарный приз)")
            elif choice == "personal_account":
                amt = random.randint(100_000_000, 150_000_000)
                add_to_account_field(accounts_cfg, user_id, "personal_account", amt)
                prize_texts.append(f"→ 💳 {amt:,}".replace(",", ".") + " RUB (легендарный приз)")
            else:  # losk
                amt = 100
                add_to_account_field(accounts_cfg, user_id, "losk", amt)
                prize_texts.append(f"→ 📒 {amt} L-осколков (легендарный приз)")

            comment = "«Вы разбудили зимнюю легендарную магию! Этот приз — настоящее сокровище Нового года. Гордитесь своим везением!»"
            legendary_broadcast = True

    # Сохраняем изменения аккаунта
    save_accounts(accounts_cfg)

    # Записываем в историю наград
    try:
        rewards_history = configparser.ConfigParser()
        if os.path.exists(REWARDS_HISTORY_FILE):
            with open(REWARDS_HISTORY_FILE, "r", encoding="utf-8") as hf:
                rewards_history.read_file(hf)
    except Exception:
        rewards_history = configparser.ConfigParser()

    if not rewards_history.has_section(user_id):
        rewards_history.add_section(user_id)
    unique_id = str(uuid.uuid4())
    history_desc = "; ".join(prize_texts) if prize_texts else "Неопределённая награда"
    rewards_history[user_id][unique_id] = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {rarity} ({code}) - {history_desc}"
    with open(REWARDS_HISTORY_FILE, "w", encoding="utf-8") as hf:
        rewards_history.write(hf)

    # Формируем сообщение пользователю
    header = "🎄 Награда мастерской 🎄"
    rarity_line = f"Редкость: {rarity} ({code})"
    content = "\n".join(prize_texts) if prize_texts else "→ Ничего не выпало."
    full_message = (
        f"{header}\n"
        f"{rarity_line}\n"
        f"Вам выпало:\n"
        f"{content}\n\n"
        f"{comment}"
    )
    # Картинки по редкости
    photo_map = {
    "Хлам": "xlam.png",
    "Обычное": "obiknoven.png",
    "Уникальное": "unikalinoe.png",
    "Легендарное": "legendarnoe.png"
    }

    photo_path = photo_map.get(rarity)
    if photo_path and os.path.exists(photo_path):
    # Неблокирующе отправляем фото; если хотим подпись в caption — передать caption=full_message
        send_photo_nonblocking(context.bot, update.effective_chat.id, photo_path)
    await update.message.reply_text(full_message, parse_mode="HTML")

    # При легендарной выдаче — оповещаем всех пользователей
    if legendary_broadcast:
        try:
            accounts_all = load_accounts()
            winner_nick = accounts_cfg[user_id].get('nick', user.full_name or str(user_id))
            broadcast_text = (
                f"🎆 ЛЕГЕНДАРНОЕ СОБЫТИЕ 🎆\n\n"
                f"Поздравляем <b>{winner_nick}</b> — он(а) только что расколол(а) снежинки и выйграл легендарный приз в праздничной мастерской!\n\n"
                f"📀 Редкость: <b>{rarity} ({code})</b>\n"
                f"🎁 Приз: {content}\n\n"
                f"Пусть это станет началом праздничного везения — гордимся и поздравляем победителя!"
            )
            await notify_all_users(context, broadcast_text, parse_mode="HTML")
        except Exception:
            # Игнорируем ошибки рассылки, чтобы не ломать основную логику
            pass

async def rdbonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /rdbonus — единоразово забрать еженедельные бонусы (ew_*) в расчётный день.
    Правила:
      - Работает только в день, который хранится в settings.ini (get_rd()).
      - Разовые: один пользователь может забрать бонус 1 раз за расчётный день.
      - Если у пользователя нет соответствующих характеристик (все ew_* == 0) —
        выводим дружелюбное сообщение и кнопку перехода в Центр обмена.
    """
    user = update.effective_user
    user_id = user.id
    user_id_str = str(user_id)

    # 1) Проверяем, установлен ли расчётный день
    rd = get_rd()
    if not rd:
        await update.message.reply_text("🔴 Расчётный день не установлен администратором. Попробуйте позже.")
        return

    today = datetime.now().date()
    rd_date = rd.date()

    # 2) Доступ только в сам расчётный день
    if today != rd_date:
        rd1 = rd - timedelta(days=6)
        await update.message.reply_text(
            "🔒 Команда доступна только в расчётный день.\n\n"
            f"📅 Период расчётной недели: {rd1.strftime('%d.%m.%Y')} - {rd.strftime('%d.%m.%Y')}\n"
            f"💽 Ближайший расчётный день: {rd.strftime('%d.%m.%Y')}\n\n"
            "ℹ️ Бонусы расчётного дня можно получить только в сам расчётный день командой /rdbonus."
        )
        return

    # 3) Проверяем — не забирал ли уже пользователь бонус в этот расчётный день
    claims = load_rd_claims()
    rd_section = rd.strftime("%Y-%m-%d")
    if not claims.has_section(rd_section):
        claims.add_section(rd_section)

    if claims.has_option(rd_section, user_id_str):
        claimed_at = claims[rd_section].get(user_id_str, "")
        await update.message.reply_text(f"✅ Вы уже получили бонус расчётного дня {rd.strftime('%d.%m.%Y')} (время: {claimed_at}).")
        return

    # 4) Берём характеристики пользователя
    user_chars = get_user_chars(user_id)
    if not user_chars:
        # Нет секции — попросим приобрести характеристики в центре обмена
        await update.message.reply_text(
            "❗ У вас не активированы характеристики, дающие еженедельные бонусы.\n"
            "Приобретите их в Центре обмена → Характеристики.",
            reply_markup=get_main_exchange_keyboard(user_id)
        )
        return

    try:
        ew_rub = int(user_chars.get("ew_rub", "0") or 0)
        ew_exp = int(user_chars.get("ew_exp", "0") or 0)
        ew_activ = int(user_chars.get("ew_activ", "0") or 0)
        ew_bust = int(user_chars.get("ew_bust", "0") or 0)
    except Exception:
        ew_rub = ew_exp = ew_activ = ew_bust = 0

    # Если все нули — просим купить в обменнике
    if ew_rub == 0 and ew_exp == 0 and ew_activ == 0 and ew_bust == 0:
        await update.message.reply_text(
            "❗ У вас нет еженедельных эффектов (ew_*). Приобретите подходящие характеристики в Центре обмена.",
            reply_markup=get_main_exchange_keyboard(user_id)
        )
        return

    # 5) Применяем бонусы к аккаунту пользователя
    accounts_cfg = load_accounts()
    user_section = str(user_id)
    if not accounts_cfg.has_section(user_section):
        await update.message.reply_text("❌ Ошибка: профиль пользователя не найден. Свяжитесь с администрацией.")
        return

    sec = accounts_cfg[user_section]
    applied_parts = []

    # перевод рублей (личный счёт)
    if ew_rub > 0:
        prev = int(sec.get("personal_account", "0"))
        sec["personal_account"] = str(prev + ew_rub)
        applied_parts.append(f"💳 +{ew_rub:,}".replace(",", ".") + " RUB")

    # EXP
    if ew_exp > 0:
        prev = int(sec.get("exp", "0"))
        sec["exp"] = str(prev + ew_exp)
        applied_parts.append(f"⚡ +{ew_exp}")

    # Монеты активности
    if ew_activ > 0:
        prev = int(sec.get("ball", "0"))
        sec["ball"] = str(prev + ew_activ)
        applied_parts.append(f"🧿 +{ew_activ}")

    # Бусты
    if ew_bust > 0:
        prev = int(sec.get("osk", "0"))
        sec["osk"] = str(prev + ew_bust)
        applied_parts.append(f"💈 +{ew_bust}")

    # Сохраняем accounts.ini
    save_accounts(accounts_cfg)

    # Сохраняем факт получения в rd_bonus.ini
    claims[rd_section][user_id_str] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_rd_claims(claims)

    # 6) Формируем красивый ответ пользователю
    header = "🎁 Вы получили награды расчётного дня!"
    body = "\n".join(applied_parts)
    footer = (
        "\n\nℹ️ Награды выдаются единоразово в расчётный день.\n"
        "Если вы ожидаете другие виды бонусов — обратитесь к администрации бота."
    )

    await update.message.reply_text(f"{header}\n\n{body}{footer}", reply_markup=get_back_keyboard())

async def ev(update, context):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    EVO_COSTS = [250, 500, 1000]
    EVO_REPORT_COINS = [1000, 2000, 3000]
    EVO_EXP_MULTIPLIERS = [1.25, 1.5, 2.0]
    EVO_MAX_LEVEL = 3

    # Эмодзи оформления (старые)
    EV_EMOJIS = ["🀄", "🎴", "🃏"]

    current_ev_level = int(user_info.get('ev_level', 0)) if user_info else 0
    user_level = int(user_info.get('level', 0)) if user_info else 0
    evo_stones = int(user_info.get('ev_stones', 0)) if user_info else 0
    personal_account = int(user_info.get('personal_account', 0)) if user_info else 0
    evball = int(user_info.get('evball', 0)) if user_info else 0

    next_ev_level = current_ev_level + 1 if current_ev_level < EVO_MAX_LEVEL else EVO_MAX_LEVEL
    evo_required_stones = EVO_COSTS[current_ev_level] if current_ev_level < EVO_MAX_LEVEL else EVO_COSTS[-1]
    coins_per_report = EVO_REPORT_COINS[current_ev_level] if current_ev_level < EVO_MAX_LEVEL else EVO_REPORT_COINS[-1]
    exp_multiplier = EVO_EXP_MULTIPLIERS[current_ev_level] if current_ev_level < EVO_MAX_LEVEL else EVO_EXP_MULTIPLIERS[-1]
    base_rate_after = 200_000 + (next_ev_level * 50_000)
    compensation = max(0, user_level - 50) * 5000
    required_level = EVO_REQUIRED_LEVELS[current_ev_level] if current_ev_level < EVO_MAX_LEVEL else EVO_REQUIRED_LEVELS[-1]

    # Эмодзи эволюции текущего уровня и следующего (старый стиль)
    current_ev_emoji = EV_EMOJIS[current_ev_level] if current_ev_level < len(EV_EMOJIS) else EV_EMOJIS[-1]
    next_ev_emoji = EV_EMOJIS[next_ev_level - 1] if (next_ev_level-1) < len(EV_EMOJIS) else EV_EMOJIS[-1]

    try:
        with open("ev.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
    except Exception:
        pass

    main_message = (
        "🧧‍ <b>Эволюция члена старшего состава.</b>\n\n"
        f"‍🎟 Ваш уровень эволюции: <b>{current_ev_level}</b>\n"
        f"🎫 Следующий уровень эволюции: <b>{next_ev_level}</b>\n\n"
        "🚅 <b>Что происходит при эволюции:</b>\n\n"
        "👼 Получение звания <b>«Хранитель»</b> в семье <b>СЕВЕРНЫЕ EMPIRE</b> и уникальный значок.\n"
        "🔄 Уровень и опыт обнуляются.\n"
        "💽 <b>Получение эволюционной льготы, которая в себя включает:</b>\n"
        f"💰 Базовая ставка после перехода будет повышена на <b>25%</b>\n"
        f"🧱 Компенсация уровня выше 50 монетами эволюции: <b>{compensation:,} 🪙 </b>\n"
        "☑️ Подтверждение уровня — после эволюции бесплатно.\n"
        "📦 Доступ к эволюционному эволавке через центр обмена.\n"
        "🔋 Повышенная выдача EXP при одобренном отчёте.\n"
        "🧮 Вывод средств без ограничений и повышенный лимит на вывод средств.\n"
        f"🪙 За каждый одобренный отчёт:  <b>{coins_per_report}</b> монет эволюции.\n\n"
        "<i>Подробнее о существующих эволюционных льготах можно узнать с помощью команды /lg</i>\n\n"
        f"🧭 Для перехода требуется респектов: <b>{evo_required_stones} 🔥</b>\n"
        f"🧬 У вас респектов: <b>{evo_stones} 🔥</b>\n"
        f"🧗 Для эволюции необходим минимум <b>{required_level}</b> уровень, у вас: <b>{user_level}</b>\n\n"
        f"🃏 Для запуска эволюции – используйте <b>/evolution</b>\n"
    )
    await update.message.reply_text(main_message, reply_markup=get_back_to_function_keyboard(), parse_mode="HTML")
    
async def evolution_handler(update, context):
    user_id = str(update.effective_user.id)
    user_info = get_user_info(user_id)
    if not user_info:
        await update.message.reply_text("❌ Ошибка: пользователь не найден.")
        return

    level = int(user_info.get('level', 0))
    ev_level = int(user_info.get('ev_level', 0))
    ev_stones = int(user_info.get('ev_stones', 0))
    personal_account = int(user_info.get('personal_account', 0))
    evball = int(user_info.get('evball', 0))
    min_level = EVO_REQUIRED_LEVELS[ev_level] if ev_level < len(EVO_REQUIRED_LEVELS) else EVO_REQUIRED_LEVELS[-1]

    # --- Проверка ошибок ---
    if personal_account < 0:
        await update.message.reply_text("❌ Ошибка. Ваш личный счет отрицательный! Эволюция недоступна.")
        return
    if level < min_level:
        await update.message.reply_text(
        f"❌ Ошибка. Для эволюции {ev_level+1} уровня нужен минимум {min_level} уровень!")
        return
    if ev_level >= EVO_MAX_LEVEL:
        await update.message.reply_text("🃏 Ошибка. У вас максимальный уровень эволюции!")
        return
    evo_require = EVO_COSTS[ev_level]
    if ev_stones < evo_require:
        await update.message.reply_text(f"❌ Ошибка. Недостаточно респектов! Нужно {evo_require}, у вас: {ev_stones}.")
        return

    next_ev = ev_level + 1
    compensation = max(0, level - 50) * 5000
    compensation_fmt = fmt(compensation)
    coins_per_report = EVO_REPORT_COINS[ev_level]
    base_rate_increase = next_ev * 50000
    base_rate_increase_fmt = fmt(base_rate_increase)

    # Сохраняем стадию подтверждения
    context.user_data['evolution_stage'] = 1

    confirm_text = (
        "🧧 <b>Вы точно хотите выполнить эволюцию?</b>\n"
        "Функция необратима.\n\n"
        f"🎟 Ваш уровень эволюции: <b>{ev_level}</b>\n"
        f"🎫 Следующий уровень эволюции: <b>{next_ev}</b>\n"
        "После активации этой функции произойдет:\n"
        "🔺 <b>Обнуление уровня и опыта.</b>\n"
        f"🔺 <b>Компенсация уровня выше 50:</b> <b>{compensation_fmt}</b> монет эволюции.\n"
        "🔺 <b>Получение звания Хранитель.</b>\n\n"
        "💽 <b>Получение эволюционной льготы, которая в себя включает:</b>\n"
        f"🔺 <b>Ваша базовая ставка увеличится на 25% с каждым уровнем эволюции.</b>.\n"
        f"🔺 <b>За каждый одобренный отчёт будете получать {coins_per_report} монет эволюции.</b>\n"
        "🔺 <b>Подтверждение уровня станет бесплатным.</b>\n"
        "🔺 <b>Доступ к эволавке и уникальному значку.</b>\n"
        "🔺 <b>Повышенная выдача EXP при одобренном отчёте.</b>\n"
        "🔺 <b>Вывод средств без ограничений и повышенный лимит на вывод средств.</b>\n"
        "🔔 <b>Все пользователи узнают о вашей эволюции!</b>\n\n"
        "🔴 Потвердите действие 1/3:"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Да", callback_data="evolution_yes")],
        [InlineKeyboardButton("❌ Нет", callback_data="evolution_no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(confirm_text, reply_markup=reply_markup, parse_mode="HTML")

async def evolution_callback_handler(update, context):
    query = update.callback_query
    user_id = str(query.from_user.id)
    user_info = get_user_info(user_id)
    if not user_info:
        await query.edit_message_text("❌ Ошибка: пользователь не найден.")
        return

    data = query.data
    stage = context.user_data.get('evolution_stage', 1)

    if data == "evolution_no":
        context.user_data.pop('evolution_stage', None)
        await query.edit_message_text("❌ Операция эволюции отменена.", parse_mode="HTML")
        return

    if data == "evolution_yes":
        # Переход на следующие стадии (1 -> 2 -> 3)
        if stage < 3:
            context.user_data['evolution_stage'] = stage + 1
            confirm_text = f"🔴 Потвердите действие {stage+1}/3:"
            keyboard = [
                [InlineKeyboardButton("✅ Да", callback_data="evolution_yes")],
                [InlineKeyboardButton("❌ Нет", callback_data="evolution_no")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(confirm_text, reply_markup=reply_markup)
            return

        # --- ЭТАП ПРОВЕДЕНИЯ ЭВОЛЮЦИИ ---
        ev_level = int(user_info.get('ev_level', 0))
        level = int(user_info.get('level', 0))
        ev_stones = int(user_info.get('ev_stones', 0))
        evball = int(user_info.get('evball', 0))
        personal_account = int(user_info.get('personal_account', 0))

        # Проверка на максимальный evo-уровень
        if ev_level >= EVO_MAX_LEVEL:
            await query.edit_message_text("🃏 Ошибка. У вас максимальный уровень эволюции!")
            context.user_data.pop('evolution_stage', None)
            return

        # Проверка на минимальный обычный уровень
        min_level = EVO_REQUIRED_LEVELS[ev_level] if ev_level < len(EVO_REQUIRED_LEVELS) else EVO_REQUIRED_LEVELS[-1]
        if level < min_level:
            await query.edit_message_text(
                f"❌ Ошибка. Для эволюции {ev_level+1} уровня нужен минимум {min_level} уровень!")
            context.user_data.pop('evolution_stage', None)
            return

        # Проверка на отрицательный персональный счет
        if personal_account < 0:
            await query.edit_message_text("❌ Ошибка. Ваш личный счет отрицательный! Эволюция недоступна.")
            context.user_data.pop('evolution_stage', None)
            return

        # Проверка на достаточность камней эволюции
        evo_require = EVO_COSTS[ev_level]
        if ev_stones < evo_require:
            await query.edit_message_text(
                f"❌ Ошибка. Недостаточно респектов! Нужно {evo_require}, у вас: {ev_stones}.")
            context.user_data.pop('evolution_stage', None)
            return

        next_ev = ev_level + 1
        compensation = max(0, level - 50) * 5000
        exp_multiplier = EVO_EXP_MULTIPLIERS[ev_level]
        base_rate_increase = 50000

        # Сохраняем изменения в accounts.ini
        accounts_cfg = load_accounts()
        sec = accounts_cfg[user_id]
        sec['ev_level'] = str(next_ev)
        sec['ev_stones'] = str(ev_stones - evo_require)
        sec['level'] = "0"
        sec['exp'] = "0"
        sec['lvlconf'] = "0"
        sec['evball'] = str(evball + compensation)
        save_accounts(accounts_cfg)

        # Сохраняем эво-ускоритель и ликвидность в user_characteristics.ini
        ensure_user_chars(user_id)
        ch_cfg = load_user_chars()
        if not ch_cfg.has_section(user_id):
            ch_cfg.add_section(user_id)
        ch_cfg[user_id]['exp_multiplier'] = str(exp_multiplier)
        ch_cfg[user_id]['max_zp'] = "1"
        save_user_chars(ch_cfg)

        # Персональное сообщение
        personal_text = (
            f"🎉 <b>Эволюция выполнена!</b> 🎉\n\n"
            f"🃏 Ваш уровень эволюции теперь: <b>{next_ev}</b>\n"
            "🔄 Уровень и опыт обнулены.\n"
            f"💠 Компенсация: <b>{fmt(compensation)}</b> монет эволюции\n"
            "👼 Вы получили звание <b>Хранитель</b>.\n"
            f"💽 Вы получили эволюционную льготу <b>{next_ev}</b> уровня.\n"
        )
        await query.edit_message_text(personal_text, parse_mode="HTML")

        # Массовое оповещение всем пользователям
        broadcast_text = (
            "✨ <b>ЭВОЛЮЦИОННО!</b> ✨\n"
            f"👤 <b>{sec.get('nick')}</b> повысил свой уровень эволюции до <b>{next_ev}</b> и получил эволюционные льготы.\n"
            "«Чтобы дойти до цели, надо прежде всего идти» — О. де Бальзак.\n"
        )
        await notify_all_users(context, broadcast_text, parse_mode="HTML")

        # Конец операции
        context.user_data.pop('evolution_stage', None)

def get_privilege_info(priv_id, user_info):
    ev_level = int(user_info.get("ev_level", 0))

    if priv_id == "lg_1":
        return (
            "👑 <b>Лидер рейтинга (льгота).</b>\n"
            "1) Временная льгота, действует для лидера рейтинга по итогам расчётной недели в течении следующей недели.\n"
            "2) Ваша базовая ставка увеличена на <b>25%</b>\n"
            "3) Увеличенная выдача EXP при одобренном отчёте на <b>25%.</b>\n"
            "4) При выдаче льготы начисляется <b>1.000 ед. снежинок</b> и <b>1К EXP.</b>\n"
            "5) При выдаче льготы начисляется <b>100 ед. респектов.</b>\n"
            "6) Лимит на вывод увеличен на <b>50.000.000 RUB.</b>\n"
            "7) Комиссия при переводах уменьшена на <b>5%</b>\n\n"
            "Для получения следующего уровня льготы, необходимо выполнить <b>следующие условия:</b>\n"
            "1) Занять <b>первое место</b> по рейтинговой системе.\n"
            "2) Набрать <b>превосходную активность</b> за расчётную неделю.\n\n"
            "<i>Эффект увеличенной выдачи EXP не суммируется.</i>\n"
            "<i>После выполнения условий, обратитесь к лидеру семьи, чтобы получить льготу.</i>"
        )
    elif priv_id == "lg_2":
        return (
            "🌟 <b>Старший заместитель (льгота).</b>\n"
            "1) Права администратора 2 уровня и эксклюзивные доплаты.\n"
            "2) Ваша базовая ставка увеличена на <b>25%</b>\n"
            "3) Увеличенная выдача EXP при одобренном отчёте на <b>25%.</b>\n"
            "4) Вывод средств без ограничений.\n"
            "5) Лимит на вывод увеличен на <b>50.000.000 RUB.</b>\n\n"
            "Для получения следующего уровня льготы, необходимо выполнить <b>следующие условия:</b>\n"
            "1) Иметь должность <b>Старший заместитель.</b>\n\n"
            "<i>Эффект увеличенной выдачи EXP не суммируется.</i>\n"
            "<i>После выполнения условий льгота будет выдана автоматически.</i>"
        )
    elif priv_id == "lg_3":
        return (
            "🀄 <b>Эволюция первая (льгота).</b>\n"
            "1) Уникальный значок и звание <b>Хранитель</b>.\n"
            "2) Ваша базовая ставка увеличена на <b>25%</b>\n"
            "3) Подтверждение уровня - <b>бесплатно.</b>\n"
            "4) Эволюционные монеты за каждый отчет в количестве <b>1.000 ед.</b> и доступ к эволавке.\n"
            "5) Увеличенная выдача EXP при одобренном отчёте на <b>25%.</b>\n"
            "6) Вывод средств без ограничений и лимит на вывод средств увеличен на 50.000.000 RUB.\n\n"
            "Для получения следующего уровня льготы, необходимо выполнить <b>следующие условия:</b>\n"
            "1) Иметь <b>250</b> респектов.\n"
            "2) Иметь минимум <b>50</b> уровень пользователя.\n\n"
            "<i>Эффект увеличенной выдачи EXP не суммируется.</i>\n"
            "<i>После выполнения условий нужно пройти эволюцию с помощью команды /evolution</i>"
        )
    elif priv_id == "lg_4":
        return (
            "🎴 <b>Эволюция вторая (льгота).</b>\n"
            "1) Уникальный значок и звание <b>Хранитель</b>.\n"
            "2) Ваша базовая ставка увеличена на <b>50%</b>\n"
            "3) Подтверждение уровня - <b>бесплатно.</b>\n"
            "4) Эволюционные монеты за каждый отчет в количестве <b>2.000 ед.</b> и доступ к эволавке.\n"
            "5) Увеличенная выдача EXP при одобренном отчёте на <b>50%.</b>\n"
            "6) Вывод средств без ограничений и лимит на вывод средств увеличен на 75.000.000 RUB.\n\n"
            "Для получения следующего уровня льготы, необходимо выполнить <b>следующие условия:</b>\n"
            "1) Пройти первую эволюцию.\n"
            "2) Иметь <b>500</b> респектов.\n"
            "3) Иметь минимум <b>75</b> уровень пользователя.\n\n"
            "<i>Эффект увеличенной выдачи EXP не суммируется.</i>\n"
            "<i>После выполнения условий нужно пройти эволюцию с помощью команды /evolution</i>"
        )
    elif priv_id == "lg_5":
        return (
            "🃏 <b>Эволюция третья (льгота).</b>\n"
            "1) Уникальный значок и звание <b>Хранитель</b>.\n"
            "2) Ваша базовая ставка увеличена на <b>75%</b>\n"
            "3) Подтверждение уровня - <b>бесплатно.</b>\n"
            "4) Эволюционные монеты за каждый отчет в количестве <b>3.000 ед.</b> и доступ к эволавке.\n"
            "5) Увеличенная выдача EXP при одобренном отчёте на <b>100%.</b>\n"
            "6) Вывод средств без ограничений и лимит на вывод средств увеличен на 100.000.000 RUB.\n\n"
            "Для получения следующего уровня льготы, необходимо выполнить <b>следующие условия:</b>\n"
            "1) Пройти первую и вторую эволюцию.\n"
            "2) Иметь <b>1000</b> респектов.\n"
            "3) Иметь минимум <b>100</b> уровень пользователя.\n\n"
            "<i>Эффект увеличенной выдачи EXP не суммируется.</i>\n"
            "<i>После выполнения условий нужно пройти эволюцию с помощью команды /evolution</i>"
        )
    elif priv_id == "lg_6":
        return (
            "🧞 <b>Эволампа джина.</b>\n"
            "При активации льготы Вы получаете на выбор три случайные легендарные характеристики.\n"
            "Для получения следующего уровня льготы, необходимо выполнить <b>следующие условия:</b>\n"
            "1) Иметь эволюцию.\n"
            "2) Купить льготу в эволавке.\n"
            "<i>После выполнения условий, для выдачи свяжитесь с лидером семьи.</i>"
        )
    elif priv_id == "lg_7":
        return (
            "🎤 <b>Пиарщик (льгота).</b>\n"
            "1) Данная льгота при использовании активирует еженедельную компенсацию оплаты сообщений в VIP ADV чат в размере <b>50 ед. бустов.</b>\n\n"
            "Для получения следующего уровня льготы, необходимо выполнить <b>следующие условия:</b>\n"
            "1) Быть ответственным за доплату  <b>пиарщик VIP чата.</b>\n\n"
            "<i>Эффект компенсации бустами не суммируется.</i>\n"
            "<i>Активация льготы с помощью команды /pactivate</i>\n"
            "<i>Награды выдаются еженедельно в расчётный день с помощью команды /rdbonus</i>"
        )
    elif priv_id == "lg_8":
        return (
            "🕹 <b>Семейный майнинг (льгота).</b>\n"
            "1) Данная льгота при использовании активирует еженедельную компенсацию затрат на охлаждающие жидкости в размере <b>200 ед. бустов.</b>\n\n"
            "Для получения следующего уровня льготы, необходимо выполнить <b>следующие условия:</b>\n"
            "1) Быть ответственным за доплату  <b>семейный майнинг.</b>\n\n"
            "<i>Эффект компенсации бустами не суммируется.</i>\n"
            "<i>Активация льготы с помощью команды /mactivate</i>\n"
            "<i>Награды выдаются еженедельно в расчётный день с помощью команды /rdbonus</i>"
        )
    elif priv_id == "lg_9":
        return (
            "📈 <b>Коммерсант (льгота).</b>\n"
            "1) Временная льгота, действует для члена старшего состава, который по итогам расчётной недели продал рекордное количество рангов.\n"
            "2) Лимит на вывод увеличен на <b>100.000.000 RUB.</b>\n"
            "3) Комиссия при переводах уменьшена на <b>5%</b>\n"
            "4) При выдаче льготы начисляется <b>500 ед. снежинок</b> и <b>500 EXP.</b>\n"
            "5) При выдаче льготы начисляется <b>50 ед. респектов.</b>\n\n"
            "Для получения следующего уровня льготы, необходимо выполнить <b>следующие условия:</b>\n"
            "1) Занять <b>первое место</b> по продажам рангов (10 и более).\n"
            "2) Набрать <b>превосходную активность</b> за расчётную неделю.\n\n"
            "<i>После выполнения условий, обратитесь к лидеру семьи, чтобы получить льготу.</i>"
        )
    elif priv_id == "lg_10":
        return "🕹 <b>Семейный майнинг (льгота).</b>\nПока нет подробностей."
    else:
        return "ℹ️ Информация о льготе не найдена."
    
async def lg_main_menu(query):
    kb = [
        [InlineKeyboardButton("⚙️ Системные", callback_data="lg_cat_system")],
        [InlineKeyboardButton("🧬 Эволюционные", callback_data="lg_cat_evo")],
        [InlineKeyboardButton("🎉 Праздничные", callback_data="lg_cat_event")],
        [InlineKeyboardButton("📦 Архивные", callback_data="lg_cat_archive")],
        [InlineKeyboardButton("🚪 Выйти", callback_data="lg_exit")]
    ]

    await query.edit_message_text(
        "💽 <b>Меню льгот.</b>\n🏵 Нажми на интересующую категорию льгот, чтобы узнать подробности:",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

async def lg_handler(update: Update, context: CallbackContext):
    # первый вход в меню → есть update.message
    kb = [
        [InlineKeyboardButton("⚙️ Системные", callback_data="lg_cat_system")],
        [InlineKeyboardButton("🧬 Эволюционные", callback_data="lg_cat_evo")],
        [InlineKeyboardButton("🎉 Праздничные", callback_data="lg_cat_event")],
        [InlineKeyboardButton("📦 Архивные", callback_data="lg_cat_archive")],
        [InlineKeyboardButton("🚪 Выйти", callback_data="lg_exit")]
    ]

    await update.message.reply_text(
        "💽 <b>Меню льгот.</b>\n🏵 Нажми на интересующую категорию льгот, чтобы узнать подробности:",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

# ================================
#   ПОДМЕНЮ — СИСТЕМНЫЕ
# ================================
async def system_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    kb = [
        [InlineKeyboardButton("👑 Лидер рейтинга", callback_data="lg_1")],
        [InlineKeyboardButton("🌟 Старший заместитель", callback_data="lg_2")],
        [InlineKeyboardButton("🎤 Пиарщик", callback_data="lg_7")],
        [InlineKeyboardButton("🕹 Семейный майнинг", callback_data="lg_8")],
        [InlineKeyboardButton("📈 Коммерсант", callback_data="lg_9")],
        [InlineKeyboardButton("🔙 Назад", callback_data="lg_back_main")]
    ]

    await query.edit_message_text(
        "⚙️ <b>Системные льготы.</b>\n🏵 Нажми на интересующую льготу, чтобы узнать подробности:",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

# ================================
#   ПОДМЕНЮ — ЭВОЛЮЦИОННЫЕ
# ================================
async def evo_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    kb = [
            [InlineKeyboardButton("🀄 Эволюция первая", callback_data="lg_3")],
            [InlineKeyboardButton("🎴 Эволюция вторая", callback_data="lg_4")],
            [InlineKeyboardButton("🃏 Эволюция третья", callback_data="lg_5")],
            [InlineKeyboardButton("🧞 Эволампа джина", callback_data="lg_6")],
            [InlineKeyboardButton("🔙 Назад", callback_data="lg_back_main")]
    ]

    await query.edit_message_text(
        "🧬 <b>Эволюционные льготы.</b>\n🏵 Нажми на интересующую льготу, чтобы узнать подробности:",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )


# ================================
#   ПОДМЕНЮ — ПРАЗДНИЧНЫЕ (пусто)
# ================================
async def event_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    kb = [[InlineKeyboardButton("🔙 Назад", callback_data="lg_back_main")]]

    await query.edit_message_text(
        "🎉 <b>Праздничные льготы.</b>\n🏵 Нажми на интересующую льготу, чтобы узнать подробности:\n\n<b>Льгот данного типа не найдено.</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )


# ================================
#   ПОДМЕНЮ — АРХИВНЫЕ (пусто)
# ================================
async def archive_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    kb = [[InlineKeyboardButton("🔙 Назад", callback_data="lg_back_main")]]

    await query.edit_message_text(
        "📦 <b>Архивные льготы.</b>\n🏵 Нажми на интересующую льготу, чтобы узнать подробности:\n\n<b>Льгот данного типа не найдено.</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )


# ================================
#   РОУТЕР CALLBACK-КНОПОК
# ================================
async def callback_router(update: Update, context: CallbackContext):
    query = update.callback_query
    # отвечаем сразу, чтобы снять спиннер у пользователя
    await query.answer()
    data = query.data

    # Категории
    if data == "lg_cat_system":
        return await system_menu(update, context)

    if data == "lg_cat_evo":
        return await evo_menu(update, context)

    if data == "lg_cat_event":
        return await event_menu(update, context)

    if data == "lg_cat_archive":
        return await archive_menu(update, context)

    # Назад
    if data == "lg_back_main":
        return await lg_main_menu(query)

    # Выйти
    if data == "lg_exit":
        return await lg_exit_handler(update, context)

    # Льготы
    if data.startswith("lg_"):
        # Берём реальные данные пользователя
        user_info = context.user_data.get("user_info", {})

        # Получаем текст льготы
        info_text = get_privilege_info(data, user_info)

        # Отправляем пользователю текст с кнопкой "Назад"
        await query.edit_message_text(
            info_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="lg_back_main")]
            ])
        )
        return

async def lg_exit_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    # Полностью удалить текущее сообщение
    await query.delete_message()

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    admin_level = int(user_info.get('is_admin', 0)) if user_info else 0

    if admin_level <= 0:
        await update.message.reply_text("❌ У вас нет доступа к просмотру команд администрации бота.")
        return

    text = (
        "🛠 <b>Админ-панель</b>\n"
        "Доступные команды:\n\n"
        "1. <b>/ahelp</b> — команды панели администратора.\n"
        "2. <b>/aactive</b> — глобальная активность пользователей.\n"
        "3. <b>/setpromocode [PROMO] [ball][money][exp][shards][tikvi][ev_stones][evball]</b> — создать промокод (для админов 3 уровня)\n"
        "4. <b>/resetpromocode [PROMO]</b> — удалить промокод (для админов 3 уровня)\n"
        "5. <b>/leader [NAME]</b> — выдать льготу: лидер рейтинга (для админов 3 уровня)\n"
        "6. <b>/leader 0</b> — обнулить льготу: лидер рейтинга (для админов 3 уровня)\n"
        "7. <b>/szam [NAME]</b> — выдать льготу: старший заместитель (для админов 3 уровня)\n"
        "8. <b>/szam 0</b> — обнулить льготу: старший заместитель (для админов 3 уровня)\n"
        "9. <b>/piarvr [NAME]</b> — выдать льготу: пиарщик VIP ADV (для админов 3 уровня)\n"
        "10. <b>/piarvr 0</b> — обнулить льготу: пиарщик VIP ADV (для админов 3 уровня)\n"
        "11. <b>/mining [NAME]</b> — выдать льготу: семейный майнинг (для админов 3 уровня)\n"
        "12. <b>/mining 0</b> — обнулить льготу: семейный майнинг (для админов 3 уровня)\n"
        "13. <b>/respect [NAME]</b> — выдать похвалу: 5 респектов ежедневно (для админов 2 и 3 уровня)\n"
        "14. <b>/setsinfo [ID]</b> — информация о наборе - включая лимиты (для админов 2 и 3 уровня)\n"
        "15. <b>/setslimit [ID] [LIMIT]</b> — изменить лимит набора (для админов 3 уровня)\n"
        "\nТакже доступны функции через главное меню и админ-панель."
    )

    await update.message.reply_text(text, parse_mode="HTML")

async def leader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    if int(user_info.get('is_admin', 0)) < 3:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return

    if not context.args:
        await update.message.reply_text(
            "Используйте:\n/leader <никнейм пользователя> — выдать льготу лидера\n/leader 0 — снять льготу у текущего лидера"
        )
        return

    leader_candidate = " ".join(context.args).strip()

    # ФУНКЦИЯ для работы с settings.ini
    def get_leader_id():
        cfg = load_settings()
        if cfg.has_section("leader") and "id" in cfg["leader"]:
            return cfg["leader"]["id"]
        return None

    def set_leader_id(uid):
        cfg = load_settings()
        if not cfg.has_section("leader"):
            cfg.add_section("leader")
        cfg["leader"]["id"] = str(uid)
        save_settings(cfg)

    def clear_leader_id():
        cfg = load_settings()
        if cfg.has_section("leader") and "id" in cfg["leader"]:
            cfg.remove_option("leader", "id")
            save_settings(cfg)

    accounts = load_accounts()

    if leader_candidate == "0":
        # Снять льготу у текущего лидера
        cur_leader_id = get_leader_id()
        if not cur_leader_id or not accounts.has_section(cur_leader_id):
            await update.message.reply_text("❌ Действующий лидер не найден.")
            return

        # Обнуляем льготу
        accounts[cur_leader_id]["lgrating"] = "0"
        accounts[cur_leader_id]["comission"] = "0"
        save_accounts(accounts)
        ensure_user_chars(cur_leader_id)
        user_chars = load_user_chars()
        user_chars[cur_leader_id]["exp_multiplier"] = "1.0"
        save_user_chars(user_chars)
        clear_leader_id()
        # Сообщение админу и пользователю-бывшему-лидеру
        try:
            leader_nick = accounts[cur_leader_id].get("nick", cur_leader_id)
            await context.bot.send_message(
                int(cur_leader_id),
                "ℹ️ Ваша льгота лидера рейтинга была обнулена администрацией."
            )
        except Exception:
            pass
        await update.message.reply_text(f"✅ Льгота лидера снята с пользователя {leader_nick}.")
        return

    # --- ВЫДАЧА ЛЬГОТЫ НОВОМУ ЛИДЕРУ ---
    # Сначала проверить, выбран ли уже лидер этой недели (settings.ini)
    active_leader_id = get_leader_id()
    if active_leader_id and accounts.has_section(active_leader_id):
        leader_nick = accounts[active_leader_id].get("nick", active_leader_id)
        await update.message.reply_text(
            f"❌ На этой неделе уже выбран лидер: {leader_nick} (ID: {active_leader_id})\n"
            "Сначала снимите льготу у действующего лидера командой <code>/leader 0</code>.",
            parse_mode="HTML"
        )
        return

    # Поиск пользователя по нику (без учета регистра)
    target_nick = leader_candidate
    target_id = None
    for sec in accounts.sections():
        if accounts[sec].get("nick", "").lower() == target_nick.lower():
            target_id = sec
            break

    if not target_id:
        await update.message.reply_text("❌ Пользователь с таким ником не найден.")
        return

    # Проверить, не является ли пользователь уже лидером
    if accounts[target_id].get("lgrating", "0") == "1":
        await update.message.reply_text(
            f"❗ Пользователь {accounts[target_id].get('nick', target_id)} уже имеет льготу лидера."
        )
        return

    # Выдать льготу: lgrating = 1 и exp_multiplier >= 1.25
    accounts[target_id]["lgrating"] = "1"
    save_accounts(accounts)
    ensure_user_chars(target_id)
    user_chars = load_user_chars()
    cur_mult = float(user_chars[target_id].get("exp_multiplier", "1.0"))
    if cur_mult < 1.25:
        user_chars[target_id]["exp_multiplier"] = "1.25"
        save_user_chars(user_chars)
    set_leader_id(target_id)

    # ----- ДОБАВЬТЕ ЭТО СЮДА!!! -----
    # Начислить 1.000 тыкв и 1.000 EXP, 5 камней эволюции
    accounts[target_id]["t"] = str(int(accounts[target_id].get("t", 0)) + 1000) #потом поменять на снежинки (пока бусты)
    accounts[target_id]["exp"] = str(int(accounts[target_id].get("exp", 0)) + 1000)
    accounts[target_id]["comission"] = str(int(accounts[target_id].get("comission", 0)) + 5)
    accounts[target_id]["ev_stones"] = str(int(accounts[target_id].get("ev_stones", 0)) + 100)
    save_accounts(accounts)

    leader_nick = accounts[target_id].get("nick", target_id)
    try:
        await context.bot.send_message(
            int(target_id),
            "🏆 <b>Вам выдана льгота «Лидер рейтинга»!</b>\n\n"
            "<i>Примечание: информация о премуществах всех видов льгот доступна с помощью команды /lg</i>\n"
            "<i>Активна до следующей смены льготы лидера.</i>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await update.message.reply_text(
        f"✅ Льгота лидера выдана пользователю {leader_nick}.\n",
        parse_mode="HTML"
    )

async def szam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)

    # Проверка прав: только админ 3 уровня
    if int(user_info.get('is_admin', 0)) < 3:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return

    if not context.args:
        await update.message.reply_text(
            "Используйте:\n"
            "/szam <никнейм пользователя> — выдать льготу Старшего заместителя\n"
            "/szam 0 — снять льготу у текущего обладателя"
        )
        return

    szam_candidate = " ".join(context.args).strip()

    # --- Работа с settings.ini ---
    def get_szam_id():
        cfg = load_settings()
        if cfg.has_section("szam") and "id" in cfg["szam"]:
            return cfg["szam"]["id"]
        return None

    def set_szam_id(uid):
        cfg = load_settings()
        if not cfg.has_section("szam"):
            cfg.add_section("szam")
        cfg["szam"]["id"] = str(uid)
        save_settings(cfg)

    def clear_szam_id():
        cfg = load_settings()
        if cfg.has_section("szam") and "id" in cfg["szam"]:
            cfg.remove_option("szam", "id")
            save_settings(cfg)

    def normalize_nick(nick: str) -> str:
        if not isinstance(nick, str):
            nick = str(nick)
        nick = nick.strip().lower().replace("ё", "е")
        nick = " ".join(nick.split())
        nick = unicodedata.normalize('NFKC', nick)
        return nick

    accounts = load_accounts()

    # --- Снятие льготы ---
    if szam_candidate == "0":
        cur_szam_id = get_szam_id()
        if not cur_szam_id or not accounts.has_section(cur_szam_id):
            await update.message.reply_text("❌ Действующий Старший заместитель не найден.")
            return

        accounts[cur_szam_id]["szam"] = "0"
        accounts[cur_szam_id]["is_admin"] = "0"
        accounts[cur_szam_id]["position"] = "Заместитель"
        save_accounts(accounts)

        ensure_user_chars(cur_szam_id)
        user_chars = load_user_chars()
        user_chars[cur_szam_id]["exp_multiplier"] = "1.0"
        user_chars[cur_szam_id]["max_zp"] = "0"
        save_user_chars(user_chars)
        clear_szam_id()

        try:
            szam_nick = accounts[cur_szam_id].get("nick", cur_szam_id)
            await context.bot.send_message(
                int(cur_szam_id),
                "ℹ️ Ваша льгота Старшего заместителя была обнулена администрацией."
            )
        except Exception:
            pass

        await update.message.reply_text(f"✅ Льгота Старшего заместителя снята с пользователя {szam_nick}.")
        return

    # --- Выдача льготы ---
    active_szam_id = get_szam_id()
    if active_szam_id and accounts.has_section(active_szam_id):
        szam_nick = accounts[active_szam_id].get("nick", active_szam_id)
        await update.message.reply_text(
            f"❌ На данный момент уже выбран Старший заместитель: {szam_nick} (ID: {active_szam_id})\n"
            "Сначала снимите льготу у действующего с помощью <code>/szam 0</code>.",
            parse_mode="HTML"
        )
        return

    # Поиск пользователя по нику (нормализованный)
    target_nick = normalize_nick(szam_candidate)
    target_id = None
    for sec in accounts.sections():
        acc_nick = normalize_nick(accounts[sec].get("nick", ""))
        if acc_nick == target_nick:
            target_id = sec
            break

    if not target_id:
        await update.message.reply_text("❌ Пользователь с таким ником не найден.")
        return

    # Проверка, не является ли уже СЗАМ
    if accounts[target_id].get("szam", "0") == "1":
        await update.message.reply_text(
            f"❗ Пользователь {accounts[target_id].get('nick', target_id)} уже обладает льготой Старшего заместителя."
        )
        return

    # Выдаем льготу
    accounts[target_id]["szam"] = "1"
    accounts[target_id]["is_admin"] = "2"  # например, повышаем уровень админа
    accounts[target_id]["position"] = "Старший заместитель"
    save_accounts(accounts)

    ensure_user_chars(target_id)
    user_chars = load_user_chars()
    # Устанавливаем exp_multiplier >=1.25
    cur_mult = float(user_chars[target_id].get("exp_multiplier", "1.0"))
    if cur_mult < 1.25:
        user_chars[target_id]["exp_multiplier"] = "1.25"
    user_chars[target_id]["max_zp"] = "1"
    save_user_chars(user_chars)

    set_szam_id(target_id)
    save_accounts(accounts)

    szam_nick = accounts[target_id].get("nick", target_id)
    try:
        await context.bot.send_message(
            int(target_id),
            "🏆 <b>Вам выдана льгота «Старший заместитель»!</b>\n\n"
            "<i>Информация о преимуществах доступна с помощью команды /lg</i>\n"
            "<i>Активна до следующей смены льготы СЗАМ.</i>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await update.message.reply_text(
        f"✅ Льгота Старшего заместителя выдана пользователю {szam_nick}.\n",
        parse_mode="HTML"
    )


async def piarvr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)

    # Нужен 3 уровень админки для выдачи
    if int(user_info.get('is_admin', 0)) < 3:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return

    if not context.args:
        await update.message.reply_text(
            "Используйте:\n/piarvr <никнейм пользователя> — выдать льготу пиара VIP ADV\n/piarvr 0 — снять льготу у текущего обладателя"
        )
        return

    piarvr_candidate = " ".join(context.args).strip()

    # --- Работа с settings.ini для отслеживания текущего szam ---
    def get_piarvr_id():
        cfg = load_settings()
        if cfg.has_section("piarvr") and "id" in cfg["piarvr"]:
            return cfg["piarvr"]["id"]
        return None

    def set_piarvr_id(uid):
        cfg = load_settings()
        if not cfg.has_section("piarvr"):
            cfg.add_section("piarvr")
        cfg["piarvr"]["id"] = str(uid)
        save_settings(cfg)

    def clear_piarvr_id():
        cfg = load_settings()
        if cfg.has_section("piarvr") and "id" in cfg["piarvr"]:
            cfg.remove_option("piarvr", "id")
            save_settings(cfg)

    accounts = load_accounts()

    if piarvr_candidate == "0":
        # Снять льготу у текущего СЗАМА
        cur_piarvr_id = get_piarvr_id()
        if not cur_piarvr_id or not accounts.has_section(cur_piarvr_id):
            await update.message.reply_text("❌ Действующий ответственный за доплату пиарщик VIP ADV не найден.")
            return

        # Обнуляем льготу
        accounts[cur_piarvr_id]["piarvr"] = "0"
        save_accounts(accounts)

        ensure_user_chars(cur_piarvr_id)
        user_chars = load_user_chars()
        # при снятии льготы — ew_bust = 0
        user_chars[cur_piarvr_id]["ew_bust"] = "0"
        save_user_chars(user_chars)

        clear_piarvr_id()
        # Сообщение админу и пользователю-бывшему-сзаму
        try:
            szam_nick = accounts[cur_piarvr_id].get("nick", cur_piarvr_id)
            await context.bot.send_message(
                int(cur_piarvr_id),
                "ℹ️ Ваша льгота пиарщика VIP ADV была обнулена администрацией."
            )
        except Exception:
            pass
        await update.message.reply_text(f"✅ Льгота пиарщика VIP ADV снята с пользователя {piarvr_nick}.")
        return

    # --- ВЫДАЧА ЛЬГОТЫ НОВОМУ СЗАМУ ---
    # Проверяем, не выдана ли уже льгота
    active_piarvr_id = get_piarvr_id()
    if active_piarvr_id and accounts.has_section(active_piarvr_id):
        piarvr_nick = accounts[active_piarvr_id].get("nick", active_piarvr_id)
        await update.message.reply_text(
            f"❌ На данный момент уже выбран пиарщик VIP ADV: {piarvr_nick} (ID: {active_piarvr_id})\n"
            "Сначала снимите льготу у действующего с помощью <code>/piarvr 0</code>.",
            parse_mode="HTML"
        )
        return

    # Поиск пользователя по нику (без учета регистра)
    target_nick = piarvr_candidate
    target_id = None
    for sec in accounts.sections():
        if accounts[sec].get("nick", "").lower() == target_nick.lower():
            target_id = sec
            break

    if not target_id:
        await update.message.reply_text("❌ Пользователь с таким ником не найден.")
        return

    # Проверить, не является ли пользователь уже Старшим заместителем
    if accounts[target_id].get("piarvr", "0") == "1":
        await update.message.reply_text(
            f"❗ Пользователь {accounts[target_id].get('nick', target_id)} уже обладает льготой пиарщика VIP ADV."
        )
        return

    # Выдаём льготу: szam = 1, adm_level = 2, exp_multiplier = 1.25, max_zp = 1, должность "Старший заместитель", вывод без ограничений
    accounts[target_id]["piarvr"] = "1"
    save_accounts(accounts)

    # Устанавливаем характеристику ew_bust = 50 сразу при выдаче льготы
    ensure_user_chars(target_id)
    user_chars = load_user_chars()
    user_chars[target_id]["ew_bust"] = "50"
    save_user_chars(user_chars)

    set_piarvr_id(target_id)
    piarvr_nick = accounts[target_id].get("nick", target_id)
    try:
        await context.bot.send_message(
            int(target_id),
            "🎤 <b>Вам выдана льгота «Пиарщик VIP ADV»!</b>\n\n"
            "<i>Примечание: информация о премуществах всех видов льгот доступна с помощью команды /lg</i>\n"
            "<i>Активна постоянно пока вы ответственный за доплату пиарщик VIP ADV.</i>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await update.message.reply_text(
        f"✅ Льгота пиарщик VIP ADV выдана пользователю {piarvr_nick}.",
        parse_mode="HTML"
    )

async def pactivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    accounts = load_accounts()
    user_chars = load_user_chars()

    # Проверка: есть ли аккаунт
    if not accounts.has_section(user_id):
        await update.message.reply_text("❌ Ваш аккаунт не найден в системе.")
        return

    # Проверка: есть ли характеристика персонажа
    ensure_user_chars(user_id)
    user_chars = load_user_chars()

    # Проверяем наличие льготы piarvr
    piarvr_status = accounts[user_id].get("piarvr", "0")

    if piarvr_status != "1":
        await update.message.reply_text(
            "⛔ Вы не являетесь ответственным за доплату «Пиарщик VIP ADV».\n"
            "Обратитесь к администратору для закрепления льготы."
        )
        return

    # Проверяем текущую характеристику ew_bust
    current_bust = user_chars[user_id].get("ew_bust", "0")

    if current_bust == "50":
        await update.message.reply_text("⚠️ Льгота уже была активирована ранее.")
        return

    # Активируем льготу
    user_chars[user_id]["ew_bust"] = "50"
    save_user_chars(user_chars)

    await update.message.reply_text(
        "🎤 Льгота пиарщика VIP ADV успешно активирована!\n"
        "Эффект от льготы - 50 бустов каждый расчётный день активен."
    )

#Функция - семейный майнинг (доплата за охлаждайки).
#Функция - семейный майнинг (доплата за охлаждайки).
#Функция - семейный майнинг (доплата за охлаждайки).
    
async def mining(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)

    # Нужен 3 уровень админки для выдачи
    if int(user_info.get('is_admin', 0)) < 3:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return

    if not context.args:
        await update.message.reply_text(
            "Используйте:\n/mining <никнейм пользователя> — выдать льготу семейного майнинга\n/mining 0 — снять льготу у текущего обладателя"
        )
        return

    mining_candidate = " ".join(context.args).strip()

    # --- Работа с settings.ini для отслеживания текущего szam ---
    def get_mining_id():
        cfg = load_settings()
        if cfg.has_section("mining") and "id" in cfg["mining"]:
            return cfg["mining"]["id"]
        return None

    def set_mining_id(uid):
        cfg = load_settings()
        if not cfg.has_section("mining"):
            cfg.add_section("mining")
        cfg["mining"]["id"] = str(uid)
        save_settings(cfg)

    def clear_mining_id():
        cfg = load_settings()
        if cfg.has_section("mining") and "id" in cfg["mining"]:
            cfg.remove_option("mining", "id")
            save_settings(cfg)

    accounts = load_accounts()

    if mining_candidate == "0":
        # Снять льготу у текущего СЗАМА
        cur_mining_id = get_mining_id()
        if not cur_mining_id or not accounts.has_section(cur_mining_id):
            await update.message.reply_text("❌ Действующий ответственный за доплату семейный майнинг не найден.")
            return

        # Обнуляем льготу
        accounts[cur_mining_id]["mining"] = "0"
        save_accounts(accounts)

        ensure_user_chars(cur_mining_id)
        user_chars = load_user_chars()
        # при снятии льготы — ew_bust = 0
        user_chars[cur_mining_id]["ew_bust"] = "0"
        save_user_chars(user_chars)

        clear_mining_id()
        # Сообщение админу и пользователю-бывшему-сзаму
        try:
            mining_nick = accounts[cur_mining_id].get("nick", cur_mining_id)
            await context.bot.send_message(
                int(cur_mining_id),
                "ℹ️ Ваша льгота семейного майнинга была обнулена администрацией."
            )
        except Exception:
            pass
        await update.message.reply_text(f"✅ Льгота семейного майнинга была снята с пользователя {mining_nick}.")
        return

    # --- ВЫДАЧА ЛЬГОТЫ НОВОМУ СЗАМУ ---
    # Проверяем, не выдана ли уже льгота
    active_mining_id = get_mining_id()
    if active_mining_id and accounts.has_section(active_mining_id):
        mining_nick = accounts[active_mining_id].get("nick", active_mining_id)
        await update.message.reply_text(
            f"❌ На данный момент уже выбран ответственный за семейный майнинг: {mining_nick} (ID: {active_mining_id})\n"
            "Сначала снимите льготу у действующего с помощью <code>/mining 0</code>.",
            parse_mode="HTML"
        )
        return

    # Поиск пользователя по нику (без учета регистра)
    target_nick = mining_candidate
    target_id = None
    for sec in accounts.sections():
        if accounts[sec].get("nick", "").lower() == target_nick.lower():
            target_id = sec
            break

    if not target_id:
        await update.message.reply_text("❌ Пользователь с таким ником не найден.")
        return

    # Проверить, не является ли пользователь уже Старшим заместителем
    if accounts[target_id].get("mining", "0") == "1":
        await update.message.reply_text(
            f"❗ Пользователь {accounts[target_id].get('nick', target_id)} уже обладает льготой семейного майнинга."
        )
        return

    # Выдаём льготу: szam = 1, adm_level = 2, exp_multiplier = 1.25, max_zp = 1, должность "Старший заместитель", вывод без ограничений
    accounts[target_id]["mining"] = "1"
    save_accounts(accounts)

    # Устанавливаем характеристику ew_bust = 50 сразу при выдаче льготы
    ensure_user_chars(target_id)
    user_chars = load_user_chars()
    user_chars[target_id]["ew_bust"] = "200"
    save_user_chars(user_chars)

    set_mining_id(target_id)
    mining_nick = accounts[target_id].get("nick", target_id)
    try:
        await context.bot.send_message(
            int(target_id),
            "🕹 <b>Вам выдана льгота «Семейный майнинг»!</b>\n\n"
            "<i>Примечание: информация о премуществах всех видов льгот доступна с помощью команды /lg</i>\n"
            "<i>Активна постоянно пока вы ответственный за доплату семейный майнинг.</i>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await update.message.reply_text(
        f"✅ Льгота семейный майнинг выдана пользователю {mining_nick}.",
        parse_mode="HTML"
    )

async def mactivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    accounts = load_accounts()
    user_chars = load_user_chars()

    # Проверка: есть ли аккаунт
    if not accounts.has_section(user_id):
        await update.message.reply_text("❌ Ваш аккаунт не найден в системе.")
        return

    # Проверка: есть ли характеристика персонажа
    ensure_user_chars(user_id)
    user_chars = load_user_chars()

    # Проверяем наличие льготы piarvr
    mining_status = accounts[user_id].get("mining", "0")

    if mining_status != "1":
        await update.message.reply_text(
            "⛔ Вы не являетесь ответственным за доплату «Семейный майнинг».\n"
            "Обратитесь к администратору для закрепления льготы."
        )
        return

    # Проверяем текущую характеристику ew_bust
    current_bust = user_chars[user_id].get("ew_bust", "0")

    if current_bust == "200":
        await update.message.reply_text("⚠️ Льгота уже была активирована ранее.")
        return

    # Активируем льготу
    user_chars[user_id]["ew_bust"] = "200"
    save_user_chars(user_chars)

    await update.message.reply_text(
        "🕹 Льгота семейного майнинга успешно активирована!\n"
        "Эффект от льготы - 200 бустов каждый расчётный день активен."
    )

async def respect(update, context):
    from datetime import datetime, timedelta

    user_id = str(update.effective_user.id)
    user_info = get_user_info(user_id)

    # Проверка прав
    if not user_info or int(user_info.get('is_admin', 0)) < 2:
        await update.message.reply_text("⛔ Недостаточно прав для использования этой команды (admin >= 2).")
        return

    # Проверка аргументов
    if len(context.args) < 2:
        await update.message.reply_text("❌ Используйте: /respect Имя Фамилия (через пробел, как в нике).")
        return
    target_nick = " ".join(context.args)
    target_id = find_user_id_by_nick(target_nick)
    if not target_id:
        await update.message.reply_text("❌ Пользователь с таким никнеймом не найден.")
        return
    if str(target_id) == user_id:
        await update.message.reply_text("❌ Вы не можете выдать похвалу самому себе!")
        return

    # Проверка кулдауна
    hist = load_history_respect()
    now = datetime.now()
    dt_format = "%d.%m.%Y %H:%M:%S"
    last_time = None
    if hist.has_section(user_id):
        last_time_str = hist[user_id].get('last_time', '')
        if last_time_str:
            try:
                last_time = datetime.strptime(last_time_str, dt_format)
            except Exception:
                last_time = None
    if last_time and now < last_time + timedelta(hours=24):
        next_give = last_time + timedelta(hours=24)
        await update.message.reply_text(f"⏳ Похвалу можно выдать после: {next_give.strftime(dt_format)}")
        return

    # Выдача респекта (+5 ev_stones)
    accounts = load_accounts()
    target_sec = accounts[str(target_id)]
    old_stones = int(target_sec.get('ev_stones', 0))
    target_sec['ev_stones'] = str(old_stones + 5)
    save_accounts(accounts)

    # Обновить историю выдачи
    if not hist.has_section(user_id):
        hist.add_section(user_id)
    hist[user_id]['last_time'] = now.strftime(dt_format)
    history_line = f"{now.strftime(dt_format)}, {target_nick}"
    prev_history = hist[user_id].get('history', '')
    hist[user_id]['history'] = (prev_history + '; ' if prev_history else '') + history_line
    save_history_respect(hist)

    # Инфо о администраторах 2+
    admin_ids = [sec for sec in accounts.sections() if sec.isdigit() and int(accounts[sec].get('is_admin', 0)) >= 2 and sec != user_id]

    # Сообщение пользователю
    admin_position = user_info.get('position', 'Администратор')
    admin_nick = user_info.get('nick', 'admin')
    try:
        await context.bot.send_message(
            int(target_id),
            f"🏅 <b>ВЫ ЗАСЛУЖИЛИ ПОХВАЛУ!</b>\n"
            f"🛡 <b>{admin_position}</b> <b>{admin_nick}</b> похвалил Вас за выдающиеся успехи в работе.\n"
            f"🔥 <b>+ 5 респектов начислено на ваш баланс!</b>\n"
            f"✨ Не останавливайтесь! Ваш вклад ценят и замечают каждый день.\n"
            f"\n<i>Выдано: {now.strftime(dt_format)})</i>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    # Сообщение админу-выдавшему
    next_cd = now + timedelta(hours=24)
    await update.message.reply_text(
        f"✅ Похвала выдана!\n"
        f"Пользователь <b>{target_nick}</b> получил +5 респектов.\n"
        f"Следующую похвалу можно выдать после: <code>{next_cd.strftime(dt_format)}</code>",
        parse_mode="HTML"
    )

    # Уведомление всем админам уровня 2+ (кроме выдавшего)
    for aid in admin_ids:
        try:
            admin_notify_nick = accounts[aid].get('nick', aid)
            await context.bot.send_message(
                int(aid),
                f"🅰 Администратор {admin_position} {admin_nick} выдал похвалу (+5 респектов) пользователю {target_nick} в {now.strftime(dt_format)}.",
            )
        except Exception:
            pass

async def setsinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    # Только для админов 2 уровня и выше
    if not user_info or int(user_info.get('is_admin', 0)) < 2:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return

    # Проверяем аргументацию
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Используйте: /setsinfo <ID_набора>")
        return
    set_id = str(int(context.args[0].strip()))

    # Читаем набор из sets.ini
    config = configparser.ConfigParser()
    config.read("sets.ini", encoding="utf-8")
    if set_id not in config.sections():
        await update.message.reply_text(f"❌ Набор с ID {set_id} не найден.")
        return

    data = config[set_id]
    def emojify(field, value):
        emoji_map = {
            'name': '🎁',
            'required_boosts': '💈',
            'ball': '🧿',
            'exp': '⚡',
            'money': '💳',
            't': '🎃',
            'limit': '🔢',
            'limitiz': '📊'
        }
        return f"{emoji_map.get(field, field)} <b>{value}</b>"

    details = [
        f"🆔 <b>ID:</b> <code>{set_id}</code>",
        emojify('name', data.get('name', '—')),
        emojify('required_boosts', data.get('required_boosts', '0')) + " (необходимо для покупки)",
        emojify('ball', data.get('ball', '0')),
        emojify('exp', data.get('exp', '0')),
        emojify('money', f"{data.get('money', '0')} RUB"),
        emojify('t', data.get('t', '0')),
        emojify('limit', data.get('limit', '0')) + " (лимит набора)",
        emojify('limitiz', data.get('limitiz', '0')) + " (количество использований)",
    ]
    await update.message.reply_text(
        "📦 <b>Информация о наборе.</b>\n\n" + "\n".join(details),
        parse_mode="HTML"
    )

async def setslimit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    if not user_info or int(user_info.get('is_admin', 0)) < 3:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return

    # Проверяем аргументы
    if len(context.args) != 2 or not context.args[0].isdigit() or not context.args[1].isdigit():
        await update.message.reply_text("Используйте: /setslimit <ID_набора> <новый_лимит> (например: /setslimit 1 100)")
        return

    set_id = str(int(context.args[0].strip()))
    new_limit = int(context.args[1].strip())

    config = configparser.ConfigParser()
    config.read("sets.ini", encoding="utf-8")
    if set_id not in config.sections():
        await update.message.reply_text(f"❌ Набор с ID {set_id} не найден.")
        return

    config[set_id]['limit'] = str(new_limit)

    with open("sets.ini", "w", encoding="utf-8") as f:
        config.write(f)

    await update.message.reply_text(
        f"✅ Лимит набора ID <b>{set_id}</b> (<b>{config[set_id].get('name','')}</b>) успешно изменён на <b>{new_limit}</b>.",
        parse_mode="HTML"
    )

def get_craft_keyboard():
    keyboard = [
        [KeyboardButton("☀️ Светлая сторона"), KeyboardButton("🖤 Темная сторона")],
        [KeyboardButton("Назад в меню крафтинга")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
# --- Основная функция крафта ---
async def craft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import datetime
    user_id = str(update.effective_user.id)

    # --- Проверка даты открытия крафта ---
    craft_open_date = datetime.date(2025, 12, 10)
    today = datetime.datetime.now().date()
    if today < craft_open_date:
        await update.message.reply_text(
            "🎄 Крафт льгот пока не доступен!\n\n"
            f"✨ Праздничный крафт откроется <b>{craft_open_date.strftime('%d.%m.%Y')}</b> — ждите волшебства ✨\n\n"
            "Пока можно продолжать собирать осколки и готовиться — ваши шансы обязательно пригодятся под ёлкой ❄️",
            parse_mode="HTML",
            reply_markup=get_back_to_craft_keyboard()
        )
        return

    # --- Проверка выбранной стороны ---
    sides_cfg = load_sides()
    if sides_cfg.has_section(user_id) and "side" in sides_cfg[user_id]:
        chosen_side = sides_cfg[user_id]["side"]
        if chosen_side == "light":
            await svetlaya_storona(update, context)
        else:
            await temnaya_storona(update, context)
        return

    # --- Получаем осколки пользователя ---
    accounts_cfg = load_accounts()
    if accounts_cfg.has_section(user_id):
        sect = accounts_cfg[user_id]
        oosk = int(sect.get("oosk", 0))
        uosk = int(sect.get("uosk", 0))
        losk = int(sect.get("losk", 0))
    else:
        oosk = uosk = losk = 0

    oosk_s, uosk_s, losk_s = fmt(oosk), fmt(uosk), fmt(losk)

    # --- Отправка картинки craft.png ---
    try:
        with open("craft.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
    except FileNotFoundError:
        pass

    # --- Сообщение выбора стороны ---
    message = (
        "🎄 <b>Система крафта.</b> 🎄\n\n"
        "🛡 <b>До начала крафта нужно выбрать сторону — светлую или темную.</b>\n\n"
        "<b>🎄 Светлая сторона </b>символизирует защиту, помощь и стабильный прогресс.\n"
        "🎅 Новые предметы, которые усиливают оборону, помогают союзникам и дают надёжные бонусы.\n\n"
        "<b>🖤 Тёмная сторона </b>символизирует сила, риск и агрессивный прогресс.\n"
        "🧛 Новые предметы, которые позволяют атаковать других, получать уникальные награды и рисковать ради сильных бонусов.\n\n"
        "🕖 <b>Если Вы передумаете, изменить сторону можно будет только скрафтив камень выбора.</b>"
    )

    await update.message.reply_text(message, reply_markup=get_craft_keyboard(), parse_mode="HTML")
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="HTML")


async def svetlaya_storona(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    save_side(user_id, "light")

    accounts_cfg = load_accounts()
    craft_cfg = load_craft_items()

    # --- бонус крафта пользователя ---
    craftup = 0
    if accounts_cfg.has_section(user_id):
        try:
            craftup = int(accounts_cfg[user_id].get("craftup", 0))
        except Exception:
            craftup = 0

    def get_final_chance(recipe_id: str) -> int:
        if craft_cfg.has_section(recipe_id):
            try:
                base = int(craft_cfg[recipe_id].get("chance", 0))
            except Exception:
                base = 0
            return min(100, base + craftup)
        return 0

    # Фото светлой стороны
    try:
        with open("svetlaya_storon.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
    except FileNotFoundError:
        pass

    message = (
        "🎄 <b>Праздничный крафт.</b> 🎄\n"
        "☀️ <b>Светлая сторона.</b>\n\n"
        "🐲 Новейшие предметы светлой стороны:\n\n"
        f"🎅 <b>Шкатулка «Деда Мороза»</b>\n"
        f"❄️ При открытии <b>даёт случайную обычную награду</b> с новогодней праздничной мастерской. КД — 72 часа.\n"
        f"🧱 Требование: 35 📒 60 🔥 100 ❄️ 45 💈\n"
        f"📟 Шанс: {get_final_chance('9')}%\n"
        f"Для крафта введите <code>/craft 9</code>\n\n"
        f"🤶 <b>Торговый прилавок «Снегурочки»</b>\n"
        f"❄️ При активации <b>снижает комиссию на 5%</b>, есть возможность "
        f"<b>передать эффект</b> снижения комиссии другому пользователю на 5 мин. КД — 5 минут.\n"
        f"🧱 Требование: 20 📒 35 🔥 50 ❄️ 20 💈\n"
        f"📟 Шанс: {get_final_chance('8')}%\n"
        f"Для крафта введите <code>/craft 8</code>\n\n"
        f"🧝‍‍ <b>Модуль защиты «Эльфийский оберег»</b>\n"
        f"❄️ С вероятностью 75% <b>блокирует кражу от Лешего</b> и дополнительно начисляет 10 EXP "
        f"при неудачной атаке на Вас.\n"
        f"🧱 Требование: 35 📕 15 🔥 20 ❄️ 15 💈\n"
        f"📟 Шанс: {get_final_chance('7')}%\n"
        f"Для крафта введите <code>/craft 7</code>\n\n"
        "<i>Примечание: информация о преимуществах всех новейших предметов доступна "
        "с помощью команды /craft info «ID предмета»</i>"
    )

    await update.message.reply_text(
        message,
        reply_markup=get_back_to_craft_keyboard(),
        parse_mode="HTML"
    )
    

async def temnaya_storona(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    save_side(user_id, "dark")

    accounts_cfg = load_accounts()
    craft_cfg = load_craft_items()

    # --- бонус крафта пользователя ---
    craftup = 0
    if accounts_cfg.has_section(user_id):
        try:
            craftup = int(accounts_cfg[user_id].get("craftup", 0))
        except Exception:
            craftup = 0

    def get_final_chance(recipe_id: str) -> int:
        if craft_cfg.has_section(recipe_id):
            try:
                base = int(craft_cfg[recipe_id].get("chance", 0))
            except Exception:
                base = 0
            return min(100, base + craftup)
        return 0

    # Фото тёмной стороны
    try:
        with open("temnaya_storon.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
    except FileNotFoundError:
        pass

    message = (
        "🥀 <b>Праздничный крафт.</b> 🥀\n"
        "🖤 <b>Тёмная сторона.</b>\n\n"
        "🏮 Новейшие предметы тёмной стороны:\n\n"
        f"🧛‍ <b>Шкатулка «Кощея Бессмертного»</b>\n"
        f"〰 При открытии даёт <b>случайную уникальную награду</b> с праздничной новогодней мастерской, "
        f"но есть риск (10%) потерять шкатулку в погоне за сокровищем. КД — 72 часа.\n"
        f"🧱 Требование: 40 📒 65 🔥 90 ❄️ 40 💈\n"
        f"📟 Шанс: {get_final_chance('10')}%\n"
        f"Для крафта введите <code>/craft 10</code>\n\n"
        f"🧟‍ <b>Торговая изба «Бабы Яги»</b>\n"
        f"〰 При активации <b>комиссия при переводах — 0%</b>, "
        f"но есть вероятность 10%, что Баба Яга подкрутит весы и перевод уйдёт на её счёт.\n"
        f"🧱 Требование: 20 📒 25 🔥 45 ❄️ 20 💈\n"
        f"📟 Шанс: {get_final_chance('11')}%\n"
        f"Для крафта введите <code>/craft 11</code>\n\n"
        f"🧌 <b>Модуль татьбы «Проделки Лешего»</b>\n"
        f"〰 При активации случайным образом <b>отбирает у жертвы 25 ед. случайного ресурса</b>, "
        f"есть риск столкнуться с Эльфийским оберегом и потерять 10 ед. случайных ресурсов. "
        f"КД — 12 часов. Активация: /mdleh «ник жертвы»\n"
        f"🧱 Требование: 35 📕 40 🔥 30 ❄️ 15 💈\n"
        f"📟 Шанс: {get_final_chance('12')}%\n"
        f"Для крафта введите <code>/craft 12</code>\n\n"
        "<i>Примечание: информация о преимуществах всех новейших предметов доступна "
        "с помощью команды /craft info «ID предмета»</i>"
    )

    await update.message.reply_text(
        message,
        reply_markup=get_back_to_craft_keyboard(),
        parse_mode="HTML"
    )


def get_back_to_craft_keyboard():
    keyboard = [[KeyboardButton("Назад в меню крафтинга")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_to_craft_keyboard():
    keyboard = [[KeyboardButton("Назад в меню крафтинга")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ----------------------
# CRUD задания
# ----------------------
def create_task(title: str, coins: int, snow: int, exp: int, description: str, creator_id: str, repeatable: str = "no"):
    cfg = load_tasks_cfg()
    tid = generate_task_id()
    sec = f"task_{tid}"
    cfg[sec] = {
        "title": title,
        "coins": str(int(coins)),
        "snow": str(int(snow)),
        "exp": str(int(exp)),
        "description": description,
        "creator_id": str(creator_id),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "repeatable": "yes" if str(repeatable).lower() in ("yes", "y", "true", "1") else "no"
    }
    save_tasks_cfg(cfg)
    return tid


def delete_task(task_id: str):
    cfg = load_tasks_cfg()
    sec = f"task_{task_id}"
    if cfg.has_section(sec):
        cfg.remove_section(sec)
        save_tasks_cfg(cfg)
        return True
    return False


def list_tasks():
    cfg = load_tasks_cfg()
    tasks = []
    for sec in cfg.sections():
        if sec.startswith("task_"):
            tid = sec.split("_", 1)[1]
            data = cfg[sec]
            tasks.append({
                "id": tid,
                "title": data.get("title", ""),
                "coins": int(data.get("coins", "0")),
                "snow": int(data.get("snow", "0")),
                "exp": int(data.get("exp", "0")),
                "description": data.get("description", ""),
                "creator_id": data.get("creator_id", ""),
                "created_at": data.get("created_at", ""),
                "repeatable": data.get("repeatable", "no")
            })
    # сортируем по созданию (новые в начале)
    tasks.sort(key=lambda x: x.get("created_at", ""), reverse=False)
    return tasks


def get_task(task_id: str):
    cfg = load_tasks_cfg()
    sec = f"task_{task_id}"
    if cfg.has_section(sec):
        data = cfg[sec]
        return {
            "id": task_id,
            "title": data.get("title", ""),
            "coins": int(data.get("coins", "0")),
            "snow": int(data.get("snow", "0")),
            "exp": int(data.get("exp", "0")),
            "description": data.get("description", ""),
            "creator_id": data.get("creator_id", ""),
            "created_at": data.get("created_at", ""),
            "repeatable": data.get("repeatable", "no")
        }
    return None


# ----------------------
# Пользовательские задания (accepted / pending_review / completed)
# ----------------------
def _user_section(user_id: str):
    return f"user_{user_id}"


def set_user_task_status(user_id: str, task_id: str, status: str):
    """
    status: accepted, pending_review, completed
    В user_tasks.ini секция user_<user_id>, ключ task_<taskid> = status|timestamp
    """
    cfg = load_user_tasks_cfg()
    us = _user_section(user_id)
    if not cfg.has_section(us):
        cfg.add_section(us)
    cfg[us][f"task_{task_id}"] = f"{status}|{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    save_user_tasks_cfg(cfg)


def get_user_tasks(user_id: str):
    cfg = load_user_tasks_cfg()
    us = _user_section(user_id)
    res = {}
    if cfg.has_section(us):
        for k, v in cfg[us].items():
            if k.startswith("task_"):
                parts = v.split("|", 1)
                status = parts[0]
                ts = parts[1] if len(parts) > 1 else ""
                tid = k.split("_", 1)[1]
                res[tid] = {"status": status, "ts": ts}
    return res


def find_users_with_task_status(task_id: str, status: str):
    """Возвращает список user_id (строк), у которых task_<id> имеет указанный статус"""
    cfg = load_user_tasks_cfg()
    res = []
    for sec in cfg.sections():
        if not sec.startswith("user_"):
            continue
        for k, v in cfg[sec].items():
            if k == f"task_{task_id}":
                st = v.split("|", 1)[0]
                if st == status:
                    uid = sec.split("_", 1)[1]
                    res.append(uid)
    return res


# ----------------------
# Формирование сообщения задачи и inline-кнопок (просмотр)
# ----------------------
def format_task_message(task: dict):
    return (
        f"📋 <b>Задания.</b>\n"
        f"🏷 <b>{task['title']}</b>\n"
        f"🆔 ID: <code>{task['id']}</code>\n\n"
        f"{task['description']}\n\n"
        f"🎁 Награда: 🧿 {task['coins']} | ❄️ {task['snow']} | ⚡ {task['exp']}\n"
        f"📅 Создано: {task.get('created_at','')}\n\n"
        f"ℹ <b>С помощью кнопок навигации ⏭️ и ⏮ листайте доступные задания для выполнения.</b>\n"
        f"✅ <b>Если Вы взяли задание в работу нажмите на кнопку «Принять».</b>\n"
        f"🟡 <b>Если Вы выполнили все условия задания нажмите на кнопку «Завершить».</b>\n"
    )

def make_tasks_keyboard(index: int, total: int, task_id: str, accepted: bool):
    kb = []
    left_disabled = index <= 0
    right_disabled = index >= total - 1

    nav_row = []
    if not left_disabled:
        nav_row.append(InlineKeyboardButton("⏮️", callback_data=f"tasks_nav_{index-1}"))
    else:
        nav_row.append(InlineKeyboardButton(" ", callback_data="noop"))

    # Accept / Finish button row
    action_row = []
    if not accepted:
        action_row.append(InlineKeyboardButton("✅ Принять", callback_data=f"tasks_accept_{task_id}"))
    else:
        action_row.append(InlineKeyboardButton("🟡 Завершить", callback_data=f"tasks_finish_{task_id}"))

    if not right_disabled:
        nav_row.append(InlineKeyboardButton("⏭️", callback_data=f"tasks_nav_{index+1}"))
    else:
        nav_row.append(InlineKeyboardButton(" ", callback_data="noop"))

    kb.append(nav_row)
    kb.append(action_row)
    kb.append([InlineKeyboardButton("❌ Закрыть", callback_data="tasks_close")])
    return InlineKeyboardMarkup(kb)


# ----------------------
# Хендлеры
# ----------------------
# ----------------------
# NEW: проверка на наличие заданий в статусе pending_review
# ----------------------
def any_pending_reviews() -> bool:
    """
    Возвращает True если в файле user_tasks.ini есть хотя бы одна запись со статусом pending_review.
    """
    cfg = load_user_tasks_cfg()
    for sec in cfg.sections():
        for k, v in cfg[sec].items():
            # v формат: status|timestamp
            try:
                status = v.split("|", 1)[0]
            except Exception:
                status = v
            if status == "pending_review":
                return True
    return False


# ----------------------
# МОД: tasks_command — теперь ограничивает доступ если есть pending_review
# ----------------------
async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Открыть просмотр заданий (вызывается из кнопки "Задания" или командой /tasks).
    Блокирует доступ для обычных пользователей, если есть задания ожидающие проверки.
    Только админы уровня >=3 могут просматривать в этот момент.
    """
    user = update.effective_user
    user_id = str(user.id)

    try:
        with open("zadania.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
    except Exception:
        pass

    # Если есть незавершённые проверки — блокируем доступ для обычных пользователей
    if any_pending_reviews():
        user_info = get_user_info(user_id)
        admin_level = int(user_info.get('is_admin', 0)) if user_info else 0
        if admin_level < 3:
            # Ограничиваем доступ
            await update.message.reply_text(
                "🔒 Доступ к заданиям временно ограничен — в данный момент есть задания, ожидающие проверки.\n"
                "Пожалуйста, дождитесь рассмотрения текущих выполненных заданий или обратитесь к администратору бота.",
                reply_markup=get_back_keyboard()
            )
            return
        # если админ >=3 — он может продолжить просмотр и модерацию

    tasks = list_tasks()
    if not tasks:
        await update.message.reply_text("📭 Заданий пока нет.", reply_markup=get_back_keyboard())
        return

    # Сохраняем список в context.user_data (чтобы навигация работала)
    context.user_data["tasks_list"] = tasks
    context.user_data["tasks_index"] = 0

    task = tasks[0]
    user_tasks = get_user_tasks(user_id)
    accepted = task["id"] in user_tasks and user_tasks[task["id"]]["status"] == "accepted"
    text = format_task_message(task)
    reply_markup = make_tasks_keyboard(0, len(tasks), task["id"], accepted)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")


# ----------------------
# NEW: Команда /reject — отклонение задания (админ >=3)
# ----------------------
async def reject_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /reject <task_id> [user_id] [причина...]
    Отклоняет задание у пользователя, переводит статус в 'rejected' и уведомляет пользователя.
    Доступ: админ >= 3
    """
    caller = update.effective_user
    caller_id = str(caller.id)
    caller_info = get_user_info(caller_id)
    if not caller_info or int(caller_info.get("is_admin", 0)) < 3:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return

    if not context.args:
        await update.message.reply_text("Использование: /reject <task_id> [user_id] [причина]\nЕсли user_id не указан — бот попытается выбрать единственного кандидата на проверке.")
        return

    task_id = context.args[0].strip()
    explicit_user = context.args[1].strip() if len(context.args) >= 2 and context.args[1].isdigit() else None
    reason = " ".join(context.args[2:]).strip() if len(context.args) >= 3 else ""

    task = get_task(task_id)
    if not task:
        await update.message.reply_text("❌ Задание не найдено.")
        return

    if explicit_user:
        target_user = explicit_user
        ut = get_user_tasks(target_user)
        if task_id not in ut or ut[task_id]["status"] != "pending_review":
            await update.message.reply_text("❌ Указанный пользователь не имеет это задание в статусе на проверке.")
            return
    else:
        candidates = find_users_with_task_status(task_id, "pending_review")
        if not candidates:
            await update.message.reply_text("❌ Нет пользователей, ожидающих проверки для этого задания.")
            return
        if len(candidates) > 1:
            # Просим уточнить user_id
            text = "Найдено несколько претендентов. Уточните user_id и выполните команду снова:\n\n"
            text += "\n".join([f"- {get_user_info(uid).get('nick','<no-nick>')} (ID: {uid})" for uid in candidates])
            await update.message.reply_text(text)
            return
        target_user = candidates[0]

    # Ставим статус rejected
    set_user_task_status(target_user, task_id, "rejected")

    # Уведомляем пользователя
    try:
        txt = (
            f"❌ Ваше выполнение задания <b>{task['title']}</b> (ID {task_id}) было отклонено администратором.\n"
        )
        if reason:
            txt += f"Причина: {reason}\n"
        txt += "Вы можете повторно принять задание и исправить выполнение."
        await context.bot.send_message(int(target_user), txt, parse_mode="HTML")
    except Exception:
        pass

    # Уведомляем администратора (caller) и остальных адм.уровня>=2
    await update.message.reply_text(f"✅ Задание {task_id} у пользователя {get_user_info(target_user).get('nick','<no-nick>')} отклонено.")
    # Оповещение адм.уровня >=2 (кроме caller)
    admin_ids = load_admin_ids()
    for aid in admin_ids:
        try:
            if str(aid) == caller_id:
                continue
            await context.bot.send_message(int(aid), f"🅰 Задание {task_id} у {get_user_info(target_user).get('nick','<no-nick>')} отклонено администратором {caller_info.get('nick','admin')}.")
        except Exception:
            continue


async def tasks_nav_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Навигация между задачами (callback)"""
    query = update.callback_query
    await query.answer()
    data = query.data  # tasks_nav_<index>
    try:
        index = int(data.split("_")[-1])
    except Exception:
        return
    tasks = context.user_data.get("tasks_list") or list_tasks()
    if not tasks:
        await query.message.edit_text("📭 Заданий пока нет.", reply_markup=None)
        return
    if index < 0 or index >= len(tasks):
        return
    context.user_data["tasks_index"] = index
    task = tasks[index]
    user_id = str(query.from_user.id)
    user_tasks = get_user_tasks(user_id)
    accepted = task["id"] in user_tasks and user_tasks[task["id"]]["status"] == "accepted"
    text = format_task_message(task)
    reply_markup = make_tasks_keyboard(index, len(tasks), task["id"], accepted)
    try:
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception:
        # иногда edit_text может поднять BadRequest — в этом случае отправляем новое
        await query.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")


async def tasks_close_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.delete()
    except Exception:
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass


async def tasks_accept_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    user_id = str(user.id)
    data = query.data  # tasks_accept_<id>
    task_id = data.split("_")[-1]
    task = get_task(task_id)
    if not task:
        await query.message.reply_text("❌ Задание не найдено или удалено.")
        return

    # Проверим, не принимал ли уже
    user_tasks = get_user_tasks(user_id)
    if task_id in user_tasks and user_tasks[task_id]["status"] in ("accepted", "pending_review"):
        await query.answer("Вы уже приняли это задание.", show_alert=True)
        return

    set_user_task_status(user_id, task_id, "accepted")
    # Уведомить админов lvl>=2, кроме, возможно, принявшего
    admin_ids = load_admin_ids()  # функция из lk.py — возвращает admin ids lvl>=2
    msg = f"🅰 Пользователь {get_user_info(user_id).get('nick','<no-nick>')} принял задание ID {task_id} — {task['title']}"
    for aid in admin_ids:
        try:
            # отправляем личные уведомления
            await context.bot.send_message(int(aid), msg)
        except Exception:
            pass

    # Обновить интерфейс — заменить кнопку на «Завершить»
    # Находим текущий индекс из context (если открыт тем же пользователем)
    idx = context.user_data.get("tasks_index", 0)
    tasks = context.user_data.get("tasks_list") or list_tasks()
    # Найдем индекс соответствующего задания, чтобы корректно обновить
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            idx = i
            break
    reply_markup = make_tasks_keyboard(idx, len(tasks), task_id, accepted=True)
    try:
        await query.message.edit_text(format_task_message(task), reply_markup=reply_markup, parse_mode="HTML")
    except Exception:
        pass

    await query.message.reply_text("✅ Задание принято. Теперь можно выполнить и нажать «Завершить».")


async def tasks_finish_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пользователь пометил выполнение — отправляем на проверку (pending_review)"""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    user_id = str(user.id)
    data = query.data  # tasks_finish_<id>
    task_id = data.split("_")[-1]
    task = get_task(task_id)
    if not task:
        await query.message.reply_text("❌ Задание не найдено.")
        return

    # Проверка, что пользователь действительно принял
    ut = get_user_tasks(user_id)
    if task_id not in ut or ut[task_id]["status"] != "accepted":
        await query.answer("Вы не принимали это задание.", show_alert=True)
        return

    set_user_task_status(user_id, task_id, "pending_review")

    # Уведомляем админов уровня >=3
    admin_ids = [int(a) for a in load_admin_ids()]  # load_admin_ids возвращает admin>=2; будем фильтровать по is_admin>=3
    # Проверяем реальные уровни в accounts.ini
    accounts = load_accounts()
    admins_to_notify = []
    for aid in admin_ids:
        try:
            if accounts.has_section(str(aid)) and int(accounts[str(aid)].get("is_admin", "0")) >= 3:
                admins_to_notify.append(int(aid))
        except Exception:
            continue

    notif_msg = (
        f"🅰 Задание на проверке:\n"
        f"Пользователь: {get_user_info(user_id).get('nick','<no-nick>')} (ID: {user_id})\n"
        f"Задание: {task['title']} (ID {task_id})\n"
        f"Награда: 🧿 {task['coins']} | ❄️ {task['snow']} | ⚡ {task['exp']}\n\n"
        f"Для подтверждения выполненной задачи используйте команду:\n/confirm {task_id} {user_id}\n"
        f"После подтверждения используйте команду:\n/deltask {task_id}\n"
        f"Для отклонения выполненной задачи используйте команду:\n/reject {task_id} {user_id} и укажите причину."
    )
    for aid in admins_to_notify:
        try:
            await context.bot.send_message(aid, notif_msg)
        except Exception:
            pass

    await query.message.reply_text("🔔 Задание отправлено на проверку лидеру семьи и старшему заместителю, принять повторно задание невозможно, ожидайте решения.")


# ----------------------
# Подтверждение и выдача наград (админ >=3)
# ----------------------
async def confirm_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /confirm <task_id> [user_id]
    Подтверждает выполнение задания и начисляет награду.
    """
    user = update.effective_user
    caller_id = str(user.id)
    caller_info = get_user_info(caller_id)
    if not caller_info or int(caller_info.get("is_admin", 0)) < 3:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return

    args = context.args
    if len(args) == 0:
        await update.message.reply_text("Использование: /confirm <task_id> [user_id]")
        return

    task_id = args[0].strip()
    explicit_user = args[1].strip() if len(args) >= 2 else None

    task = get_task(task_id)
    if not task:
        await update.message.reply_text("❌ Задание не найдено.")
        return

    # Если user указан явно — используем
    if explicit_user:
        target_user = explicit_user
        # Проверим, что у пользователя есть pending_review на это задание
        ut = get_user_tasks(target_user)
        if task_id not in ut or ut[task_id]["status"] != "pending_review":
            await update.message.reply_text("❌ Указанный пользователь не имеет это задание в статусе на проверке.")
            return
    else:
        # Ищем всех пользователей с pending_review; если 0 — сообщаем, если >1 — просим уточнить
        candidates = find_users_with_task_status(task_id, "pending_review")
        if not candidates:
            await update.message.reply_text("❌ Нет пользователей, ожидающих проверки для этого задания.")
            return
        if len(candidates) > 1:
            # Покажем список и попросим уточнить user_id
            text = "Найдено несколько претендентов. Используйте команду /confirm <task_id> <user_id> для подтверждения.\n\n"
            text += "Кандидаты:\n" + "\n".join([f"- {get_user_info(uid).get('nick','<no-nick>')} (ID: {uid})" for uid in candidates])
            await update.message.reply_text(text)
            return
        target_user = candidates[0]

    # Проходим выдачу награды
    accounts_cfg = load_accounts()
    if not accounts_cfg.has_section(str(target_user)):
        await update.message.reply_text("❌ Профиль пользователя не найден в accounts.ini")
        return

    sec = accounts_cfg[str(target_user)]
    # добавляем награды (безопасно: int-get)
    try:
        sec['ball'] = str(int(sec.get('ball', '0')) + int(task.get('coins', 0)))
        sec['t'] = str(int(sec.get('t', '0')) + int(task.get('snow', 0)))
        sec['exp'] = str(int(sec.get('exp', '0')) + int(task.get('exp', 0)))
        save_accounts(accounts_cfg)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при начислении награды: {e}")
        return

    # Обновляем статус у пользователя
    set_user_task_status(target_user, task_id, "completed")

    # Уведомления
    try:
        await context.bot.send_message(int(target_user),
            f"✅ Ваше задание <b>{task['title']}</b> (ID {task_id}) подтверждено администратором.\n"
            f"Вам начислено: 🧿 {task['coins']} | ❄️ {task['snow']} | ⚡ {task['exp']}",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await update.message.reply_text(f"✅ Награды успешно выданы пользователю {get_user_info(target_user).get('nick','<no-nick>')} (ID: {target_user}).")


# ----------------------
# Добавление задания (ConversationHandler)
# ----------------------
async def addtask_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = get_user_info(str(user.id))
    if not user_info or int(user_info.get("is_admin", 0)) < 3:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return ConversationHandler.END

    context.user_data['new_task'] = {}
    await update.message.reply_text("✏️ Введите название задания (коротко):", reply_markup=get_back_keyboard())
    return AT_TITLE


async def addtask_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("Название не может быть пустым. Введите название:")
        return AT_TITLE
    context.user_data['new_task']['title'] = text
    await update.message.reply_text("🧿 Сколько монет активности (целое число)?", reply_markup=get_back_keyboard())
    return AT_COINS


async def addtask_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        v = int(update.message.text.strip())
    except Exception:
        await update.message.reply_text("Введите целое число для монет активности.")
        return AT_COINS
    context.user_data['new_task']['coins'] = v
    await update.message.reply_text("❄️ Сколько снежинок (целое число)?", reply_markup=get_back_keyboard())
    return AT_SNOW


async def addtask_snow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        v = int(update.message.text.strip())
    except Exception:
        await update.message.reply_text("Введите целое число для снежинок.")
        return AT_SNOW
    context.user_data['new_task']['snow'] = v
    await update.message.reply_text("⚡ Сколько EXP (целое число)?", reply_markup=get_back_keyboard())
    return AT_EXP


async def addtask_exp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        v = int(update.message.text.strip())
    except Exception:
        await update.message.reply_text("Введите целое число для EXP.")
        return AT_EXP
    context.user_data['new_task']['exp'] = v
    await update.message.reply_text("📝 Введите описание задания (кратко):", reply_markup=get_back_keyboard())
    return AT_DESC


async def addtask_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data['new_task']['description'] = text
    await update.message.reply_text("🔁 Повторяемое задание? (yes/no):", reply_markup=get_back_keyboard())
    return AT_REPEAT


async def addtask_repeat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip().lower()
    context.user_data['new_task']['repeatable'] = "yes" if txt in ("yes", "y", "да", "д") else "no"
    nt = context.user_data['new_task']
    preview = (
        f"Проверьте задание перед созданием:\n\n"
        f"Название: {nt['title']}\n"
        f"Описание: {nt['description']}\n"
        f"Награда: 🧿 {nt['coins']} | ❄️ {nt['snow']} | ⚡ {nt['exp']}\n"
        f"Повторяемое: {nt['repeatable']}\n\n"
        f"Подтвердите создание (Да/Нет)."
    )
    await update.message.reply_text(preview, reply_markup=get_back_keyboard())
    return AT_CONFIRM


async def addtask_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    if text not in ("да", "д", "yes", "y"):
        await update.message.reply_text("Отмена создания задания.")
        context.user_data.pop('new_task', None)
        return ConversationHandler.END

    nt = context.user_data.get('new_task', {})
    creator = str(update.effective_user.id)
    tid = create_task(
        title=nt.get('title', 'Без названия'),
        coins=int(nt.get('coins', 0)),
        snow=int(nt.get('snow', 0)),
        exp=int(nt.get('exp', 0)),
        description=nt.get('description', ''),
        creator_id=creator,
        repeatable=nt.get('repeatable', 'no')
    )
    await update.message.reply_text(f"✅ Задание создано. ID: {tid}", reply_markup=get_back_keyboard())
    # очистка
    context.user_data.pop('new_task', None)
    return ConversationHandler.END


async def addtask_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('new_task', None)
    await update.message.reply_text("❌ Создание задания отменено.", reply_markup=get_back_keyboard())
    return ConversationHandler.END


# ----------------------
# Удаление задания (команда /deltask <id> или интерактивно)
# ----------------------
async def deltask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = get_user_info(str(user.id))
    if not user_info or int(user_info.get("is_admin", 0)) < 3:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return

    if context.args:
        tid = context.args[0].strip()
        ok = delete_task(tid)
        if ok:
            await update.message.reply_text(f"✅ Задание {tid} удалено.")
        else:
            await update.message.reply_text("❌ Задание не найдено.")
        return

    # Если нет аргументов — показываем список задач с кнопками удаления
    tasks = list_tasks()
    if not tasks:
        await update.message.reply_text("📭 Заданий пока нет.", reply_markup=get_back_keyboard())
        return
    kb = []
    for t in tasks:
        kb.append([InlineKeyboardButton(f"{t['title']} (ID {t['id']})", callback_data=f"task_delete_{t['id']}")])
    kb.append([InlineKeyboardButton("Закрыть", callback_data="tasks_close")])
    await update.message.reply_text("Выберите задание для удаления:", reply_markup=InlineKeyboardMarkup(kb))


async def task_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # task_delete_<id>
    tid = data.split("_")[-1]
    task = get_task(tid)
    if not task:
        await query.message.reply_text("❌ Задание не найдено.")
        return
    kb = [
        [InlineKeyboardButton("✅ Подтвердить удаление", callback_data=f"task_delete_confirm_{tid}")],
        [InlineKeyboardButton("❌ Отменить", callback_data="tasks_close")]
    ]
    await query.message.reply_text(f"Вы действительно хотите удалить задание: {task['title']} (ID {tid}) ?", reply_markup=InlineKeyboardMarkup(kb))


async def task_delete_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # task_delete_confirm_<id>
    tid = data.split("_")[-1]
    ok = delete_task(tid)
    if ok:
        await query.message.reply_text(f"✅ Задание {tid} удалено.")
    else:
        await query.message.reply_text("❌ Ошибка удаления (возможно, уже удалено).")

conv_addtask = ConversationHandler(
    entry_points=[CommandHandler("addtask", addtask_start)],
    states={
        AT_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, addtask_title)],
        AT_COINS: [MessageHandler(filters.TEXT & ~filters.COMMAND, addtask_coins)],
        AT_SNOW: [MessageHandler(filters.TEXT & ~filters.COMMAND, addtask_snow)],
        AT_EXP: [MessageHandler(filters.TEXT & ~filters.COMMAND, addtask_exp)],
        AT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, addtask_desc)],
        AT_REPEAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, addtask_repeat)],
        AT_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, addtask_confirm)],
    },
    fallbacks=[CommandHandler("cancel", addtask_cancel)],
    per_user=True
)

async def commers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)

    if int(user_info.get("is_admin", 0)) < 3:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return

    if not context.args:
        await update.message.reply_text(
            "Используйте:\n"
            "/commers <никнейм пользователя> — выдать льготу Коммерсант\n"
            "/commers 0 — снять льготу у текущего Коммерсанта"
        )
        return

    commers_candidate = " ".join(context.args).strip()

    # ──────────────────────────────
    # Работа с settings.ini
    # ──────────────────────────────
    def get_commers_id():
        cfg = load_settings()
        if cfg.has_section("commers") and "id" in cfg["commers"]:
            return cfg["commers"]["id"]
        return None

    def set_commers_id(uid):
        cfg = load_settings()
        if not cfg.has_section("commers"):
            cfg.add_section("commers")
        cfg["commers"]["id"] = str(uid)
        save_settings(cfg)

    def clear_commers_id():
        cfg = load_settings()
        if cfg.has_section("commers") and "id" in cfg["commers"]:
            cfg.remove_option("commers", "id")
            save_settings(cfg)

    accounts = load_accounts()

    # ──────────────────────────────
    # СНЯТИЕ ЛЬГОТЫ: /commers 0
    # ──────────────────────────────
    if commers_candidate == "0":
        cur_commers_id = get_commers_id()
        if not cur_commers_id or not accounts.has_section(cur_commers_id):
            await update.message.reply_text("❌ Действующий коммерсант не найден.")
            return

        commers_nick = accounts[cur_commers_id].get("nick", cur_commers_id)

        accounts[cur_commers_id]["commers"] = "0"
        accounts[cur_commers_id]["comission"] = "0"
        save_accounts(accounts)
        clear_commers_id()

        try:
            await context.bot.send_message(
                int(cur_commers_id),
                "ℹ️ Ваша льгота <b>Коммерсант</b> была обнулена администрацией.",
                parse_mode="HTML"
            )
        except Exception:
            pass

        await update.message.reply_text(
            f"✅ Льгота Коммерсант снята с пользователя {commers_nick}."
        )
        return

    # ──────────────────────────────
    # Проверка: уже есть коммерсант
    # ──────────────────────────────
    active_commers_id = get_commers_id()
    if active_commers_id and accounts.has_section(active_commers_id):
        commers_nick = accounts[active_commers_id].get("nick", active_commers_id)
        await update.message.reply_text(
            f"❌ Уже назначен коммерсант: {commers_nick} (ID: {active_commers_id})\n"
            "Сначала снимите льготу командой <code>/commers 0</code>.",
            parse_mode="HTML"
        )
        return

    # ──────────────────────────────
    # Поиск пользователя по нику
    # ──────────────────────────────
    target_id = None
    for sec in accounts.sections():
        if accounts[sec].get("nick", "").lower() == commers_candidate.lower():
            target_id = sec
            break

    if not target_id:
        await update.message.reply_text("❌ Пользователь с таким никнеймом не найден.")
        return

    # Уже коммерсант?
    if accounts[target_id].get("commers", "0") == "1":
        await update.message.reply_text(
            f"❗ Пользователь {accounts[target_id].get('nick', target_id)} уже является Коммерсантом."
        )
        return

    # ──────────────────────────────
    # ВЫДАЧА ЛЬГОТЫ
    # ──────────────────────────────
    accounts[target_id]["commers"] = "1"

    # Бонусы Коммерсанта
    accounts[target_id]["t"] = str(int(accounts[target_id].get("t", 0)) + 500)
    accounts[target_id]["exp"] = str(int(accounts[target_id].get("exp", 0)) + 500)
    accounts[target_id]["comission"] = str(int(accounts[target_id].get("comission", 0)) + 5)
    accounts[target_id]["ev_stones"] = str(int(accounts[target_id].get("ev_stones", 0)) + 50)

    save_accounts(accounts)
    set_commers_id(target_id)

    commers_nick = accounts[target_id].get("nick", target_id)

    try:
        await context.bot.send_message(
            int(target_id),
            "🏷 <b>Вам выдана льгота «Коммерсант»!</b>\n\n"
            "<i>Продажи — ваш конёк. Удачных сделок!</i>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await update.message.reply_text(
        f"✅ Льгота Коммерсант выдана пользователю {commers_nick}.",
        parse_mode="HTML"
    )

# ---------- Хендлер /craft ----------
async def craft_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /craft              -> краткая подсказка
    /craft info <id>    -> подробности рецепта
    /craft <id>         -> попытка крафта (списание ресурсов, шанс, эффекты)
    """
    user = update.effective_user
    uid = str(user.id)
    args = context.args or []

    if not args:
        await update.message.reply_text(
            "🔧 Использование /craft:\n"
            "/craft info <id> — подробности рецепта\n"
            "/craft <id> — попытка скрафтить предмет / льготу / ресурс"
        )
        return

    cmd = args[0].lower()
    cfg = load_craft_items()

    # ---------- INFO ----------
    if cmd == "info":
        if len(args) < 2:
            await update.message.reply_text("Укажите ID рецепта: /craft info <id>")
            return

        rid = args[1]
        if not cfg.has_section(rid):
            await update.message.reply_text("❌ Рецепт не найден.")
            return

        rec = _parse_recipe_section(cfg, rid)

        costs_lines = []
        for k, v in rec["costs"].items():
            if v:
                pretty = RESOURCE_NAMES.get(k, k)
                costs_lines.append(f" - {pretty}: {fmt(v)}")

        await update.message.reply_text(
            f"⚖️ <b>Рецепт №{rec['id']} — {rec['name']}</b>\n\n"
            f"{rec['desc']}\n\n"
            f"📟 Базовый шанс: <b>{rec['chance']}%</b>\n"
            f"💰 Стоимость крафта:\n"
            + ("\n".join(costs_lines) if costs_lines else " - нет затрат"),
            parse_mode="HTML"
        )
        return

    # ---------- КРАФТ ----------
    rid = args[0]
    if not cfg.has_section(rid):
        await update.message.reply_text("❌ Рецепт не найден.")
        return

    # cooldown
    now = time.time()
    last = _last_craft_call.get(uid, 0)
    if now - last < CRAFT_COOLDOWN:
        await update.message.reply_text("⏳ Подождите секунду перед новой попыткой крафта.")
        return
    _last_craft_call[uid] = now

    rec = _parse_recipe_section(cfg, rid)
    accounts_cfg = load_accounts()

    # ---------- CRAFTUP ----------
    craftup = 0
    if accounts_cfg.has_section(uid):
        try:
            craftup = int(accounts_cfg[uid].get("craftup", 0))
        except Exception:
            craftup = 0

    base_chance = int(rec["chance"])
    final_chance = min(100, base_chance + craftup)

    bonus_text = (
        f"💎 Бонус к крафту: <b>+{craftup}%</b>\n"
        if craftup > 0 else
        "💎 Бонус к крафту: <b>0%</b>\n"
    )

    # ---------- УНИКАЛЬНОСТЬ ----------
    if rec["unique"] and accounts_cfg.has_section(uid):
        if accounts_cfg[uid].get(f"craft_{rid}") is not None:
            await update.message.reply_text(
                "❗ Вы уже имеете уникальную характеристику этого рецепта — попытка запрещена."
            )
            return

    # ---------- ПРОВЕРКА РЕСУРСОВ ----------
    ok, reason = can_afford(accounts_cfg, uid, rec["costs"])
    if not ok:
        await update.message.reply_text(f"❌ Невозможно начать крафт: {reason}")
        return

    # ---------- СПИСАНИЕ ----------
    deduct_costs(accounts_cfg, uid, rec["costs"])
    save_accounts(accounts_cfg)

    # ---------- БРОСОК ----------
    roll = random.randint(1, 100)
    success = roll <= final_chance

    if success:
        accounts_cfg = load_accounts()
        apply_effects(accounts_cfg, uid, rec["effects"])

        if rec["unique"]:
            accounts_cfg[uid][f"craft_{rid}"] = "1"

        save_accounts(accounts_cfg)

        await update.message.reply_text(
            f"✅ Вы успешно создали: <b>{rec['name']}</b> (шанс: {final_chance}%)\n"
            f"🗄 Информация о предмете: <code>/craft info {rec['id']}</code>",
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            f"❌ Создание <b>{rec['name']}</b> не удалось (шанс: {final_chance}%)\n"
            f"🗄 Информация о предмете: <code>/craft info {rec['id']}</code>",
            parse_mode="HTML"
        )


# ---------- /setcraft — диалог создания рецепта (admin level >= 3) ----------
# Добавьте в начало файла (рядом с другими states) константы SC_NAME..SC_CONFIRM (если ещё нет)
# Conversation flow:
#  name -> desc -> chance -> costs (формат: key=val,comma-separated) -> effects (semicolon-separated) -> unique(y/n) -> confirm
async def setcraft_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    if not user_info or int(user_info.get('is_admin', 0)) < 3:
        await update.message.reply_text("⛔ У вас нет доступа к созданию рецептов.")
        return ConversationHandler.END
    context.user_data['setcraft'] = {}
    await update.message.reply_text("✏️ Введите имя рецепта:")
    return SC_NAME

async def setcraft_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['setcraft']['name'] = update.message.text.strip()
    await update.message.reply_text("📝 Введите описание рецепта:")
    return SC_DESC

async def setcraft_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['setcraft']['desc'] = update.message.text.strip()
    await update.message.reply_text("🎯 Введите шанс успеха в процентах (0-100):")
    return SC_CHANCE

async def setcraft_chance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ch = int(update.message.text.strip())
        if ch < 0 or ch > 100:
            raise ValueError
    except Exception:
        await update.message.reply_text("Введите целое число от 0 до 100.")
        return SC_CHANCE
    context.user_data['setcraft']['chance'] = str(ch)
    await update.message.reply_text(
        "💰 Введите затраты (через запятую). Пример:\n"
        "exp=100, ev_stones=50, osk=10, t=250, personal_account=100000\n"
        "Поля: exp, ev_stones, ball, evball, osk, t, personal_account, oosk, uosk, losk\n"
        "Если ничего — введите 0 или оставьте пустым."
    )
    return SC_COSTS

async def setcraft_costs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    costs = {
        "exp":0,"ev_stones":0,"ball":0,"evball":0,"osk":0,"t":0,
        "personal_account":0,"oosk":0,"uosk":0,"losk":0
    }
    if text:
        parts = [p.strip() for p in text.split(",") if p.strip()]
        for p in parts:
            if "=" in p:
                k,v = p.split("=",1)
                k=k.strip(); v=v.strip()
                if k in costs:
                    try:
                        costs[k] = int(v)
                    except Exception:
                        costs[k] = 0
    context.user_data['setcraft']['costs'] = costs
    await update.message.reply_text(
        "✨ Введите эффекты (через ';'). Поддерживаемые эффекты:\n"
        " add_char:key=value\n"
        " set_field:field=value\n"
        " inc_field:field=amount\n"
        "Пример: add_char:craft_7=1;inc_field:osk=50"
    )
    return SC_EFFECTS

async def setcraft_effects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    # простой валидационный проход - оставить как raw
    context.user_data['setcraft']['effects_raw'] = text
    await update.message.reply_text("🔒 Это уникальный рецепт? (yes/no)")
    return SC_UNIQUE

async def setcraft_unique(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip().lower()
    unique = txt in ("yes","y","да","1","true")
    context.user_data['setcraft']['unique'] = unique

    payload = context.user_data['setcraft']
    costs = payload['costs']
    costs_lines = [f"{k}={v}" for k,v in costs.items() if v]
    effects_preview = payload.get('effects_raw','(нет)')
    preview = (
        f"🔎 Проверьте рецепт:\n"
        f"Имя: {payload.get('name')}\n"
        f"Описание: {payload.get('desc')}\n"
        f"Шанс: {payload.get('chance')}%\n"
        f"Уникальный: {'Да' if unique else 'Нет'}\n"
        f"Затраты: " + (", ".join(costs_lines) if costs_lines else "нет") + "\n"
        f"Эффекты: {effects_preview}\n\n"
        "Введите 'Да' для сохранения, или 'Нет' для отмены."
    )
    await update.message.reply_text(preview)
    return SC_CONFIRM

async def setcraft_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip().lower()
    if txt not in ("да","д","yes","y"):
        await update.message.reply_text("❌ Создание рецепта отменено.")
        context.user_data.pop('setcraft', None)
        return ConversationHandler.END

    # создать новую секцию с новым id (next integer)
    cfg = load_craft_items()
    # find next numeric id
    existing = [int(s) for s in cfg.sections() if s.isdigit()]
    next_id = str((max(existing) + 1) if existing else 1)
    data = context.user_data['setcraft']
    cfg[next_id] = {}
    cfg[next_id]['name'] = data.get('name','item_'+next_id)
    cfg[next_id]['desc'] = data.get('desc','')
    cfg[next_id]['chance'] = data.get('chance','0')
    # costs
    for k,v in data['costs'].items():
        cfg[next_id][f"cost_{k}"] = str(v)
    cfg[next_id]['effects'] = data.get('effects_raw','')
    cfg[next_id]['unique'] = "yes" if data.get('unique') else "no"
    save_craft_items(cfg)
    await update.message.reply_text(f"✅ Рецепт создан с ID {next_id}")
    context.user_data.pop('setcraft', None)
    return ConversationHandler.END

async def setcraft_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('setcraft', None)
    await update.message.reply_text("❌ Создание рецепта отменено.")
    return ConversationHandler.END

def deduct_random_resource(user_id: str, resources: list, amount: int) -> str:
    """
    Снимает случайный ресурс у пользователя. Возвращает название ресурса (с эмодзи), если удалось снять.
    Если ресурсов недостаточно, возвращает None.
    """
    config = load_config(ACCOUNTS_FILE)

    if not config.has_section(user_id):
        return None

    available_resources = [
        resource for resource in resources
        if int(config[user_id].get(resource, 0)) >= amount
    ]

    if not available_resources:
        return None

    chosen_resource = random.choice(available_resources)
    current_amount = int(config[user_id][chosen_resource])
    config[user_id][chosen_resource] = str(current_amount - amount)
    save_config(config, ACCOUNTS_FILE)

    resource_names = {
        "osk": "💈 Бусты",
        "t": "❄ Снежинки",
        "ball": "🧿 Монеты активности",
        "exp": "⚡ EXP"
    }
    return resource_names.get(chosen_resource, chosen_resource)

def format_timedelta(td: timedelta) -> str:
    """
    Форматирование объекта timedelta в читабельный вид: 'X часов, Y минут, Z секунд'.
    """
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours} часов")
    if minutes > 0:
        parts.append(f"{minutes} минут")
    if seconds > 0:
        parts.append(f"{seconds} секунд")

    return ", ".join(parts)

def add_exp(user_id: str, amount: int):
    """
    Добавляет указанное количество EXP пользователю.
    """
    config = load_config(ACCOUNTS_FILE)

    if not config.has_section(user_id):
        config.add_section(user_id)

    current_exp = int(config[user_id].get("exp", 0))  # Получаем текущее значение EXP
    config[user_id]["exp"] = str(current_exp + amount)
    save_config(config, ACCOUNTS_FILE)
    
import random

async def notify_admins_leshey(bot, text: str):
    accounts_cfg = load_config(ACCOUNTS_FILE)

    for uid in accounts_cfg.sections():
        try:
            admin_lvl = int(accounts_cfg[uid].get("is_admin", 0))
            if admin_lvl >= 2:
                await bot.send_message(
                    chat_id=int(uid),
                    text=text,
                    parse_mode="HTML"
                )
        except Exception:
            continue
        
async def mdleh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker_id = str(update.effective_user.id)
    args = context.args

    # Проверяем, указан ли ник жертвы
    if not args:
        await update.message.reply_text("❌ Укажите ник жертвы: /mdleh <ник жертвы>")
        return

    # Проверяем, есть ли характеристика "Проделки Лешего" у атакующего
    attacker_config = load_config(ACCOUNTS_FILE)
    if not attacker_config.has_section(attacker_id) or attacker_config.get(attacker_id, MOD_LESHEY_TATIB, fallback="0") == "0":
        await update.message.reply_text(
            "❌ У вас нет характеристики 'Проделки Лешего'. Приобретите её, чтобы использовать модуль."
        )
        return

    # Составляем полный ник жертвы (учёт пробелов)
    victim_nick = " ".join(args).strip()
    victim_id = find_user_id_by_nick(victim_nick)

    # Проверяем, существует ли жертва
    if not victim_id:
        await update.message.reply_text(f"❌ Жертва с ником '{victim_nick}' не найдена.")
        return

    # Проверяем кулдаун атакующего
    if not is_module_available(attacker_id, MOD_LESHEY_TATIB):
        cooldown_end = get_cooldown_end(attacker_id, MOD_LESHEY_TATIB)
        remaining_time = cooldown_end - datetime.now()
        formatted_time = format_timedelta(remaining_time)  # Форматируем время
        await update.message.reply_text(
            f"⏳ Ваш модуль ещё на кулдауне. Подождите {formatted_time}."
        )
        return

    # Проверяем наличие "Эльфийского оберега" у жертвы
    victim_config = load_config(ACCOUNTS_FILE)
    has_elf_protection = victim_config.has_section(victim_id) and victim_config.get(victim_id, MOD_ELF_PROTECTION, fallback="0") == "1"

    if has_elf_protection:
        # Случайный шанс срабатывания оберега (75%)
        if random.random() < 0.75:
            # Устанавливаем кулдаун для Лешего
            set_cooldown(attacker_id, MOD_LESHEY_TATIB, 12 * 60 * 60)

            # Леший теряет 10 единиц случайного ресурса
            lost_resource = deduct_random_resource(attacker_id, ["osk", "t", "ball", "exp"], 10)

            # Уведомляем Лешего об неудачной атаке
            if lost_resource:
                await update.message.reply_text(
                    f"🧝‍ Леший наткнулся на Эльфийский оберег у {victim_nick}! Атака не удалась, и вы потеряли 10 {lost_resource}."
                )
            else:
                await update.message.reply_text(
                    f"🧝‍ Леший наткнулся на Эльфийский оберег у {victim_nick}! Атака не удалась, а у вас не было ресурсов для потери."
                )

            # Начисляем 10 EXP жертве
            add_exp(victim_id, 10)

            # Уведомляем жертву об атаке
            await context.bot.send_message(
                chat_id=int(victim_id),
                text="🛡 Леший попытался напасть на вас, но ваш Эльфийский оберег заблокировал атаку и вы получили 10 EXP."
            )
            admin_text = (
                "🅰 <b>Новая активность Лешего.</b>\n\n"
                f"👤 <b>Атакующий:</b> {update.effective_user.full_name} ({attacker_id})\n"
                f"🎯 <b>Цель:</b> {victim_nick} ({victim_id})\n"
                f"🛡 <b>Результат:</b> Заблокировано Эльфийским оберегом\n"
                f"📦 <b>Потеря атакующего:</b> {lost_resource or 'нет'}\n"
                f"⏰ <b>Время:</b> {datetime.now().strftime('%H:%M:%S')}"
            )
            await notify_admins_leshey(context.bot, admin_text)
            return

    # Пытаемся украсть 25 единиц случайного ресурса у жертвы
    stolen_resource = deduct_random_resource(victim_id, ["osk", "t", "ball", "exp"], 25)

    # Устанавливаем кулдаун для Лешего
    set_cooldown(attacker_id, MOD_LESHEY_TATIB, 12 * 60 * 60)

    if stolen_resource:
        await update.message.reply_text(
            f"🧌 Вы успешно украли 25 {stolen_resource} у {victim_nick}!"
        )
        admin_text = (
            "🅰 <b>Новая активность Лешего.</b>\n\n"
            f"👤 <b>Атакующий:</b> {update.effective_user.full_name} ({attacker_id})\n"
            f"🎯 <b>Цель:</b> {victim_nick} ({victim_id})\n"
            f"✅ <b>Результат:</b> Успешная кража\n"
            f"📦 <b>Украдено:</b> 25 {stolen_resource}\n"
            f"⏰ <b>Время:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        await notify_admins_leshey(context.bot, admin_text)
        await context.bot.send_message(
            chat_id=int(victim_id),
            text=f"🧌 Леший украл у вас 25 {stolen_resource}, для защиты вам нужен Эльфийский оберег, будьте осторожны."
        )
    else:
        await update.message.reply_text(
            f"😬 У {victim_nick} недостаточно ресурсов для кражи, атака завершилась неудачей, кулдаун активирован."
        )
        admin_text = (
            "🅰 <b>Новая активность Лешего.</b>\n\n"
            f"👤 <b>Атакующий:</b> {update.effective_user.full_name} ({attacker_id})\n"
            f"🎯 <b>Цель:</b> {victim_nick} ({victim_id})\n"
            f"⚠️ <b>Результат:</b> Неудача — недостаточно ресурсов\n"
            f"⏰ <b>Время:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        await notify_admins_leshey(context.bot, admin_text)



#СНЕГУРОЧКА ПРИЛАВОК
async def prilavok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    accounts = load_accounts()

    # 🔐 Проверка характеристики
    if not accounts.has_section(user_id) or accounts[user_id].get("prilavoksnegurka", "0") != "1":
        await update.message.reply_text(
            "⛔ У вас не разблокирован Торговый прилавок Снегурочки."
        )
        return

    # ⏳ Кулдаун
    if not is_module_available(user_id, MOD_SNEGURKA_SHOP):
        cooldown_end = get_cooldown_end(user_id, MOD_SNEGURKA_SHOP)
        remaining = cooldown_end - datetime.now()
        minutes = max(1, int(remaining.total_seconds() // 60))
        await update.message.reply_text(
            f"❄️ Прилавок Снегурочки ещё не готов.\n"
            f"⏳ Осталось: {minutes} мин."
        )
        return

    # ✅ Активация эффекта
    if not accounts.has_section(user_id):
        accounts.add_section(user_id)
    accounts[user_id]["comission"] = "5"
    save_accounts(accounts)

    set_cooldown(user_id, MOD_SNEGURKA_SHOP, COOLDOWN_SNEGURKA_SHOP)

    await update.message.reply_text(
        "🛍🤶 <b>Торговый прилавок Снегурочки активирован!</b>\n\n"
        "📉 Комиссия снижена на <b>5%</b>\n"
        "🎁 Вы можете передать эффект командой:\n"
        "<code>/sendprilavok «никнейм»</code>",
        parse_mode="HTML"
    )

async def sendprilavok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = str(update.effective_user.id)
    accounts = load_accounts()

    # 🔐 Проверка характеристики
    if not accounts.has_section(sender_id) or accounts[sender_id].get("prilavoksnegurka", "0") != "1":
        await update.message.reply_text(
            "⛔ У вас не разблокирован Торговый прилавок Снегурочки."
        )
        return

    # 🎁 Проверка эффекта
    if accounts[sender_id].get("comission", "0") != "5":
        await update.message.reply_text(
            "❌ У вас нет активного эффекта Снегурочки для передачи."
        )
        return

    # 📌 Никнейм (с пробелами)
    if not context.args:
        await update.message.reply_text(
            "⚠️ Укажите никнейм пользователя.\n"
            "Пример:\n"
            "<code>/sendprilavok Бот Северный</code>",
            parse_mode="HTML"
        )
        return

    nick = " ".join(context.args).strip()
    target_id = find_user_id_by_nick(nick)

    if not target_id:
        await update.message.reply_text(
            f"❌ Пользователь <b>{nick}</b> не найден.",
            parse_mode="HTML"
        )
        return

    # ✅ Выдаём эффект получателю
    if not accounts.has_section(target_id):
        accounts.add_section(target_id)
    accounts[target_id]["comission"] = "5"

    save_accounts(accounts)

    # 📤 Ответ отправителю
    await update.message.reply_text(
        f"🎁 <b>Эффект передан!</b>\n\n"
        f"👤 Получатель: <b>{nick}</b>\n"
        f"📉 Комиссия снижена на <b>5%</b> на 5 минут.",
        parse_mode="HTML"
    )

    # 📩 Оповещение получателя
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=(
                "🎁🤶️ <b>Вы получили временный Торговый прилавок Снегурочки!</b>\n\n"
                "📉 Комиссия снижена на <b>5%</b>\n"
                "⏱ Длительность: <b>5 минут</b>\n\n"
                "Используйте его с умом 😉"
            ),
            parse_mode="HTML"
        )
    except Exception:
        pass  # если пользователь не открывал бота

    # ⏱ Авто-снятие эффекта через 5 минут
    async def remove_effect():
        await asyncio.sleep(300)
        acc = load_accounts()
        if acc.has_section(target_id):
            acc[target_id]["comission"] = "0"
            save_accounts(acc)

            # 🔔 Уведомление об окончании
            try:
                await context.bot.send_message(
                    chat_id=target_id,
                    text="🤶 Эффект временного Торгового прилавка Снегурочки завершился.\nКомиссия восстановлена."
                )
            except Exception:
                pass

    asyncio.create_task(remove_effect())

#ИЗБА БАБЫ ЯГИ
async def izba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    accounts = load_accounts()

    if not accounts.has_section(user_id):
        await update.message.reply_text("❌ Аккаунт не найден.")
        return

    state = accounts[user_id].get("izbayagi", "0")

    if state == "0":
        await update.message.reply_text(
            "⛔ У вас нет Торговой избы Бабы Яги."
        )
        return

    if state == "2":
        await update.message.reply_text(
            "🏚 Торговая изба Бабы Яги уже активна."
        )
        return

    # ✅ 1 → 2
    accounts[user_id]["izbayagi"] = "2"
    accounts[user_id]["comission"] = "10"
    save_accounts(accounts)

    await update.message.reply_text(
        "🏚🧟‍  <b>Торговая изба Бабы Яги активирована!</b>\n\n"
        "📉 Комиссия: <b>0%</b>\n"
        "🎲 Каждый перевод с помощью Бабы Яги имеет <b>10%</b> шанс потери ресурсов.\n\n"
        "🔌 Отключение: <code>/izbaoff</code>",
        parse_mode="HTML"
    )

async def izbaoff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    accounts = load_accounts()

    if not accounts.has_section(user_id):
        await update.message.reply_text("❌ Аккаунт не найден.")
        return

    if accounts[user_id].get("izbayagi", "0") != "2":
        await update.message.reply_text(
            "ℹ️ Торговая изба Бабы Яги сейчас не активна."
        )
        return

    # ✅ 2 → 1
    accounts[user_id]["izbayagi"] = "1"
    accounts[user_id]["comission"] = "0"
    save_accounts(accounts)

    await update.message.reply_text(
        "🔌 <b>Торговая изба Бабы Яги отключена.</b>\n"
        "Комиссия восстановлена до стандартной.",
        parse_mode="HTML"
    )
    
async def smoroz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    chat_id = update.effective_chat.id

    # Загрузка аккаунтов
    accounts_cfg = load_accounts()
    if not accounts_cfg.has_section(user_id):
        await update.message.reply_text("❌ Профиль не найден.")
        return

    # Проверка наличия шкатулки
    if accounts_cfg[user_id].get("sdedmoroz", "0") != "1":
        await update.message.reply_text("❌ У вас нет шкатулки «Деда Мороза».")
        return

    # Проверка кулдауна
    cds_cfg = configparser.ConfigParser()
    if os.path.exists(MOD_CDS_FILE):
        cds_cfg.read(MOD_CDS_FILE, encoding="utf-8")
    if not cds_cfg.has_section(user_id):
        cds_cfg.add_section(user_id)

    # безопасно получить last_call
    try:
        last_call = float(cds_cfg[user_id].get(MOD_MOROZ_BOX, "0"))
    except Exception:
        last_call = 0.0

    now = time.time()
    if now - last_call < SDED_MOROZ_COOLDOWN:
        remaining_hours = int((SDED_MOROZ_COOLDOWN - (now - last_call)) / 3600)
        await update.message.reply_text(f"🎅 Шкатулку «Деда Мороза» можно открыть через {remaining_hours} часов.")
        return

    # helper: увеличить числовое поле в аккаунте (безопасно создаёт/читает поле)
    def _inc_account_field(cfg: configparser.ConfigParser, uid: str, field: str, amount: int):
        try:
            cur = int(cfg[uid].get(field, "0"))
        except Exception:
            cur = 0
        cfg[uid][field] = str(cur + int(amount))

    # Генерируем только обычную награду
    choice = random.choice(["t", "ball", "exp", "osk", "ev_stones", "money", "oosk"])
    prize_texts = []

    if choice == "t":
        amt = random.randint(50, 100)
        prize_texts.append(f"→ ❄️ {amt} снежинок")
        _inc_account_field(accounts_cfg, user_id, "t", amt)
    elif choice == "ball":
        amt = random.randint(10, 25)
        prize_texts.append(f"→ 🧿 {amt} монет активности")
        _inc_account_field(accounts_cfg, user_id, "ball", amt)
    elif choice == "exp":
        amt = random.randint(50, 100)
        prize_texts.append(f"→ ⚡ {amt} EXP")
        _inc_account_field(accounts_cfg, user_id, "exp", amt)
    elif choice == "osk":
        amt = random.randint(10, 25)
        prize_texts.append(f"→ 💈 {amt} буст(ов)")
        _inc_account_field(accounts_cfg, user_id, "osk", amt)
    elif choice == "ev_stones":
        amt = random.randint(10, 25)
        prize_texts.append(f"→ 🔥 {amt} респект(ов)")
        _inc_account_field(accounts_cfg, user_id, "ev_stones", amt)
    elif choice == "money":
        amt = random.randint(500_000, 2_500_000)
        prize_texts.append(f"→ 💳 {amt:,}".replace(",", ".") + " RUB")
        _inc_account_field(accounts_cfg, user_id, "money", amt)
    else:  # oosk
        amt = random.randint(25, 100)
        prize_texts.append(f"→ 📘 {amt} O-осколков")
        _inc_account_field(accounts_cfg, user_id, "oosk", amt)

    # Сохраняем изменения в accounts.ini
    try:
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            accounts_cfg.write(f)
    except Exception as e:
        print("Failed to write accounts file (smoroz):", e)
        await update.message.reply_text("⚠️ Ошибка при сохранении награды. Администратор оповещён.")

    # Сообщение пользователю
    header = "🎅 Шкатулка «Деда Мороза» 🎅"
    content = "\n".join(prize_texts)
    comment = "«Шкатулка открылась, пусть новогоднее настроение будет с вами весь год.»"
    full_message = f"{header}\nВам выпало:\n{content}\n\n{comment}"
    await update.message.reply_text(full_message, parse_mode="HTML")

    # Записываем кулдаун
    try:
        cds_cfg[user_id][MOD_MOROZ_BOX] = str(time.time())
        with open(MOD_CDS_FILE, "w", encoding="utf-8") as f:
            cds_cfg.write(f)
    except Exception as e:
        print("Failed to write cooldowns file (smoroz):", e)
        

async def skoshey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    chat_id = update.effective_chat.id

    # Загрузка аккаунтов
    accounts_cfg = load_accounts()
    if not accounts_cfg.has_section(user_id):
        await update.message.reply_text("❌ Профиль не найден.")
        return

    # Проверка наличия шкатулки
    if accounts_cfg[user_id].get(MOD_SKOSHEY_BOX, "0") != "1":
        await update.message.reply_text("❌ У вас нет шкатулки «Кощея Бессмертного».")
        return

    # Проверка кулдауна
    cds_cfg = configparser.ConfigParser()
    if os.path.exists(MOD_CDS_FILE):
        cds_cfg.read(MOD_CDS_FILE, encoding="utf-8")
    if not cds_cfg.has_section(user_id):
        cds_cfg.add_section(user_id)

    # безопасно получить last_call
    try:
        last_call = float(cds_cfg[user_id].get(MOD_SKOSHEY_BOX, "0"))
    except Exception:
        last_call = 0.0

    now = time.time()
    if now - last_call < SDED_MOROZ_COOLDOWN:
        remaining_hours = int((SDED_MOROZ_COOLDOWN - (now - last_call)) / 3600)
        await update.message.reply_text(f"🧛 Шкатулку «Кощея Бессмертного» можно открыть через {remaining_hours} часов.")
        return

    # helper: увеличить числовое поле в аккаунте (безопасно создаёт/читает поле)
    def _inc_account_field(cfg: configparser.ConfigParser, uid: str, field: str, amount: int):
        try:
            cur = int(cfg[uid].get(field, "0"))
        except Exception:
            cur = 0
        cfg[uid][field] = str(cur + int(amount))

    # Риск потерять шкатулку (10%) проверяется первым
    lost_box = False
    if random.randint(1, 100) <= 10:
        accounts_cfg[user_id][MOD_SKOSHEY_BOX] = "0"
        lost_box = True
        # Сохраняем аккаунт сразу, чтобы пользователь больше не смог открыть
        try:
            with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
                accounts_cfg.write(f)
        except Exception as e:
            print("Error saving accounts file after losing box:", e)
            await update.message.reply_text("⚠️ Ошибка при сохранении данных аккаунта. Попробуйте позже.")
            # Записываем кулдаун даже при ошибке сохранения аккаунта (чтобы избежать повторного открытия)
        # Сообщение пользователю без награды
        comment = "❗ В погоне за сокровищем шкатулка «Кощея Бессмертного» потеряна.\n" \
                  "Не грустите, праздничная магия всё равно с вами 🌟"
        full_message = f"🧛‍ Шкатулка «Кощея Бессмертного» 🧛‍\n\n{comment}"
        await update.message.reply_text(full_message, parse_mode="HTML")
    else:
        # Генерируем только уникальную награду
        choice = random.choice(["t", "ball", "exp", "osk", "ev_stones", "personal_account", "uosk"])
        prize_texts = []

        if choice == "t":
            amt = random.randint(250, 500)
            prize_texts.append(f"→ ❄️ {amt} снежинок")
            _inc_account_field(accounts_cfg, user_id, "t", amt)
        elif choice == "ball":
            amt = random.randint(50, 150)
            prize_texts.append(f"→ 🧿 {amt} монет активности")
            _inc_account_field(accounts_cfg, user_id, "ball", amt)
        elif choice == "exp":
            amt = random.randint(250, 500)
            prize_texts.append(f"→ ⚡ {amt} EXP")
            _inc_account_field(accounts_cfg, user_id, "exp", amt)
        elif choice == "osk":
            amt = random.randint(50, 60)
            prize_texts.append(f"→ 💈 {amt} буст(ов)")
            _inc_account_field(accounts_cfg, user_id, "osk", amt)
        elif choice == "ev_stones":
            amt = random.randint(50, 250)
            prize_texts.append(f"→ 🔥 {amt} респект(ов)")
            _inc_account_field(accounts_cfg, user_id, "ev_stones", amt)
        elif choice == "money":
            amt = random.randint(25_000_000, 30_000_000)
            prize_texts.append(f"→ 💳 {amt:,}".replace(",", ".") + " RUB")
            _inc_account_field(accounts_cfg, user_id, "personal_account", amt)
        else:  # uosk
            amt = random.randint(25, 100)
            prize_texts.append(f"→ 📕 {amt} U-осколков")
            _inc_account_field(accounts_cfg, user_id, "uosk", amt)

        # Сохраняем изменения в accounts.ini
        try:
            with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
                accounts_cfg.write(f)
        except Exception as e:
            print("Failed to write accounts file:", e)
            await update.message.reply_text("⚠️ Ошибка при сохранении награды. Администратор оповещён.")
        else:
            # Сообщение пользователю с наградой — только если запись прошла успешно (или даже при ошибке можно сообщать)
            header = "🧛‍ Шкатулка «Кощея Бессмертного» 🧛‍"
            content = "\n".join(prize_texts)
            comment = "«Вы смело открыли шкатулку и получили уникальный подарок от которого веет новогодним настроением»"
            full_message = f"{header}\nВам выпало:\n{content}\n\n{comment}"
            await update.message.reply_text(full_message, parse_mode="HTML")

    # Записываем кулдаун в любом случае
    try:
        cds_cfg[user_id][MOD_SKOSHEY_BOX] = str(time.time())
        with open(MOD_CDS_FILE, "w", encoding="utf-8") as f:
            cds_cfg.write(f)
    except Exception as e:
        print("Failed to write cooldowns file:", e)
        # не критично отправлять ошибку пользователю здесь


def get_main_verstak_keyboard(user_id=None):
    user_info = get_user_info(user_id) if user_id else None
    position = user_info.get("position", "") if user_info else ""

    keyboard = [
        [KeyboardButton("Льготы")],
        [KeyboardButton("Крафтовые наборы")],
        [KeyboardButton("Предметы")],
        [KeyboardButton("Ресурсы")],
        [KeyboardButton("Праздничный крафт")],
        [KeyboardButton("Назад")]
    ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_back_to_verstak_keyboard():
    # Кнопка Назад, возвращающая в центр обмена
    keyboard = [[KeyboardButton("Назад в меню крафтинга")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def verstak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_info = get_user_info(user_id)
    accounts_cfg = load_accounts()

    # ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------
    def safe_int(value, default=0):
        try:
            return int(value or 0)
        except Exception:
            return default

    def fmt(n):
        return f"{int(n):,}".replace(",", ".")

    # ---------- РЕСУРСЫ ----------
    sect = accounts_cfg[user_id] if accounts_cfg.has_section(user_id) else {}

    oosk = safe_int(sect.get("oosk", 0))
    uosk = safe_int(sect.get("uosk", 0))
    losk = safe_int(sect.get("losk", 0))

    current_exp = safe_int(user_info.get("exp", 0))
    ev_stones = safe_int(user_info.get("ev_stones", 0))
    evball = safe_int(user_info.get("evball", 0))
    ball = safe_int(user_info.get("ball", 0))
    osk = safe_int(user_info.get("osk", 0))
    snow = safe_int(user_info.get("t", 0))

    # если нужен лимит EXP — задай явно
    required_exp = safe_int(user_info.get("required_exp", 0))

    oosk_s, uosk_s, losk_s = fmt(oosk), fmt(uosk), fmt(losk)

    # ---------- КАРТИНКА ----------
    try:
        with open("verstak.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
    except FileNotFoundError:
        pass

    # ---------- СООБЩЕНИЕ ----------
    message = (
        "🧱 <b>Крафтинг — это игровая система создания предметов, артефактов или льгот "
        "путём объединения ресурсов, с шансом успеха и особыми эффектами.</b>\n\n"
        "🎑 Что будем крафтить? Выберите из списка.\n\n"
        f"🎏 <b>Ваши ресурсы:</b>\n"
        f"→ 🔥 Респекты: {ev_stones}\n"
        f"→ 🧿 Монеты активности: {ball}\n"
        f"→ 🪙 Монеты эволюции: {evball}\n"
        f"→ 💈 Бусты: {osk}\n"
        f"→ ❄️ Снежинки: {snow}\n"
        f"→ ⚡ Опыт: {current_exp}\n"
        f"→ 📘 O-осколков: {oosk_s}\n"
        f"→ 📕 U-осколков: {uosk_s}\n"
        f"→ 📒 L-осколков: {losk_s}\n\n"
        "<i>ℹ️ Подробности и рецепты крафтов всех предметов: /craft info «ID предмета»</i>"
    )

    await update.message.reply_text(
        message,
        reply_markup=get_main_verstak_keyboard(update.effective_user.id),
        parse_mode="HTML"
    )

async def verstak1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    accounts_cfg = load_accounts()
    craft_cfg = load_craft_items()

    # --- бонус крафта пользователя ---
    craftup = 0
    if accounts_cfg.has_section(user_id):
        try:
            craftup = int(accounts_cfg[user_id].get("craftup", 0))
        except Exception:
            craftup = 0

    def get_final_chance(recipe_id: str) -> int:
        if craft_cfg.has_section(recipe_id):
            try:
                base = int(craft_cfg[recipe_id].get("chance", 0))
            except Exception:
                base = 0
            return min(100, base + craftup)
        return 0

    # Фото
    try:
        with open("verstak.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
    except FileNotFoundError:
        pass

    message = (
        "🎎 <b>Крафтинг ресурсов.</b>\n\n"
        f"📘 <b>O - осколок (📟 — {get_final_chance('1')}%):</b>\n"
        f"🧱 Требование: 3 🔥 3 ❄️ 3 ⚡\n"
        f"Для крафта введите <code>/craft 1</code>\n\n"

        f"📕 <b>U - осколок (📟 — {get_final_chance('2')}%):</b>\n"
        f"🧱 Требование: 25 📘 5 🔥 5 ❄️ 1 💈\n"
        f"Для крафта введите <code>/craft 2</code>\n\n"

        f"📒 <b>L - осколок (📟 — {get_final_chance('3')}%):</b>\n"
        f"🧱 Требование: 25 📕 10 🔥 10 ❄️ 3 💈\n"
        f"Для крафта введите <code>/craft 3</code>\n\n"

        f"🔥 <b>Респект (📟 — {get_final_chance('4')}%):</b>\n"
        f"🧱 Требование: 1 💈 2 🧿 2 ⚡️\n"
        f"Для крафта введите <code>/craft 4</code>\n\n"

        f"❄ <b>Снежинка (📟 — {get_final_chance('5')}%):</b>\n"
        f"🧱 Требование: 1 🧿 1 🔥 1 ⚡️\n"
        f"Для крафта введите <code>/craft 5</code>\n\n"

        "<i>ℹ Примечание: информация о преимуществах всех видов ресурсов доступна "
        "с помощью команды /craft info «ID предмета»</i>"
    )

    await update.message.reply_text(
        message,
        reply_markup=get_back_to_verstak_keyboard(),
        parse_mode="HTML"
    )


async def verstak2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    accounts_cfg = load_accounts()
    # Фото светлой стороны
    try:
        with open("verstak.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
    except FileNotFoundError:
        pass

    message = (
        "🍇 <b>Крафтинг льгот.</b>\n\n"
        f"🥴 На данный момент нет доступных для крафта льгот.\n\n"
        "<i>ℹ Примечание: информация о премуществах всех видов ресурсов доступна с помощью команды /craft info «ID предмета»</i>"
    )
    await update.message.reply_text(message, reply_markup=get_back_to_verstak_keyboard(), parse_mode="HTML")
    
async def verstak3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    accounts_cfg = load_accounts()
    craft_cfg = load_craft_items()

    # --- получаем бонус крафта пользователя ---
    craftup = 0
    if accounts_cfg.has_section(user_id):
        try:
            craftup = int(accounts_cfg[user_id].get("craftup", 0))
        except Exception:
            craftup = 0

    # --- функция для расчёта итогового шанса ---
    def get_final_chance(user_id: str, recipe_id: str) -> int:
        base_chance = 0
        if craft_cfg.has_section(recipe_id):
            try:
                base_chance = int(craft_cfg[recipe_id].get("chance", 0))
            except Exception:
                base_chance = 0
        return min(100, base_chance + craftup)

    # Фото
    try:
        with open("verstak.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
    except FileNotFoundError:
        pass

    message = (
        "🍭 <b>Крафтинг предметов.</b>\n\n"
        f"🗿 <b>Камень выбора (📟 — {get_final_chance(user_id, '6')}%):</b>\n"
        f"🧱 Требование: 5 📕 10 🔥 25 ❄️\n"
        f"Для крафта введите <code>/craft 6</code>\n\n"
        f"🧾 <b>Грамота заместителя (📟 — {get_final_chance(user_id, '15')}%):</b>\n"
        "🧱 Требование: 25 📒 50 🔥 50 🧿 25 💈\n"
        "Для крафта введите <code>/craft 14</code>\n\n"
        "<i>ℹ Примечание: информация о преимуществах всех видов ресурсов доступна с помощью команды "
        "/craft info «ID предмета»</i>"
    )

    await update.message.reply_text(
        message,
        reply_markup=get_back_to_verstak_keyboard(),
        parse_mode="HTML"
    )


async def verstak4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    accounts_cfg = load_accounts()
    craft_cfg = load_craft_items()

    # --- бонус крафта пользователя ---
    craftup = 0
    if accounts_cfg.has_section(user_id):
        try:
            craftup = int(accounts_cfg[user_id].get("craftup", 0))
        except Exception:
            craftup = 0

    # --- рецепт ID = 13 ---
    recipe_id = "13"
    base_chance = 0
    if craft_cfg.has_section(recipe_id):
        try:
            base_chance = int(craft_cfg[recipe_id].get("chance", 0))
        except Exception:
            base_chance = 0

    # --- итоговый шанс ---
    final_chance = min(100, base_chance + craftup)

    # Фото
    try:
        with open("verstak.png", "rb") as photo:
            await update.message.reply_photo(photo=photo)
    except FileNotFoundError:
        pass

    message = (
        "🐉 <b>Крафтинг наборов.</b>\n\n"
        f"🧩 <b>Легендарный набор осколков (📟 — {final_chance}%):</b>\n"
        f"В набор входит: 100 📘 50 📕 25 📒\n"
        f"🧱 Требование: 50 💈 50 🔥 50 ❄️\n"
        f"Для крафта введите <code>/craft {recipe_id}</code>\n\n"
        "<i>ℹ Примечание: информация о преимуществах всех видов ресурсов доступна с помощью команды "
        "/craft info «ID предмета»</i>"
    )

    await update.message.reply_text(
        message,
        reply_markup=get_back_to_verstak_keyboard(),
        parse_mode="HTML"
    )

# ---------- /resetcraft ----------
async def resetcraft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /resetcraft <id> — удаляет рецепт крафта
    Только для админов 3 уровня.
    """
    user_id = update.effective_user.id
    user_info = get_user_info(user_id)
    if not user_info or int(user_info.get('is_admin', 0)) < 3:
        await update.message.reply_text("⛔ У вас нет доступа к удалению рецептов.")
        return

    args = context.args or []
    if not args:
        await update.message.reply_text("❗ Укажите ID рецепта: /resetcraft <id>")
        return

    rid = args[0]
    cfg = load_craft_items()
    if not cfg.has_section(rid):
        await update.message.reply_text(f"❌ Рецепт с ID {rid} не найден.")
        return

    cfg.remove_section(rid)
    save_craft_items(cfg)
    await update.message.reply_text(f"✅ Рецепт с ID {rid} успешно удалён.")

async def resetside_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)

    accounts_cfg = load_accounts()

    if not accounts_cfg.has_section(uid):
        await update.message.reply_text("❌ Профиль не найден.")
        return

    resetside = int(accounts_cfg[uid].get("resetside", 0))

    if resetside <= 0:
        await update.message.reply_text("🗿 У вас нет Камня выбора.")
        return

    # Загружаем стороны
    sides_cfg = configparser.ConfigParser()
    sides_cfg.read("user_sides.ini", encoding="utf-8")

    # Удаляем сторону
    if sides_cfg.has_section(uid):
        sides_cfg.remove_section(uid)
        with open("user_sides.ini", "w", encoding="utf-8") as f:
            sides_cfg.write(f)

    # Списываем камень
    accounts_cfg[uid]["resetside"] = "0"
    save_accounts(accounts_cfg)

    await update.message.reply_text(
        "🗿 <b>Камень выбора активирован!</b>\n\n"
        "⚖️ Ваша сторона очищена.\n"
        "Теперь вы можете заново выбрать путь — Светлый или Тёмный.",
        parse_mode="HTML"
    )

async def grzam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)

    accounts_cfg = load_accounts()
    
    if not accounts_cfg.has_section(uid):
        await update.message.reply_text("❌ Профиль не найден.")
        return

    # Получаем текущий статус грамоты
    grzam_status = int(accounts_cfg[uid].get("grzam", 0))

    if grzam_status == 0:
        await update.message.reply_text("❌ 🧾 У вас нет Грамоты заместителя для активации.")
        return
    elif grzam_status == 2:
        await update.message.reply_text("❌ 🧾 Грамота заместителя уже активирована и не может быть использована повторно.")
        return

    # Применяем эффекты грамоты
    current_comission = int(accounts_cfg[uid].get("comission", 0))
    accounts_cfg[uid]["comission"] = str(current_comission + 3)

    craftup = int(accounts_cfg[uid].get("craftup", 0))
    accounts_cfg[uid]["craftup"] = str(min(100, craftup + 3))  # максимум 100%

    ev_stones = int(accounts_cfg[uid].get("ev_stones", 0))
    exp = int(accounts_cfg[uid].get("exp", 0))
    personal_account = int(accounts_cfg[uid].get("personal_account", 0))

    accounts_cfg[uid]["ev_stones"] = str(ev_stones + 250)
    accounts_cfg[uid]["exp"] = str(exp + 500)
    accounts_cfg[uid]["personal_account"] = str(personal_account + 25_000_000)

    accounts_cfg[uid]["grzam"] = "2"  # активирована

    save_accounts(accounts_cfg)

    await update.message.reply_text(
        "🧾 Вы активировали Грамоту заместителя.\n\n"
        "🍾 Благодарим вас за верность семье СЕВЕРНЫЕ EMPIRE и вклад в общее дело.\n"
        "🎩 Ваши усилия отмечены и вознаграждены.\n\n"
        "✅ Комиссия увеличена на +3%\n"
        "✅ Шанс крафта увеличен на +3%\n"
        "✅ Лимит на вывод увеличен на 50.000.000 RUB\n"
        "✅ На ваш аккаунт зачислено: 250 🔥, 500 ⚡, 25КК 💳\n\n"
        "💬 <i>«Сила хранителя не в мечах, а в мудрости и заботе о тех, кто ему доверен.»</i>\n\n"
        "<i>Грамота теперь активирована и повторно использовать её нельзя.</i>",
        parse_mode="HTML"
    )


async def grchran(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)

    accounts_cfg = load_accounts()
    
    if not accounts_cfg.has_section(uid):
        await update.message.reply_text("❌ Профиль не найден.")
        return

    # Получаем текущий статус грамоты
    grchran_status = int(accounts_cfg[uid].get("grchran", 0))

    if grchran_status == 0:
        await update.message.reply_text("❌ 🧾 У вас нет Грамоты хранителя для активации.")
        return
    elif grchran_status == 2:
        await update.message.reply_text("❌ 🧾 Грамота хранителя уже активирована и не может быть использована повторно.")
        return

    # Применяем эффекты грамоты
    current_comission = int(accounts_cfg[uid].get("comission", 0))
    accounts_cfg[uid]["comission"] = str(current_comission + 5)

    craftup = int(accounts_cfg[uid].get("craftup", 0))
    accounts_cfg[uid]["craftup"] = str(min(100, craftup + 5))  # максимум 100%

    ev_stones = int(accounts_cfg[uid].get("ev_stones", 0))
    exp = int(accounts_cfg[uid].get("exp", 0))
    personal_account = int(accounts_cfg[uid].get("personal_account", 0))

    accounts_cfg[uid]["ev_stones"] = str(ev_stones + 500)
    accounts_cfg[uid]["exp"] = str(exp + 1000)
    accounts_cfg[uid]["personal_account"] = str(personal_account + 50_000_000)

    accounts_cfg[uid]["grchran"] = "2"  # активирована

    save_accounts(accounts_cfg)

    await update.message.reply_text(
        "🧾 Вы активировали Грамоту хранителя.\n\n"
        "🎊 Благодарим вас за верность семье СЕВЕРНЫЕ EMPIRE и вклад в общее дело.\n"
        "🎩 Ваши усилия отмечены и вознаграждены.\n\n"
        "✅ Комиссия увеличена на +5%\n"
        "✅ Шанс крафта увеличен на +5%\n"
        "✅ Лимит на вывод увеличен на 100.000.000 RUB\n"
        "✅ На ваш аккаунт зачислено: 500 🔥, 1К ⚡, 50КК 💳\n\n"
        "<i>Грамота теперь активирована и повторно использовать её нельзя.</i>",
        parse_mode="HTML"
    )

async def ll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    accounts = load_accounts()

    # 🔐 Проверка характеристики (ключ для Лидера — "prilavoklider")
    if not accounts.has_section(user_id) or accounts[user_id].get("prilavoklider", "0") != "1":
        await update.message.reply_text(
            "⛔ У вас не разблокирован ⚙️ Технический прилавок."
        )
        return

    # ⏳ Кулдаун
    if not is_module_available(user_id, MOD_LEADER_SHOP):
        cooldown_end = get_cooldown_end(user_id, MOD_LEADER_SHOP)
        remaining = cooldown_end - datetime.now()
        minutes = max(1, int(remaining.total_seconds() // 60))
        await update.message.reply_text(
            f"⚙ Прилавок технический не готов.\n"
            f"⏳ Осталось: {minutes} мин."
        )
        return

    # ✅ Активация эффекта
    if not accounts.has_section(user_id):
        accounts.add_section(user_id)
    accounts[user_id]["comission"] = "10"  # уменьшение комиссии на 10%
    save_accounts(accounts)

    set_cooldown(user_id, MOD_LEADER_SHOP, COOLDOWN_LEADER_SHOP)

    await update.message.reply_text(
        "⚙ 🛍 <b>Технический прилавок активирован.</b>\n\n"
        "📉 Комиссия снижена до <b>0%</b>\n"
        "🎁 Вы можете передать эффект командой:\n"
        "<code>/sendll «никнейм»</code>",
        parse_mode="HTML"
    )

async def sendll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = str(update.effective_user.id)
    accounts = load_accounts()

    # 🔐 Проверка характеристики
    if not accounts.has_section(sender_id) or accounts[sender_id].get("prilavoklider", "0") != "1":
        await update.message.reply_text(
            "⛔ У вас не разблокирован ⚙ Технический прилавок"
        )
        return

    # 🎁 Проверка эффекта
    if accounts[sender_id].get("comission", "0") != "10":
        await update.message.reply_text(
            "❌ У вас нет активного эффекта Технического прилавка для передачи."
        )
        return

    # 📌 Никнейм (с пробелами)
    if not context.args:
        await update.message.reply_text(
            "⚠️ Укажите никнейм пользователя.\n"
            "Пример:\n"
            "<code>/sendprilavok_leadera Бот Северный</code>",
            parse_mode="HTML"
        )
        return

    nick = " ".join(context.args).strip()
    target_id = find_user_id_by_nick(nick)

    if not target_id:
        await update.message.reply_text(
            f"❌ Пользователь <b>{nick}</b> не найден.",
            parse_mode="HTML"
        )
        return

    # ✅ Выдаём эффект получателю
    if not accounts.has_section(target_id):
        accounts.add_section(target_id)
    accounts[target_id]["comission"] = "10"

    save_accounts(accounts)

    # 📤 Ответ отправителю
    await update.message.reply_text(
        f"🎁 <b>Эффект передан!</b>\n\n"
        f"👤 Получатель: <b>{nick}</b>\n"
        f"📉 Комиссия снижена до <b>0%</b> на 5 минут.",
        parse_mode="HTML"
    )

    # 📩 Оповещение получателя
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=(
                "⚙️ <b>Вы получили временный Технический прилавок.</b>\n"
                "📉 Комиссия снижена до <b>0%</b>\n"
                "⏱ Длительность: <b>5 минут</b>\n\n"
                "Нужна для технических выдачей без комиссии."
            ),
            parse_mode="HTML"
        )
    except Exception:
        pass  # если пользователь не открывал бота

    # ⏱ Авто-снятие эффекта через 5 минут
    async def remove_effect():
        await asyncio.sleep(300)
        acc = load_accounts()
        if acc.has_section(target_id):
            acc[target_id]["comission"] = "0"
            save_accounts(acc)

            # 🔔 Уведомление об окончании
            try:
                await context.bot.send_message(
                    chat_id=target_id,
                    text="⚙️ Эффект временного технического прилавка завершился.\nКомиссия восстановлена."
                )
            except Exception:
                pass

    asyncio.create_task(remove_effect())    
    
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
    application.add_handler(CommandHandler("lvlconf", lvlconf))
    application.add_handler(CommandHandler("removewarn", removewarn))
    application.add_handler(CommandHandler("bonus", bonus))
    application.add_handler(CommandHandler("rdbonus", rdbonus))
    application.add_handler(CommandHandler("ot", report))
    application.add_handler(CommandHandler("evolution", evolution_handler))
    application.add_handler(CommandHandler("lg", lg_handler))
    application.add_handler(CommandHandler("ahelp", admin_help))
    application.add_handler(CommandHandler("leader", leader))
    application.add_handler(CommandHandler("szam", szam))
    application.add_handler(CommandHandler("piarvr", piarvr))
    application.add_handler(CommandHandler("pactivate", pactivate))
    application.add_handler(CommandHandler("mining", mining))
    application.add_handler(CommandHandler("mactivate", mactivate))
    application.add_handler(CommandHandler("respect", respect))
    application.add_handler(CommandHandler("setsinfo", setsinfo))
    application.add_handler(CommandHandler("setslimit", setslimit))
    application.add_handler(CommandHandler("happy", happy))
    application.add_handler(CommandHandler("commers", commers))
    application.add_handler(CommandHandler("grzam", grzam))
    application.add_handler(CommandHandler("grchran", grchran))
    application.add_handler(CommandHandler("resetside", resetside_command))
    application.add_handler(conv_addtask)
    application.add_handler(CommandHandler("deltask", deltask_command))
    application.add_handler(CommandHandler("tasks", tasks_command))
    application.add_handler(CallbackQueryHandler(tasks_nav_callback, pattern=r"^tasks_nav_\d+$"))
    application.add_handler(CallbackQueryHandler(tasks_accept_callback, pattern=r"^tasks_accept_\d+$"))
    application.add_handler(CallbackQueryHandler(tasks_finish_callback, pattern=r"^tasks_finish_\d+$"))
    application.add_handler(CallbackQueryHandler(tasks_close_callback, pattern=r"^tasks_close$"))
    application.add_handler(CallbackQueryHandler(task_delete_callback, pattern=r"^task_delete_\d+$"))
    application.add_handler(CallbackQueryHandler(task_delete_confirm_callback, pattern=r"^task_delete_confirm_\d+$"))
    application.add_handler(CommandHandler("reject", reject_task_command))   # <-- добавьте эту строку
    application.add_handler(CommandHandler("confirm", confirm_task_command))
    application.add_handler(CallbackQueryHandler(evolution_callback_handler, pattern="^evolution_(yes|no)$"))
    application.add_handler(conv_reg)
    # craft
    application.add_handler(CommandHandler("craft", craft_command))
    application.add_handler(CommandHandler("resetcraft", resetcraft))
    conv_setcraft = ConversationHandler(
        entry_points=[CommandHandler("setcraft", setcraft_start)],
        states={
            SC_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, setcraft_name)],
            SC_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, setcraft_desc)],
            SC_CHANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, setcraft_chance)],
            SC_COSTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, setcraft_costs)],
            SC_EFFECTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, setcraft_effects)],
            SC_UNIQUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, setcraft_unique)],
            SC_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, setcraft_confirm)],
        },
        fallbacks=[CommandHandler("cancel", setcraft_cancel)],
        per_user=True
    )
    application.add_handler(conv_setcraft)
    application.add_handler(CommandHandler("mdleh", mdleh))       # Проделки Лешего
    application.add_handler(CommandHandler("prilavok", prilavok)) # Торговый прилавок Снегурочки
    application.add_handler(CommandHandler("sendprilavok", sendprilavok))
    application.add_handler(CommandHandler("izba", izba))
    application.add_handler(CommandHandler("izbaoff", izbaoff))  
    application.add_handler(CommandHandler("smoroz", smoroz))     # Шкатулка Деда Мороза
    application.add_handler(CommandHandler("skoshey", skoshey))   # Шкатулка Кощея Бессмертного
    application.add_handler(CommandHandler("ll", ll)) # Торговый прилавок Снегурочки
    application.add_handler(CommandHandler("sendll", sendll))
    # Обработчики регистрации
    application.add_handler(CallbackQueryHandler(admin, pattern="^admin$"))
    application.add_handler(CallbackQueryHandler(view_registrations, pattern="^view_registrations$"))
    application.add_handler(CallbackQueryHandler(reg_detail, pattern="^reg_detail_.*$"))
    application.add_handler(CallbackQueryHandler(reg_approve, pattern=r"^reg_approve_[a-zA-Z0-9]+$"))
    application.add_handler(CallbackQueryHandler(reg_reject, pattern="^reg_reject_.*"))
    application.add_handler(CallbackQueryHandler(delete_user_account, pattern="^delete_user_account_.*$"))
    application.add_handler(CommandHandler("aactive", aactive))
    application.add_handler(CallbackQueryHandler(aactive_callback, pattern="^pos_"))
    # Обработчики колбэков (пополнение)
    application.add_handler(CallbackQueryHandler(start_deposit, pattern="^deposit_start$"))
    application.add_handler(CallbackQueryHandler(admin_deposits, pattern="^admin_deposits$"))
    application.add_handler(CallbackQueryHandler(view_deposit, pattern="^viewdep_"))
    application.add_handler(CallbackQueryHandler(approve_deposit, pattern="^approvedep_"))
    application.add_handler(CallbackQueryHandler(reject_deposit, pattern="^rejectdep_"))
    application.add_handler(CommandHandler("limited_sets", limited_sets))
    application.add_handler(CommandHandler("buys", buys))
    application.add_handler(CommandHandler("buyt", buyt))
    # Обработчики колбэков (заявки на вывод)
    application.add_handler(CallbackQueryHandler(handle_withdrawal_selection, pattern=r'^withdraw_\d+$'))
    application.add_handler(CallbackQueryHandler(confirm_withdraw_request, pattern=r"^confirm_withdraw$"))
    application.add_handler(CallbackQueryHandler(cancel_withdraw_request, pattern=r"^cancel_withdraw$"))
    application.add_handler(CallbackQueryHandler(view_withdrawal, pattern=r"^view_[a-zA-Z0-9]{8}$"))
    application.add_handler(CallbackQueryHandler(approve_withdrawal, pattern=r"^approve_[a-zA-Z0-9]{8}$"))
    application.add_handler(CallbackQueryHandler(reject_withdrawal, pattern=r"^reject_[a-zA-Z0-9]{8}$"))
    application.add_handler(CallbackQueryHandler(admin_withdrawals, pattern=r"^admin_withdrawals$"))
    application.add_handler(CallbackQueryHandler(start_custom_withdrawal, pattern="^withdraw_custom$"))
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
    application.add_handler(CallbackQueryHandler(new_obnova, pattern="^new_obnova$"))
    application.add_handler(CallbackQueryHandler(change_rd, pattern="^change_rd$"))
    application.add_handler(CallbackQueryHandler(cancel_change_rd, pattern='^cancel_change_rd$'))
    application.add_handler(CallbackQueryHandler(handle_back_to_user_edit, pattern="^cancel_change_nick$"))
    application.add_handler(CallbackQueryHandler(rating_results_handler, pattern="^rating_results$"))
    application.add_handler(CallbackQueryHandler(rating_confirm_handler, pattern="^rating_confirm_(yes|no)$"))
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
    application.add_handler(CallbackQueryHandler(callback_router))

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
