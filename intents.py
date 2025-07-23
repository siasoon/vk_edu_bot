FAQ = {
    "как выбрать проект": "Выбрать проект можно на https://education.vk.company/projects",
    "где найти информацию о вебинарах": "Они находятся в разделе 'События' на сайте.",
    "какой файл загружать": "Смотрите требования к проекту — чаще всего PDF или архив.",
}

CLOSED_QUESTIONS = {
    "возможно ли взять несколько проектов": "Да.",
    "нужно ли оформлять отчет": "Да, отчёт обязателен."
}

def get_answer(text):
    text = text.lower()
    for question, answer in FAQ.items():
        if question in text:
            return answer
    for question, answer in CLOSED_QUESTIONS.items():
        if question in text:
            return answer
    return None
