import os
import sys

# Определяем корневую директорию проекта
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Добавляем корневую директорию в sys.path
sys.path.append(ROOT_DIR)

class Version:
    def __init__(self, version: str):
        elems = version.split('.')
        self.major = int(elems[0])
        self.middle = int(elems[1])
        self.minor = int(elems[2])
        self.version_str = version

    def __int__(self):
        return self.major * 100 + self.middle * 10 + self.minor

    def __str__(self):
        return self.version_str

import requests

from updater.update_consts import GITHUB_REPO, CURRENT_VERSION


def check_for_updates():
    """Проверяет наличие обновлений на GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        latest_release = response.json()
        latest_version = Version(latest_release['tag_name'])
        if int(latest_version) > int(CURRENT_VERSION):
            return latest_release
    return None
