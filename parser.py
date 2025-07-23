# parser.py

import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://education.vk.company"

def parse_course_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("h1", class_="styles_title__xYyKv")
    title = title_tag.get_text(strip=True) if title_tag else "Без названия"

    desc_tag = soup.find("div", class_="styles_description__ZCEUN")
    topics = desc_tag.get_text(strip=True) if desc_tag else "Нет описания"

    labels = soup.find_all("p", class_="styles_label__nfnzU")
    info = {"format": "Не указан", "duration": "Не указана", "audience": "Не указана"}

    for label in labels:
        text = label.get_text(strip=True)
        next_el = label.find_next_sibling("p")
        if not next_el:
            continue

        if "Формат" in text:
            info["format"] = next_el.get_text(strip=True)
        elif "Длительность" in text:
            info["duration"] = next_el.get_text(strip=True)
        elif "Для кого" in text:
            info["audience"] = next_el.get_text(strip=True)

    return {
        "title": title,
        "format": info["format"],
        "duration": info["duration"],
        "audience": info["audience"],
        "topics": topics,
        "url": url
    }


def parse_vk_education_courses():
    url = f"{BASE_URL}/students#courses"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    courses = []

    h3_tags = soup.find_all("h3")

    for h3 in h3_tags:
        title = h3.get_text(strip=True)
        parent = h3.find_parent()
        a_tag = parent.find("a", href=True) if parent else None

        if a_tag:
            link = a_tag['href']
            full_url = link if link.startswith("http") else BASE_URL + link

            try:
                details = parse_course_page(full_url)
                details["title"] = title
                details["url"] = full_url
                courses.append(details)
            except Exception as e:
                print(f"Ошибка при парсинге {full_url}: {e}")

            time.sleep(0.5)

    return courses
