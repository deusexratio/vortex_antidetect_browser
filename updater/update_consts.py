import os
import sys

# Определяем корневую директорию проекта
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Добавляем корневую директорию в sys.path
sys.path.append(ROOT_DIR)

from updater.update_utils import Version

GITHUB_REPO = "deusexratio/vortex_antidetect_browser"
CURRENT_VERSION = Version("1.0.5")
