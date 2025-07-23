# bot.py

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from fuzzywuzzy import fuzz
from parser import parse_vk_education_courses

vk_session = vk_api.VkApi(token="vk1.a.rM7jjKpwccx0heaZpDKq5kWOXC3lni6tpOS0NkxJWmPpTwf0RHGOSR9KKfRslDm6V6lHZNobhQj48Fp1Sk_5X2g_htKfHdlrDyfC0ILghiNwYDqd9ry7veRIaMjGnh33mELsyEa1NuiOLVsOQ_0b5ZdObxP1CRUGREfaUY-UWLP3jsaWOlLEiEsXlAg697vR2FanTJXzVdxepcI1vHYWBQ")
vk = vk_session.get_api()
longpoll = VkLongPoll(vk)

courses = parse_vk_education_courses()

bad_words = ["дурак", "тупой", "бл", "сука", "хер", "мат"]  # можно расширить

def check_mat(text):
    return any(word in text.lower() for word in bad_words)

def send_message(user_id, message, keyboard=None):
    vk.messages.send(
        user_id=user_id,
        message=message,
        random_id=0,
        keyboard=keyboard.get_keyboard() if keyboard else None
    )

def create_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Как выбрать проект?", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Где найти вебинары?", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Как загрузить решение?", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("Какие проекты для студентов?", color=VkKeyboardColor.POSITIVE)
    return keyboard

def search_course_by_name(name):
    for course in courses:
        if fuzz.partial_ratio(course["title"].lower(), name.lower()) > 80:
            return course
    return None

def search_courses_by_audience(word):
    return [c for c in courses if word.lower() in c["audience"].lower()]

def search_courses_by_topic(keyword):
    return [c for c in courses if keyword.lower() in c["topics"].lower()]

def handle_question(text):
    text = text.strip().lower()

    if check_mat(text):
        return "Пожалуйста, соблюдай уважительный тон 🛑"

    if "привет" in text:
        return "Привет! Я бот от VK Education. Задавай вопросы или выбери кнопку 👇"

    if "как выбрать проект" in text:
        return "Перейди на сайт https://education.vk.company/students#courses и выбери тот, что тебе интересен!"

    if "загрузить решение" in text:
        return "Просто прикрепи файл в конце занятия на сайте VK Education."

    if "вебинар" in text:
        return "Записи доступны на странице проекта или в Telegram-канале VK Education."

    if "для студентов" in text:
        found = search_courses_by_audience("студент")
        if found:
            return "Вот проекты для студентов:\n" + "\n".join([f"• {c['title']}" for c in found])
        return "Не найдено проектов для студентов 😕"

    if "формат" in text:
        for course in courses:
            if fuzz.partial_ratio(course["title"].lower(), text) > 80:
                return f"Формат проекта «{course['title']}»: {course['format']}"
        return "Не нашёл формат для указанного проекта."

    if "срок" in text or "длительность" in text:
        for course in courses:
            if fuzz.partial_ratio(course["title"].lower(), text) > 80:
                return f"Длительность проекта «{course['title']}»: {course['duration']}"
        return "Не нашёл длительность для указанного проекта."

    if "темы" in text or "направление" in text:
        for course in courses:
            if fuzz.partial_ratio(course["title"].lower(), text) > 80:
                return f"Темы проекта «{course['title']}»: {course['topics']}"
        return "Не нашёл описание тем проекта."

    if any(word in text for word in ["фронтенд", "frontend", "искусственный интеллект", "ai", "дизайн", "данные"]):
        keyword = text
        found = search_courses_by_topic(keyword)
        if found:
            return "Вот подходящие курсы по твоей теме:\n" + "\n".join([f"• {c['title']}" for c in found])
        return "Не нашёл подходящих курсов по этой теме."

    return "Пока не знаю, как ответить 🤔 Попробуй переформулировать или воспользуйся кнопками ниже!"

# --- Основной цикл ---
keyboard = create_keyboard()

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id = event.user_id
        msg = event.text
        answer = handle_question(msg)
        send_message(user_id, answer, keyboard=keyboard)
