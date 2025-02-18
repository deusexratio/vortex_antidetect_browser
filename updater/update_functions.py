import sys

import requests
import zipfile
import os
import shutil
from tkinter import messagebox

from loguru import logger

# Определяем корневую директорию проекта
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Добавляем корневую директорию в sys.path
sys.path.append(ROOT_DIR)

from updater.update_utils import check_for_updates


def download_and_install_update(release):
    """Скачивает и устанавливает обновление"""
    assets = release.get('assets', [])
    print(release)
    for asset in assets:
        print(asset)
        if asset['name'].endswith('.zip'):
            print(asset['name'])
            download_url = asset['browser_download_url']
            print(download_url)
            response = requests.get(download_url, stream=True)
            if response.status_code == 200:
                with open('update.zip', 'wb') as f:
                    for chunk in response.iter_content(chunk_size=128):
                        f.write(chunk)
                install_update('update.zip')
                return True
    return False

def download_and_install_updates_from_zipball(release):
    try:
        zipball_url = release.get('zipball_url')
        response = requests.get(zipball_url, stream=True)
        if response.status_code == 200:
            logger.success(f'Downloaded zip from {zipball_url}')
            with open('update.zip', 'wb') as f:
                for chunk in response.iter_content(chunk_size=128):
                    f.write(chunk)
                logger.success(f'Wrote zip to update.zip')
            install_update('update.zip')
            return True
    except Exception as e:
        messagebox.showerror("Update", f"Failed to download the update. {e}")
        return False

def install_update(zip_path):
    """Устанавливает обновление из zip архива"""
    # Извлекаем архив
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall('update')
    logger.success(f'Extracted zip')

    # Получаем имя папки, которая была создана
    extracted_folder = os.path.join('update', os.listdir('update')[0])  # Предполагаем, что в архиве только одна папка

    # Копируем файлы из папки в целевую директорию
    for item in os.listdir(extracted_folder):
        s = os.path.join(extracted_folder, item)
        d = os.path.join('.', item)  # Замените '.' на нужную целевую директорию
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
            logger.success(f'Copied directory {d} from {extracted_folder}')
        else:
            shutil.copy2(s, d)
            logger.success(f'Copied file {d} from {extracted_folder}')

    # Удаляем временные файлы
    shutil.rmtree('update')
    logger.success('Deleted update folder')
    os.remove(zip_path)
    logger.success(f'Deleted {zip_path}')

    # Завершаем программу
    messagebox.showinfo("Update", "Update installed successfully. The application will now close.")


def main():
    release = check_for_updates()
    download_and_install_updates_from_zipball(release)
    sys.exit(0)


if __name__ == "__main__":
    main()
