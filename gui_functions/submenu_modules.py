import sys
import os
import tkinter as tk
import subprocess
from tkinter import messagebox

from db import config
from db.db_api import load_profiles
from gui_functions.common_dialogs import PasswordThreadsDialog


class SubMenuModules(tk.Toplevel):
    def __init__(self, parent, loop):
        super().__init__(parent)
        self.loop = loop
        self.title("Modules")

        # Настройка размеров окна
        window_width = 400
        window_height = 200
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
            ("Turbo Tap", self.on_turbo_tap),
            ("Abstract Pizza", self.on_abstract_pizza),
        ]

        for text, command in buttons:
            btn = tk.Button(button_frame, text=text, command=command)
            btn.pack(pady=5, fill=tk.X)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()

        # Создаем и размещаем текст
        tk.Label(
            self,
            text="Turbo Tap under construction...",
            font=("Arial", 12)
        ).pack(expand=True)

    def on_abstract_pizza(self):
        """Запускает abstract_pizza.py с выбранными профилями"""
        dialog = ModuleProfilesDialog(self)
        self.wait_window(dialog)

        if dialog.result:
            profile_names, password, threads = dialog.result
            profiles_names = ",".join(profile_names)
            # Запускаем скрипт со списком профилей
            script_path = os.path.join(config.ROOT_DIR, "modules", "abstract_pizza.py")

            subprocess.Popen([sys.executable, script_path, profiles_names, password, str(threads), 'Abstract'])

    def on_turbo_tap(self):
        """Запускает turbo_tap.py с выбранными профилями"""
        dialog = ModuleProfilesDialog(self)
        self.wait_window(dialog)

        if dialog.result:
            profile_names, password, threads = dialog.result
            profiles_names = ",".join(profile_names)
            # Запускаем скрипт со списком профилей
            script_path = os.path.join(config.ROOT_DIR, "modules", "turbo_tap.py")

            subprocess.Popen([sys.executable, script_path, profiles_names, password, str(threads)])


class ModuleProfilesDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        self.parent = parent

        self.title("Select Profiles for Module:")

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
        tk.Button(frame, text="Start Module", command=self.on_start).pack(side=tk.BOTTOM, padx=5)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()


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
        profile_names = [self.profiles_list.get(i) for i in profiles_selection]

        password_threads_dialog = PasswordThreadsDialog(self)
        self.wait_window(password_threads_dialog)

        # Если пользователь нажал OK и ввел данные
        if password_threads_dialog.result:
            password, threads = password_threads_dialog.result

            self.result = profile_names, password, threads
            self.destroy()
