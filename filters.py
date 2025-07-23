import re

BAD_WORDS = ["блин", "черт", "мат1", "мат2"]  # Добавь нужные слова

def contains_profanity(text):
    text = text.lower()
    for word in BAD_WORDS:
        if re.search(rf'\b{word}\b', text):
            return True
    return False
