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


def extract_related_text(topics):
    for topic in topics:
        if isinstance(topic, dict):
            if topic.get("Text"):
                return topic["Text"]
            # Рекурсивный случай, если вложенный список
            if topic.get("Topics"):
                text = extract_related_text(topic["Topics"])
                if text:
                    return text
    return None

def search_external_sources(query):
    try:
        params = {
            "q": query,
            "format": "json",
            "no_redirect": 1,
            "no_html": 1,
            "skip_disambig": 1
        }
        response = requests.get("https://api.duckduckgo.com/", params=params)
        data = response.json()

        # Проверяем несколько возможных полей с ответами
        for field in ["AbstractText", "Definition", "Answer"]:
            if data.get(field):
                return data[field]

        # Рекурсивно проверяем RelatedTopics
        related_text = extract_related_text(data.get("RelatedTopics", []))
        if related_text:
            return related_text

        # Проверяем поле Results (список)
        results = data.get("Results", [])
        if results:
            for res in results:
                if res.get("Text"):
                    return res["Text"]

        return "Извините, я не нашёл полезной информации. Попробуйте переформулировать запрос."
    except Exception as e:
        print("Ошибка при поиске:", e)
        return "Произошла ошибка при обращении к интернет-источникам."



# === Главный цикл бота ===
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        text = event.text.lower()

        # Сначала проверяем FAQ с fuzzy
        matched_question = get_best_match(text, list(faq.keys()))
        if matched_question:
            answer = faq[matched_question]
        else:
            answer = search_external_sources(text)

        vk.messages.send(
            user_id=event.user_id,
            message=answer,
            random_id=0,
            keyboard=keyboard_json
        )
