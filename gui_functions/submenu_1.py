import sys
import os
import tkinter as tk
import traceback
from tkinter import messagebox

from loguru import logger
import subprocess

from db import config
from db.db_api import load_profiles, flush_wallets, get_all_extensions_from_db
from file_functions.Import import import_profiles, import_wallets
from file_functions.utils import get_file_names

class SubMenu1(tk.Toplevel):
    def __init__(self, parent, loop):
        super().__init__(parent)
        self.loop = loop
        self.title("Import Functions")

        # Настройка размеров окна
        window_width = 400
        window_height = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        # Создаем фрейм для кнопок
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Добавляем кнопки
        buttons = [
            ("Import profiles to database from profiles.xlsx", import_profiles),
            ("Export selected cookies from AdsBrowser profiles", self.on_export_cookies),
            ("Import cookies from JSONs in user_files/cookies", self.on_import_cookies),
            ("Import wallets to database for profiles from profiles.xlsx", import_wallets),
            ("Flush all seed phrases and private keys from database", self.on_flush_wallets),
            ("Fetch all extension ids to database", self.on_fetch_extension_ids),
            ("Clear selected extensions cache", self.on_clear_cache_for_extension),
            ("Import X tokens from 'Profiles' sheet", self.on_import_x_cookies),
            ("Import Discord tokens from 'Profiles' sheet", self.on_import_discord_cookies),
        ]

        for text, command in buttons:
            btn = tk.Button(button_frame, text=text, command=command)
            btn.pack(pady=5, fill=tk.X)

    @staticmethod
    def on_flush_wallets():
        try:
            logger.debug('Starting deleting all rows in "wallets" table in database')
            flush_wallets()
            logger.success('Successfully deleted all wallets')
        except Exception as e:
            traceback.print_exc()
            logger.error(e)

    @staticmethod
    def on_export_cookies():
        # import subprocess

        script_path = os.path.join(config.ROOT_DIR, "file_functions", "selected_cookies_from_ads.py")
        subprocess.Popen([sys.executable, script_path])

    @staticmethod
    def on_import_cookies():
        # Запускаем установку в отдельном процессе

        script_path = os.path.join(config.ROOT_DIR, "file_functions", "import_cookies.py")
        subprocess.Popen([sys.executable, script_path])

    @staticmethod
    def on_import_x_cookies():
        # Запускаем установку в отдельном процессе

        script_path = os.path.join(config.ROOT_DIR, "file_functions", "import_x_discord_token.py")
        subprocess.Popen([sys.executable, script_path, 'X'])

    @staticmethod
    def on_import_discord_cookies():
        # Запускаем установку в отдельном процессе

        script_path = os.path.join(config.ROOT_DIR, "file_functions", "import_x_discord_token.py")
        subprocess.Popen([sys.executable, script_path, 'Discord'])

    def on_profile_settings(self):
        logger.debug("Открыты настройки профилей")
        # Здесь будет логика настроек профилей

    def on_proxy_management(self):
        logger.debug("Открыто управление прокси")
        # Здесь будет логика управления прокси

    def on_browser_settings(self):
        logger.debug("Открыты настройки браузера")
        # Здесь будет логика настроек браузера

    def on_import_export(self):
        logger.debug("Открыто окно импорта/экспорта")
        # Здесь будет логика импорта/экспорта

    @staticmethod
    def on_fetch_extension_ids():
        extension_paths = get_file_names(config.EXTENSIONS_DIR, files=False)
        if extension_paths:
            # Запускаем установку в отдельном процессе

            script_path = os.path.join(config.ROOT_DIR, "file_functions", "get_ext_ids.py")
            subprocess.Popen([sys.executable, script_path])
        else:
            messagebox.showwarning("Warning", "No extension folders in user_files/extensions!")

    def on_clear_cache_for_extension(self):
        """Открывает диалог выбора расширений для очистки кэша"""
        dialog = ExtensionSelectionDialog(self)


class ExtensionSelectionDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_extensions = []

        self.title("Select Extensions")

        # Настройка размеров окна
        window_width = 400
        window_height = 300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        # Создаем основной фрейм
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        tk.Label(
            main_frame,
            text="Select extensions to clear cache:",
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 10))

        # Фрейм для списка с прокруткой
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Добавляем скроллбар
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Создаем список расширений
        self.extension_list = tk.Listbox(
            list_frame,
            selectmode=tk.MULTIPLE,
            font=("Arial", 10),
            activestyle='none',
            selectbackground='#0078D7',
            selectforeground='white'
        )
        self.extension_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Привязываем скроллбар к списку
        scrollbar.config(command=self.extension_list.yview)
        self.extension_list.config(yscrollcommand=scrollbar.set)

        # Загружаем список расширений
        self.load_extensions()

        # Кнопки
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=(20, 0))

        tk.Button(
            button_frame,
            text="Clear Selected",
            command=self.on_clear_selected
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Clear All",
            command=self.on_clear_all
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side=tk.LEFT, padx=5)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()

        # Ждем, пока окно не будет закрыто
        parent.wait_window(self)

    def load_extensions(self):
        """Загружает список расширений из БД"""
        extensions = get_all_extensions_from_db()
        for ext in extensions:
            self.extension_list.insert(tk.END, f"{ext.name} ({ext.extension_id})")

    def get_selected_extension_ids(self):
        """Возвращает ID выбранных расширений"""
        selected_indices = self.extension_list.curselection()
        extensions = get_all_extensions_from_db()
        selected_extensions = []

        for idx in selected_indices:
            selected_extensions.append(extensions[idx].extension_id)

        return selected_extensions

    def clear_cache_for_extensions(self, extension_ids):
        """Очищает кэш для выбранных расширений"""
        profiles = load_profiles()
        cleared_count = 0

        for profile in profiles:
            for ext_id in extension_ids:
                cache_path = os.path.join(
                    config.USER_DATA_DIR,
                    profile.name,
                    "Default",
                    "Local Extension Settings",
                    ext_id
                )
                try:
                    if os.path.exists(cache_path):
                        import shutil
                        shutil.rmtree(cache_path)
                        cleared_count += 1
                except Exception as e:
                    logger.error(f"Error clearing cache for {ext_id} in {profile.name}: {e}")

        return cleared_count

    def on_clear_selected(self):
        """Обработчик нажатия кнопки Clear Selected"""
        selected_ids = self.get_selected_extension_ids()
        if not selected_ids:
            messagebox.showwarning("Warning", "Please select at least one extension")
            return

        cleared = self.clear_cache_for_extensions(selected_ids)
        messagebox.showinfo("Success", f"Cleared cache in {cleared} locations")
        self.destroy()

    def on_clear_all(self):
        """Обработчик нажатия кнопки Clear All"""
        extensions = get_all_extensions_from_db()
        extension_ids = [ext.extension_id for ext in extensions]
        cleared = self.clear_cache_for_extensions(extension_ids)
        messagebox.showinfo("Success", f"Cleared cache in {cleared} locations")
        self.destroy()