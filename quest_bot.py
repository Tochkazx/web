"""
🎁 КВЕСТ-БОТ ДЛЯ ПОДАРКА
Опросник, который определяет какую подписку получит девушка: 3, 6 или 12 месяцев.

Установка:
    pip install pyTelegramBotAPI

Запуск:
    1. Вставь свой BOT_TOKEN (получить у @BotFather)
    2. python quest_bot.py
"""

import telebot
from telebot import types
import json

# ===================== НАСТРОЙКИ =====================

BOT_TOKEN = "ВСТАВЬ_СВОЙ_TOKEN_ЗДЕСЬ"  # Получить у @BotFather в Telegram

# Что написать в финале в зависимости от результата
PRIZES = {
    "3": {
        "title": "🥉 Подписка на 3 месяца!",
        "text": (
            "Ты прошла квест и заработала подписку на 3 месяца! 🎉\n\n"
            "Это только начало — следи за следующими квестами, там будет ещё интереснее 😉\n\n"
            "Твой подарочный код: <b>GIFT-3M-XXXX</b>\n"
            "_(замени XXXX на реальный код)_"
        ),
    },
    "6": {
        "title": "🥈 Подписка на 6 месяцев!",
        "text": (
            "Вау, ты знаешь меня лучше, чем я думал! 😍\n\n"
            "За это — подписка на целых 6 месяцев! 🎁\n\n"
            "Твой подарочный код: <b>GIFT-6M-XXXX</b>\n"
            "_(замени XXXX на реальный код)_"
        ),
    },
    "12": {
        "title": "🥇 Подписка на 12 месяцев!",
        "text": (
            "МАКСИМУМ! Ты потрясающая! 🏆✨\n\n"
            "Ты ответила на всё идеально — держи подписку на целый год!\n\n"
            "Твой подарочный код: <b>GIFT-12M-XXXX</b>\n"
            "_(замени XXXX на реальный код)_"
        ),
    },
}

# ===================== ВОПРОСЫ =====================
# Каждый ответ добавляет баллы. Сумма определяет приз:
#   0–4  баллов → 3 месяца
#   5–8  баллов → 6 месяцев
#   9+   баллов → 12 месяцев
#
# Структура: {"text": "Текст вопроса", "options": [{"text": "Текст ответа", "points": N}, ...]}

QUESTIONS = [
    {
        "text": "💭 Вопрос 1: Какой твой любимый способ провести выходной день?",
        "options": [
            {"text": "🛋 Дома, в тишине и уюте", "points": 1},
            {"text": "🌿 Прогулка на природе", "points": 2},
            {"text": "🎭 Куда-нибудь выбраться — кино, кафе, галерея", "points": 3},
            {"text": "🎉 Вечеринка или встреча с друзьями", "points": 3},
        ],
    },
    {
        "text": "🍕 Вопрос 2: Что закажешь на ужин, если выбор за тобой?",
        "options": [
            {"text": "🍣 Суши или роллы", "points": 2},
            {"text": "🍕 Пицца — всегда беспроигрышно", "points": 1},
            {"text": "🥗 Что-то лёгкое и полезное", "points": 3},
            {"text": "🍔 Бургер, и никаких компромиссов", "points": 2},
        ],
    },
    {
        "text": "🎬 Вопрос 3: Что выберешь для вечера вдвоём?",
        "options": [
            {"text": "😂 Комедия — чтобы посмеяться", "points": 1},
            {"text": "💕 Романтика — классика жанра", "points": 3},
            {"text": "😱 Триллер — адреналин приветствуется", "points": 2},
            {"text": "🎞 Что угодно, главное — вместе", "points": 3},
        ],
    },
    {
        "text": "💝 Вопрос 4: Какой подарок тебе нравится больше всего?",
        "options": [
            {"text": "💐 Цветы — просто и красиво", "points": 1},
            {"text": "✨ Что-то неожиданное и с душой", "points": 3},
            {"text": "💆 Совместный опыт — поездка, ужин, SPA", "points": 3},
            {"text": "🛍 Что-то полезное из вишлиста", "points": 2},
        ],
    },
    {
        "text": "🌙 Вопрос 5: Что для тебя важнее всего в отношениях?",
        "options": [
            {"text": "🤝 Поддержка и понимание", "points": 2},
            {"text": "😂 Смех и лёгкость", "points": 2},
            {"text": "🔥 Страсть и интерес", "points": 3},
            {"text": "🏠 Надёжность и стабильность", "points": 1},
        ],
    },
]

# ===================== КОД БОТА =====================

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Хранилище состояний пользователей: {user_id: {"step": N, "points": N}}
user_state = {}


def get_question_markup(question_index: int) -> types.InlineKeyboardMarkup:
    """Создаёт клавиатуру с вариантами ответа для вопроса."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    q = QUESTIONS[question_index]
    for i, option in enumerate(q["options"]):
        callback_data = f"answer_{question_index}_{i}"
        markup.add(types.InlineKeyboardButton(option["text"], callback_data=callback_data))
    return markup


def send_question(chat_id: int, question_index: int):
    """Отправляет очередной вопрос."""
    q = QUESTIONS[question_index]
    progress = f"<i>Вопрос {question_index + 1} из {len(QUESTIONS)}</i>\n\n"
    bot.send_message(chat_id, progress + q["text"], reply_markup=get_question_markup(question_index))


def determine_prize(points: int) -> str:
    """Определяет приз по сумме баллов."""
    if points >= 9:
        return "12"
    elif points >= 5:
        return "6"
    else:
        return "3"


def send_result(chat_id: int, points: int):
    """Отправляет финальный результат с призом."""
    prize_key = determine_prize(points)
    prize = PRIZES[prize_key]

    # Прогресс-бар для баллов (макс ~15)
    max_points = len(QUESTIONS) * 3
    filled = int((points / max_points) * 10)
    bar = "🟩" * filled + "⬜" * (10 - filled)

    result_text = (
        f"🎊 <b>Квест пройден!</b>\n\n"
        f"Твои баллы: {bar} {points}/{max_points}\n\n"
        f"<b>{prize['title']}</b>\n\n"
        f"{prize['text']}"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Пройти ещё раз", callback_data="restart"))

    bot.send_message(chat_id, result_text, reply_markup=markup)


# ===================== ХЕНДЛЕРЫ =====================

@bot.message_handler(commands=["start"])
def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_state[user_id] = {"step": 0, "points": 0}

    name = message.from_user.first_name or "красавица"

    intro = (
        f"Привет, <b>{name}</b>! 🎁\n\n"
        "Для тебя подготовлен маленький квест — ответь на несколько вопросов, "
        "и в конце тебя ждёт сюрприз! 🎀\n\n"
        "Отвечай честно — это важно 😉\n\n"
        "Готова? Поехали! 🚀"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✨ Начать квест", callback_data="start_quest"))

    bot.send_message(message.chat.id, intro, reply_markup=markup)


@bot.message_handler(commands=["help"])
def cmd_help(message: types.Message):
    bot.send_message(
        message.chat.id,
        "ℹ️ Это квест-бот с сюрпризом!\n\n"
        "/start — начать квест\n\n"
        "Просто отвечай на вопросы кнопками и жди финала 🎁",
    )


@bot.callback_query_handler(func=lambda call: call.data == "start_quest" or call.data == "restart")
def handle_start_quest(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_state[user_id] = {"step": 0, "points": 0}

    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    send_question(call.message.chat.id, 0)


@bot.callback_query_handler(func=lambda call: call.data.startswith("answer_"))
def handle_answer(call: types.CallbackQuery):
    user_id = call.from_user.id

    # Если состояние не найдено — попросить /start
    if user_id not in user_state:
        bot.answer_callback_query(call.id, "Напиши /start чтобы начать! 🙂")
        return

    state = user_state[user_id]

    # Парсим callback: answer_{question_index}_{option_index}
    parts = call.data.split("_")
    q_index = int(parts[1])
    o_index = int(parts[2])

    # Защита от двойного нажатия / устаревших кнопок
    if q_index != state["step"]:
        bot.answer_callback_query(call.id, "Ты уже ответила на этот вопрос 😊")
        return

    # Начисляем баллы
    points_earned = QUESTIONS[q_index]["options"][o_index]["points"]
    state["points"] += points_earned
    state["step"] += 1

    # Убираем кнопки у текущего вопроса
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    selected_text = QUESTIONS[q_index]["options"][o_index]["text"]
    bot.answer_callback_query(call.id, f"✅ Выбрано: {selected_text}")

    # Следующий вопрос или финал
    if state["step"] < len(QUESTIONS):
        send_question(call.message.chat.id, state["step"])
    else:
        total_points = state["points"]
        del user_state[user_id]  # Очищаем состояние
        send_result(call.message.chat.id, total_points)


# Обработка любого текста (если пишут руками)
@bot.message_handler(func=lambda m: True)
def handle_text(message: types.Message):
    bot.send_message(
        message.chat.id,
        "Пользуйся кнопками 😊\nЕсли потерялась — напиши /start"
    )


# ===================== ЗАПУСК =====================

if __name__ == "__main__":
    print("🤖 Бот запущен! Нажми Ctrl+C для остановки.")
    print(f"📊 Вопросов: {len(QUESTIONS)}")
    print(f"🎁 Призы: 3 / 6 / 12 месяцев")
    print("─" * 40)

    bot.infinity_polling(timeout=10, long_polling_timeout=5)
