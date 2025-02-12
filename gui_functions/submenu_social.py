import sys
import os
import tkinter as tk
import subprocess
from tkinter import messagebox

from loguru import logger

from db import config
from db.db_api import load_profiles


class SubMenuSocial(tk.Toplevel):
    def __init__(self, parent, loop):
        super().__init__(parent)
        self.loop = loop
        self.title("Social")

        # Настройка размеров окна
        window_width = 400
        window_height = 300
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
            ("Import X tokens from 'Profiles' sheet", self.on_import_x_cookies),
            ("Import Discord tokens from 'Profiles' sheet", self.on_import_discord_cookies),
            ("Launch mutual following on X", self.on_mutual_following),
        ]

        for text, command in buttons:
            btn = tk.Button(button_frame, text=text, command=command)
            btn.pack(pady=5, fill=tk.X)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()

    def on_mutual_following(self):
        """Запускает взаимную подписку"""
        dialog = MutualFollowingProfilesDialog(self)
        self.wait_window(dialog)

        if dialog.result:
            profiles_names_list = dialog.result
            profiles_names = ",".join(profiles_names_list)
            # Запускаем скрипт со списком профилей
            script_path = os.path.join(config.ROOT_DIR, "social_functions", "mutual_following.py")

            subprocess.Popen([sys.executable, script_path, profiles_names])


    @staticmethod
    def on_import_x_cookies():
        # Запускаем установку в отдельном процессе
        logger.debug(f"Starting importing X tokens, please wait...")
        script_path = os.path.join(config.ROOT_DIR, "social_functions", "import_x_discord_token.py")
        subprocess.Popen([sys.executable, script_path, 'X'])

    @staticmethod
    def on_import_discord_cookies():
        # Запускаем установку в отдельном процессе
        logger.debug(f"Starting importing Discord tokens, please wait...")
        script_path = os.path.join(config.ROOT_DIR, "social_functions", "import_x_discord_token.py")
        subprocess.Popen([sys.executable, script_path, 'Discord'])


class MutualFollowingProfilesDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        self.parent = parent

        self.title("Select Profiles for Mutual Following")

        # Настройка размеров окна
        window_width = 400
        window_height = 550
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        # Настройка окна
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Список профилей

        tk.Label(frame, text="Select profiles:").pack()
        self.profiles_list = tk.Listbox(frame, height=25, selectmode=tk.MULTIPLE, exportselection=0)
        self.profiles_list.pack(fill=tk.X, pady=5)

        # Загружаем профили
        for profile in load_profiles():
            self.profiles_list.insert(tk.END, profile.name)

        # Кнопки
        tk.Button(frame, text="Cancel", command=self.destroy).pack(side=tk.BOTTOM, padx=5)
        tk.Button(frame, text="Start Mutual Following", command=self.on_start).pack(side=tk.BOTTOM, padx=5)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()

        # Добавляем обработчики выбора
        # self.main_profile_list.bind('<<ListboxSelect>>', self.on_main_profile_select)

    # def on_main_profile_select(self, event):
    #     """Обработчик выбора главного профиля"""
    #     selection = self.main_profile_list.curselection()
    #     if selection:
    #         main_profile = self.main_profile_list.get(selection[0])
    #         # Делаем главный профиль недоступным для выбора в списке последователей
    #         for i in range(self.follower_profiles_list.size()):
    #             if self.follower_profiles_list.get(i) == main_profile:
    #                 self.follower_profiles_list.selection_clear(i)
    #                 self.follower_profiles_list.itemconfig(i, {'bg': '#f0f0f0'})
    #             else:
    #                 self.follower_profiles_list.itemconfig(i, {'bg': 'white'})

    def on_start(self):
        # main_sel = self.main_profile_list.curselection()
        profiles_selection = self.profiles_list.curselection()

        # if not main_sel:
        #     messagebox.showerror("Error", "Please select main profile")
        #     return

        if not profiles_selection:
            messagebox.showerror("Error", "Please select profiles")
            return

        # main_name = self.main_profile_list.get(main_sel[0])
        follower_names = [self.profiles_list.get(i) for i in profiles_selection]

        self.result = follower_names
        self.destroy()


class ProfileListDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None

        self.title("Enter Profile Names")

        # Настройка размеров окна
        window_width = 400
        window_height = 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        # Создаем и размещаем элементы
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Метка с инструкцией
        tk.Label(
            frame,
            text="Enter profile names separated by commas:",
            font=("Arial", 10)
        ).pack(pady=(0, 10))

        # Текстовое поле для ввода
        self.text_entry = tk.Text(frame, height=5)
        self.text_entry.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Кнопки
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=(0, 10))

        tk.Button(
            button_frame,
            text="OK",
            command=self.on_ok,
            width=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Cancel",
            command=self.on_cancel,
            width=10
        ).pack(side=tk.LEFT, padx=5)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()

        # Фокус на поле ввода
        self.text_entry.focus_set()

    def on_ok(self):
        """Обработчик нажатия OK"""
        text = self.text_entry.get("1.0", tk.END).strip()
        if text:
            # Разбиваем текст на имена профилей и очищаем их
            profile_names = [name.strip() for name in text.split(",") if name.strip()]
            if profile_names:
                self.result = profile_names
                self.destroy()
            else:
                messagebox.showerror("Error", "Please enter at least one profile name")
        else:
            messagebox.showerror("Error", "Please enter profile names")

    def on_cancel(self):
        """Обработчик нажатия Cancel"""
        self.destroy()

