import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from intents import get_answer
from filters import contains_profanity
from unknown_handler import handle_unknown
from parser import is_project_related

GROUP_ID = '231743337'
TOKEN = 'vk1.a.rM7jjKpwccx0heaZpDKq5kWOXC3lni6tpOS0NkxJWmPpTwf0RHGOSR9KKfRslDm6V6lHZNobhQj48Fp1Sk_5X2g_htKfHdlrDyfC0ILghiNwYDqd9ry7veRIaMjGnh33mELsyEa1NuiOLVsOQ_0b5ZdObxP1CRUGREfaUY-UWLP3jsaWOlLEiEsXlAg697vR2FanTJXzVdxepcI1vHYWBQ'

vk_session = vk_api.VkApi(token=TOKEN)
longpoll = VkBotLongPoll(vk_session, GROUP_ID)
vk = vk_session.get_api()

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        text = event.message.text.strip()
        user_id = event.message.from_id

        # Проверка на мат
        if contains_profanity(text):
            vk.messages.send(
                user_id=user_id,
                message="Пожалуйста, без нецензурной лексики 🙏",
                random_id=0
            )
            continue

        # FAQ и ответы
        answer = get_answer(text)
        if answer:
            vk.messages.send(user_id=user_id, message=answer, random_id=0)
            continue

        # Проверка на наличие названия проекта
        if is_project_related(text):
            vk.messages.send(user_id=user_id, message="Это один из проектов VK Education!", random_id=0)
            continue

        # Неизвестный вопрос
        unknown = handle_unknown(text)
        vk.messages.send(user_id=user_id, message=unknown, random_id=0)
