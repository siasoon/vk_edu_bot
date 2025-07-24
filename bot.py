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
    "как выбрать и записаться на проект": "Чтобы выбрать проект, зайди на сайт https://education.vk.company/students#courses и выбери подходящий.",
    "можно ли взять несколько проектов": "Да, ты можешь участвовать сразу в нескольких проектах.",
    "как загрузить решение": "Просто прикрепи файл в конце занятия на сайте VK Education.",
    "где найти записи вебинаров": "Записи доступны на странице проекта или в Telegram-канале VK Education.",
    "сколько длится проект": "Обычно проекты длятся от 2 до 8 недель, точные сроки указаны на странице.",
    "привет": "Привет, я бот от VK Education и помогу тебе со всеми вопросами о твоих учебных программах!",
    "спасибо": "Всегда пожалуйста! Надеюсь я ответил на твой вопрос, обращайся по другим вопросам, я помогу."
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

def get_best_match(user_msg, questions):
    user_msg = user_msg.lower()
    matches = difflib.get_close_matches(user_msg, questions, n=1, cutoff=0.5)
    return matches[0] if matches else None

def search_with_serpapi(query):
    try:
        params = {
            "q": query,
            "api_key": "85e1420dec2be33b79c5a2fa46f4cdceb16bceb7287340626eebc3dedd008a0e",  # ← сюда вставь свой ключ
            "engine": "google",
            "num": 1
        }
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()

        if "organic_results" in data and data["organic_results"]:
            return data["organic_results"][0]["snippet"]
        else:
            return "Ничего не нашлось через интернет-поиск."
    except Exception as e:
        print("Ошибка SerpAPI:", e)
        return "Произошла ошибка при поиске."

banned_words = ["блять", "сука", "нахуй", "пизд", "ебан", "хуй", "чмо", "мразь", "гандон",
    "долбаёб", "урод", "сволочь", "тварь"]

def contains_profanity(text):
    words = text.lower().split()
    for word in words:
        for banned in banned_words:
            if banned in word:
                return True
    return False

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        text = event.text.lower()
        if contains_profanity(text):
            vk.messages.send(
                user_id=event.user_id,
                message="Пожалуйста, соблюдайте нормы общения. Ваш вопрос содержит недопустимые выражения.",
                random_id=0,
                keyboard=keyboard_json
            )
            continue  
        matched_question = get_best_match(text, list(faq.keys()))
        if matched_question:
            answer = faq[matched_question]
        else:
            answer = search_with_serpapi(text)

        vk.messages.send(
            user_id=event.user_id,
            message=answer,
            random_id=0,
            keyboard=keyboard_json
        )
