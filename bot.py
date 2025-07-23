import os
import json
import requests
from bs4 import BeautifulSoup
import difflib
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

# === VK API setup ===
token = os.getenv("TOKEN")
vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

print("✅ Бот запущен!")

# === Функция парсинга курсов VK Education ===
def parse_vk_education_courses():
    url = "https://education.vk.company/students#courses"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except Exception as e:
        print("Ошибка при парсинге сайта:", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    
    courses = []

    # Здесь ориентируемся на структуру сайта — 
    # Нужно изучить структуру блоков с курсами.
    # Например, предположим что курсы в div с классом 'course-card' (пример)
    
    course_cards = soup.find_all("div", class_="course-card")
    if not course_cards:
        # fallback: ищем заголовки h3 как пример
        course_cards = soup.find_all("h3")
        for c in course_cards:
            title = c.get_text(strip=True)
            if title:
                courses.append({
                    "title": title,
                    "duration": "Информация не найдена",
                    "topics": "Информация не найдена",
                    "format": "Информация не найдена"
                })
        return courses

    # Если нашли курсы по классу 'course-card'
    for card in course_cards:
        title = card.find("h3")
        duration = card.find(class_="duration")   # примеры классов, надо проверить на сайте
        topics = card.find(class_="topics")
        fmt = card.find(class_="format")

        courses.append({
            "title": title.get_text(strip=True) if title else "Без названия",
            "duration": duration.get_text(strip=True) if duration else "Не указано",
            "topics": topics.get_text(strip=True) if topics else "Не указано",
            "format": fmt.get_text(strip=True) if fmt else "Не указано",
        })

    return courses

# Попытка получить курсы при старте бота
courses_data = parse_vk_education_courses()

# === FAQ с базовыми ответами и кнопками ===
faq = {
    "как выбрать проект": "Чтобы выбрать проект, зайди на сайт https://education.vk.company/students#courses и выбери подходящий.",
    "можно ли взять несколько проектов": "Да, ты можешь участвовать сразу в нескольких проектах.",
    "как загрузить решение": "Просто прикрепи файл в конце занятия на сайте VK Education.",
    "где найти записи вебинаров": "Записи доступны на странице проекта или в Telegram-канале VK Education.",
    "сколько длится проект": "Обычно проекты длятся от 2 до 8 недель, точные сроки указаны на странице.",
    "привет": "Привет, я бот от VK Education и помогу тебе со всеми вопросами о твоих учебных программах!"
}

keyboard = {
    "one_time": False,
    "buttons": [
        [{"action": {"type": "text", "label": "Как выбрать проект?"}, "color": "primary"}],
        [{"action": {"type": "text", "label": "Можно ли взять несколько проектов?"}, "color": "primary"}],
        [{"action": {"type": "text", "label": "Как загрузить решение?"}, "color": "primary"}],
        [{"action": {"type": "text", "label": "Где найти записи вебинаров?"}, "color": "secondary"}],
        [{"action": {"type": "text", "label": "Сколько длится проект?"}, "color": "secondary"}],
    ]
}
keyboard_json = json.dumps(keyboard, ensure_ascii=False).encode('utf-8').decode('utf-8')

# === Функция для fuzzy matching ===
def get_best_match(user_msg, questions):
    user_msg = user_msg.lower()
    matches = difflib.get_close_matches(user_msg, questions, n=1, cutoff=0.5)
    return matches[0] if matches else None

# === Функция обработки вопросов про курсы ===
def answer_about_courses(msg, courses):
    msg = msg.lower()

    # Примеры ключевых слов для поиска по курсам
    if any(word in msg for word in ["фронтенд", "frontend", "верстка"]):
        # Ищем курсы с темой фронтенд
        matched = [c for c in courses if "фронтенд" in c["topics"].lower() or "frontend" in c["topics"].lower()]
        if matched:
            response = "Вот курсы, в которых затрагивается тема фронтенд разработки:\n"
            for c in matched:
                response += f"- {c['title']} (Сроки: {c['duration']}, Формат: {c['format']})\n"
            return response
        else:
            return "К сожалению, курсы с темой фронтенд не найдены."

    # Пример: запрос о сроках конкретного проекта
    if "срок" in msg or "длится" in msg:
        # Ищем название проекта в сообщении
        for course in courses:
            if course["title"].lower() in msg:
                return f"Проект «{course['title']}» длится: {course['duration']}."

    # Можно добавить больше правил и проверок

    return None

# === Главный цикл бота ===
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        text = event.text.lower()

        # Сначала проверяем FAQ с fuzzy
        matched_question = get_best_match(text, list(faq.keys()))
        if matched_question:
            answer = faq[matched_question]
        else:
            # Проверяем вопросы по курсам
            answer = answer_about_courses(text, courses_data)

        if not answer:
            answer = "Извини, я не понял вопрос. Попробуй переформулировать или выбери вопрос из кнопок ниже 👇"

        vk.messages.send(
            user_id=event.user_id,
            message=answer,
            random_id=0,
            keyboard=keyboard_json
        )
