import requests
from bs4 import BeautifulSoup

def get_project_titles():
    url = 'https://education.vk.company/projects'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    titles = []
    for block in soup.select('.project-card__title'):
        titles.append(block.text.strip())

    return titles

def is_project_related(text):
    projects = get_project_titles()
    for title in projects:
        if title.lower() in text.lower():
            return True
    return False

