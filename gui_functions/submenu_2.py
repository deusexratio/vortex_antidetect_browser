import sys
import os
import tkinter as tk
from tkinter import messagebox
import subprocess

from db import config
from gui_functions.common_dialogs import PasswordThreadsDialog


class SubMenu2(tk.Toplevel):
    def __init__(self, parent, loop):
        super().__init__(parent)
        self.loop = loop
        self.title("Import Extensions Functions")

        # Настройка размеров окна
        window_width = 400
        window_height = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        # Создаем и размещаем текст
        # tk.Label(
        #     self,
        #     text="Importing Wallets Under Construction...",
        #     font=("Arial", 12)
        # ).pack(expand=True)

        # Создаем фрейм для кнопок
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Добавляем кнопки
        buttons = [
            ("Import seed phrases in Rabby Wallet", self.on_import_seed_rabby),
            ("Import private keys in Rabby Wallet", self.on_import_pk_rabby),
            ("Import seed phrases in Phantom Wallet", self.on_import_seed_phantom),
            ("Import private keys in Phantom Wallet", self.on_import_pk_phantom),
            ("Import seed phrases in Backpack Wallet", self.on_import_seed_backpack),
            ("Import private keys in Backpack Wallet", self.on_import_pk_backpack),
            ("Import seed phrases in Metamask Wallet", self.on_import_seed_metamask),
            ("Import private keys in Metamask Wallet", self.on_import_pk_metamask),
        ]

        for text, command in buttons:
            btn = tk.Button(button_frame, text=text, command=command)
            btn.pack(pady=5, fill=tk.X)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()


    def on_import_seed_rabby(self):
        # Показываем диалог для ввода параметров
        dialog = PasswordThreadsDialog(self)
        self.wait_window(dialog)

        # Если пользователь нажал OK и ввел данные
        if dialog.result:
            password, threads = dialog.result

            # Запускаем скрипт с параметрами
            script_path = os.path.join(config.ROOT_DIR, "wallet_functions", "rabby.py")
            subprocess.Popen([
                sys.executable,
                script_path,
                'seed',  # тип импорта
                password,
                str(threads)
            ])

    def on_import_pk_rabby(self):
        # Показываем диалог для ввода параметров
        dialog = PasswordThreadsDialog(self)
        self.wait_window(dialog)

        # Если пользователь нажал OK и ввел данные
        if dialog.result:
            password, threads = dialog.result

            # Запускаем скрипт с параметрами
            script_path = os.path.join(config.ROOT_DIR, "wallet_functions", "rabby.py")
            subprocess.Popen([
                sys.executable,
                script_path,
                'pk',  # тип импорта
                password,
                str(threads)
            ])

    def on_import_seed_metamask(self):
        # Показываем диалог для ввода параметров
        dialog = PasswordThreadsDialog(self)
        self.wait_window(dialog)

        # Если пользователь нажал OK и ввел данные
        if dialog.result:
            password, threads = dialog.result

            # Запускаем скрипт с параметрами
            script_path = os.path.join(config.ROOT_DIR, "wallet_functions", "metamask.py")
            subprocess.Popen([
                sys.executable,
                script_path,
                'seed',  # тип импорта
                password,
                str(threads)
            ])

    def on_import_pk_metamask(self):
        # Показываем диалог для ввода параметров
        dialog = PasswordThreadsDialog(self)
        self.wait_window(dialog)

        # Если пользователь нажал OK и ввел данные
        if dialog.result:
            password, threads = dialog.result

            # Запускаем скрипт с параметрами
            script_path = os.path.join(config.ROOT_DIR, "wallet_functions", "metamask.py")
            subprocess.Popen([
                sys.executable,
                script_path,
                'pk',  # тип импорта
                password,
                str(threads)
            ])

    def on_import_seed_phantom(self):
        # Показываем диалог для ввода параметров
        dialog = PasswordThreadsDialog(self)
        self.wait_window(dialog)

        # Если пользователь нажал OK и ввел данные
        if dialog.result:
            password, threads = dialog.result

            # Запускаем скрипт с параметрами
            script_path = os.path.join(config.ROOT_DIR, "wallet_functions", "phantom.py")
            subprocess.Popen([
                sys.executable,
                script_path,
                'seed',  # тип импорта
                password,
                str(threads)
            ])

    def on_import_pk_phantom(self):
        # Показываем диалог для ввода параметров
        dialog = PasswordThreadsDialog(self)
        self.wait_window(dialog)

        # Если пользователь нажал OK и ввел данные
        if dialog.result:
            password, threads = dialog.result

            # Запускаем скрипт с параметрами
            script_path = os.path.join(config.ROOT_DIR, "wallet_functions", "phantom.py")
            subprocess.Popen([
                sys.executable,
                script_path,
                'pk',  # тип импорта
                password,
                str(threads)
            ])

    def on_import_seed_backpack(self):
        # Показываем диалог для ввода параметров
        dialog = PasswordThreadsDialog(self)
        self.wait_window(dialog)

        # Если пользователь нажал OK и ввел данные
        if dialog.result:
            password, threads = dialog.result

            # Запускаем скрипт с параметрами
            script_path = os.path.join(config.ROOT_DIR, "wallet_functions", "backpack.py")
            subprocess.Popen([
                sys.executable,
                script_path,
                'seed',  # тип импорта
                password,
                str(threads)
            ])

    def on_import_pk_backpack(self):
        # Показываем диалог для ввода параметров
        dialog = PasswordThreadsDialog(self)
        self.wait_window(dialog)

        # Если пользователь нажал OK и ввел данные
        if dialog.result:
            password, threads = dialog.result

            # Запускаем скрипт с параметрами
            script_path = os.path.join(config.ROOT_DIR, "wallet_functions", "backpack.py")
            subprocess.Popen([
                sys.executable,
                script_path,
                'pk',  # тип импорта
                password,
                str(threads)
            ])
