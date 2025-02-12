import sys
import os
import tkinter as tk
import subprocess
from tkinter import messagebox

from db import config


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

    def on_turbo_tap(self):
        """Запускает turbo_tap.py с выбранными профилями"""
        dialog = ProfileListDialog(self)
        self.wait_window(dialog)

        if dialog.result:
            # Запускаем скрипт с списком профилей
            script_path = os.path.join(config.ROOT_DIR, "wallet_functions", "turbo_tap.py")
            profile_list = ",".join(dialog.result)  # Объединяем имена через запятую

            subprocess.Popen([
                sys.executable,
                script_path,
                profile_list
            ])


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

