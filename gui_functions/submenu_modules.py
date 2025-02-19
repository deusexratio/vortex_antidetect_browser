import sys
import os
import tkinter as tk
import subprocess
from tkinter import messagebox

from loguru import logger

from db import config
from db.db_api import load_profiles
from gui_functions.common_dialogs import PasswordThreadsDialog


class SubMenuModules(tk.Toplevel):
    def __init__(self, parent, loop):
        super().__init__(parent)
        self.loop = loop
        self.title("Modules")

        self.pizza_subprocess = None
        self.turbo_subprocess = None
        self.fantasy_subprocess = None

        # Настройка размеров окна
        window_width = 400
        window_height = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        # Создаем и размещаем текст
        tk.Label(
            self,
            text="Turbo Tap under construction...",
            font=("Arial", 12)
        ).pack(expand=True)

        # Создаем фрейм для кнопок
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Добавляем кнопки
        buttons = [
            ("Turbo Tap", self.on_turbo_tap),
            ("Abstract Pizza", self.on_abstract_pizza),
            ("Fantasy Monad", self.on_fantasy_monad),
        ]

        for text, command in buttons:
            btn = tk.Button(button_frame, text=text, command=command)
            btn.pack(pady=5, fill=tk.X)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()

        stop_frame = tk.Frame(self)
        stop_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        stop_buttons = [
            ("Stop Turbo Tap", self.stop_turbo_tap),
            ("Stop Abstract Pizza", self.stop_abstract_pizza),
            ("Stop Fantasy Monad", self.stop_fantasy_monad),
        ]

        for text, command in stop_buttons:
            btn = tk.Button(stop_frame, text=text, command=command)
            btn.pack(pady=5, fill=tk.X)

    def on_abstract_pizza(self):
        """Запускает abstract_pizza.py с выбранными профилями"""
        dialog = ModuleProfilesDialog(self, module='Pizza')
        self.wait_window(dialog)

        if dialog.result:
            print(dialog.result)
            # profile_names, password, threads = dialog.result
            profile_names, pizza_range, threads = dialog.result
            profiles_names = ",".join(profile_names)
            # Запускаем скрипт со списком профилей
            script_path = os.path.join(config.ROOT_DIR, "modules", "abstract_pizza.py")
            if self.pizza_subprocess is None:
                self.pizza_subprocess = subprocess.Popen([sys.executable, script_path,
                                                          # profiles_names, password, str(threads), 'Abstract'])
                                                          profiles_names, pizza_range, str(threads), 'Abstract'])

    def stop_abstract_pizza(self):
        """Останавливает субпроцесс"""
        if self.pizza_subprocess is not None and self.pizza_subprocess.poll() is None:
            self.pizza_subprocess.terminate()  # Или self.process.kill() для принудительной остановки
            self.pizza_subprocess.wait()  # Ждем завершения процесса
            logger.debug("Pizza stopped")

    def on_turbo_tap(self):
        """Запускает turbo_tap.py с выбранными профилями"""
        dialog = ModuleProfilesDialog(self, module='Turbo')
        self.wait_window(dialog)

        if dialog.result:
            profile_names, taps_range, password, threads = dialog.result
            profiles_names = ",".join(profile_names)
            # Запускаем скрипт со списком профилей
            script_path = os.path.join(config.ROOT_DIR, "modules", "turbo_tap.py")
            if self.turbo_subprocess is None:
                self.turbo_subprocess = subprocess.Popen([sys.executable, script_path,
                                                          profiles_names, taps_range, password, str(threads)])

    def stop_turbo_tap(self):
        """Останавливает субпроцесс"""
        if self.turbo_subprocess is not None and self.turbo_subprocess.poll() is None:
            self.turbo_subprocess.terminate()  # Или self.process.kill() для принудительной остановки
            self.turbo_subprocess.wait()  # Ждем завершения процесса
            logger.debug("Turbo Tap stopped")

    def on_fantasy_monad(self):
        """Запускает turbo_tap.py с выбранными профилями"""
        dialog = ModuleProfilesDialog(self, module='Fantasy')
        self.wait_window(dialog)

        if dialog.result:
            profile_names, ref_codes, how_many_accounts, threads = dialog.result
            profiles_names = ",".join(profile_names)
            # Запускаем скрипт со списком профилей
            script_path = os.path.join(config.ROOT_DIR, "modules", "fantasy_monad.py")
            if self.fantasy_subprocess is None:
                self.fantasy_subprocess = subprocess.Popen([sys.executable, script_path,
                                                          profiles_names, ref_codes, how_many_accounts, str(threads)])

    def stop_fantasy_monad(self):
        """Останавливает субпроцесс"""
        if self.fantasy_subprocess is not None and self.fantasy_subprocess.poll() is None:
            self.fantasy_subprocess.terminate()  # Или self.process.kill() для принудительной остановки
            self.fantasy_subprocess.wait()  # Ждем завершения процесса
            logger.debug("Fantasy Monad stopped")


class ModuleProfilesDialog(tk.Toplevel):
    def __init__(self, parent, module: str):
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
        if module == 'Pizza':
            tk.Button(frame, text="Start Module", command=self.on_start_pizza).pack(side=tk.BOTTOM, padx=5)
        if module == 'Turbo':
            tk.Button(frame, text="Start Module", command=self.on_start_turbo).pack(side=tk.BOTTOM, padx=5)
        if module == 'Fantasy':
            tk.Button(frame, text="Start Module", command=self.on_start_fantasy).pack(side=tk.BOTTOM, padx=5)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()


    def on_start(self):
        profiles_selection = self.profiles_list.curselection()

        if not profiles_selection:
            messagebox.showerror("Error", "Please select profiles")
            return

        profile_names = [self.profiles_list.get(i) for i in profiles_selection]

        password_threads_dialog = PasswordThreadsDialog(self)
        self.wait_window(password_threads_dialog)

        # Если пользователь нажал OK и ввел данные
        if password_threads_dialog.result:
            password, threads = password_threads_dialog.result

            self.result = profile_names, password, threads
            self.destroy()

    def on_start_pizza(self):
        profiles_selection = self.profiles_list.curselection()
        if not profiles_selection:
            messagebox.showerror("Error", "Please select profiles")
            return

        profile_names = [self.profiles_list.get(i) for i in profiles_selection]

        pizza_range_dialog = PizzaDialog(self)
        self.wait_window(pizza_range_dialog)

        if pizza_range_dialog.result:
            pizza_range, threads = pizza_range_dialog.result

            self.result = profile_names, pizza_range, threads
            self.destroy()

    def on_start_turbo(self):
        profiles_selection = self.profiles_list.curselection()
        if not profiles_selection:
            messagebox.showerror("Error", "Please select profiles")
            return

        profile_names = [self.profiles_list.get(i) for i in profiles_selection]

        taps_range_dialog = TurboDialog(self)
        self.wait_window(taps_range_dialog)

        if taps_range_dialog.result:
            taps_range, password, threads = taps_range_dialog.result

            self.result = profile_names, taps_range, password, threads
            self.destroy()

    def on_start_fantasy(self):
        profiles_selection = self.profiles_list.curselection()
        if not profiles_selection:
            messagebox.showerror("Error", "Please select profiles")
            return

        profile_names = [self.profiles_list.get(i) for i in profiles_selection]

        fantasy_settings_dialog = FantasyDialog(self)
        self.wait_window(fantasy_settings_dialog)

        if fantasy_settings_dialog.result:
            ref_codes, how_many_accounts, threads = fantasy_settings_dialog.result

            self.result = profile_names, ref_codes, how_many_accounts, threads
            self.destroy()


class PizzaDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None

        self.title("Enter how many pizzas you want to cook on each profile:")

        # Настройка размеров окна
        window_width = 400
        window_height = 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        tk.Label(
            self,
            text="Enter range to random like '30-50'",
            font=("Arial", 12)
        ).pack(expand=True)

        # Создаем и размещаем элементы
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Поле для количества потоков
        tk.Label(frame, text="Pizzas:").grid(row=0, column=0, sticky='w', pady=5)
        self.pizza_entry = tk.Entry(frame)
        self.pizza_entry.grid(row=0, column=1, sticky='ew', pady=5)
        self.pizza_entry.insert(0, "30-50")  # Значение по умолчанию

        # Поле для количества потоков
        tk.Label(frame, text="Threads:").grid(row=1, column=0, sticky='w', pady=5)
        self.threads_entry = tk.Entry(frame)
        self.threads_entry.grid(row=1, column=1, sticky='ew', pady=5)
        self.threads_entry.insert(0, "3")  # Значение по умолчанию

        # Кнопки
        button_frame = tk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        tk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

        # Настройка grid
        frame.columnconfigure(1, weight=1)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()

        # Фокус на поле пароля
        self.pizza_entry.focus_set()

        # Привязываем Enter к OK
        self.bind('<Return>', lambda e: self.on_ok())

    def on_ok(self):
        try:
            pizzas_range = self.pizza_entry.get()
            if len(pizzas_range.split('-')) != 2:
                raise ValueError("Incorrect input")
            threads = int(self.threads_entry.get())
            if threads <= 0:
                raise ValueError("Threads must be positive")

            self.result = (pizzas_range, threads)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))



class TurboDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None

        self.title("Enter how many taps you want to do on each profile:")

        # Настройка размеров окна
        window_width = 400
        window_height = 300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        tk.Label(
            self,
            text="Enter range to random like '10000-50000'",
            font=("Arial", 12)
        ).pack(expand=True)

        # Создаем и размещаем элементы
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Поле для количества taps
        tk.Label(frame, text="Taps:").grid(row=0, column=0, sticky='w', pady=5)
        self.taps_entry = tk.Entry(frame)
        self.taps_entry.grid(row=0, column=1, sticky='ew', pady=5)
        self.taps_entry.insert(0, "10000-50000")  # Значение по умолчанию

        # Поле для количества потоков
        tk.Label(frame, text="Password:").grid(row=1, column=0, sticky='w', pady=5)
        self.password_entry = tk.Entry(frame)
        self.password_entry.grid(row=1, column=1, sticky='ew', pady=5)
        self.password_entry.insert(0, "12345678")  # Значение по умолчанию

        # Поле для количества потоков
        tk.Label(frame, text="Threads:").grid(row=2, column=0, sticky='w', pady=5)
        self.threads_entry = tk.Entry(frame)
        self.threads_entry.grid(row=2, column=1, sticky='ew', pady=5)
        self.threads_entry.insert(0, "3")  # Значение по умолчанию

        # Кнопки
        button_frame = tk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        tk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

        # Настройка grid
        frame.columnconfigure(1, weight=1)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()

        # Фокус на поле пароля
        self.taps_entry.focus_set()

        # Привязываем Enter к OK
        self.bind('<Return>', lambda e: self.on_ok())

    def on_ok(self):
        try:
            taps_range = self.taps_entry.get()
            if len(taps_range.split('-')) != 2:
                raise ValueError("Incorrect input")

            password = self.password_entry.get()
            if not password:
                raise ValueError("Password cannot be empty")

            threads = int(self.threads_entry.get())
            if threads <= 0:
                raise ValueError("Threads must be positive")

            self.result = (taps_range, password, threads)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))


class FantasyDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None

        self.title("Enter launch settings:")

        # Настройка размеров окна
        window_width = 600
        window_height = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        tk.Label(
            self,
            text="Enter referral codes like 'ref1,ref2,ref3,...'\n "
                 "OR leave blank",
            font=("Arial", 12)
        ).pack(expand=True)

        # Создаем и размещаем элементы
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Поле для количества taps
        tk.Label(frame, text="Referral codes:").grid(row=0, column=0, sticky='w', pady=5)
        self.refs_entry = tk.Entry(frame)
        self.refs_entry.grid(row=0, column=1, sticky='ew', pady=5)
        self.refs_entry.insert(0, "ref1,ref2,ref3,...")  # Значение по умолчанию

        tk.Label(
            self,
            text="You can leave blank how many accounts to register on each ref code if no ref codes",
            font=("Arial", 12)
        ).pack(expand=True)

        # Поле для количества потоков
        tk.Label(frame, text="Enter how many accounts to register on each ref code:").grid(row=1, column=0, sticky='w', pady=5)
        self.accounts_entry = tk.Entry(frame)
        self.accounts_entry.grid(row=1, column=1, sticky='ew', pady=5)
        self.accounts_entry.insert(0, "5")  # Значение по умолчанию

        # Поле для количества потоков
        tk.Label(frame, text="Threads:").grid(row=2, column=0, sticky='w', pady=5)
        self.threads_entry = tk.Entry(frame)
        self.threads_entry.grid(row=2, column=1, sticky='ew', pady=5)
        self.threads_entry.insert(0, "3")  # Значение по умолчанию

        # Кнопки
        button_frame = tk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        tk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

        # Настройка grid
        frame.columnconfigure(1, weight=1)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()

        # Фокус на поле пароля
        self.refs_entry.focus_set()

        # Привязываем Enter к OK
        self.bind('<Return>', lambda e: self.on_ok())

    def on_ok(self):
        try:
            ref_codes = self.refs_entry.get()
            # if len(ref_codes.split('-')) != 2:
            #     raise ValueError("Incorrect input")

            how_many_accounts = self.accounts_entry.get()

            if ref_codes and not how_many_accounts:
                raise ValueError("If you fill ref codes you need to fill how many accounts")

            threads = int(self.threads_entry.get())
            if threads <= 0:
                raise ValueError("Threads must be positive")

            self.result = (ref_codes, how_many_accounts, threads)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
