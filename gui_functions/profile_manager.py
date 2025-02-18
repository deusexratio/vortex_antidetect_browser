import asyncio
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog

from better_proxy import Proxy
from loguru import logger
from typing import Dict, Any

from playwright.async_api import async_playwright

from browser_functions.functions import close_profile, launch_profile_async # launch_synced_profiles
from db import config
from db.db_api import load_profiles, get_profile
from db.models import db, Profile
from file_functions.utils import get_file_names
from gui_functions.submenu_1 import SubMenu1

from gui_functions.submenu_2 import SubMenu2
from gui_functions.submenu_deletion import DeleteProfilesDialog
from gui_functions.submenu_modules import SubMenuModules
from gui_functions.submenu_social import SubMenuSocial
from updater.update_utils import check_for_updates
from gui_functions.utils import is_dark_mode_win, is_dark_mode_mac, apply_dark_theme, create_custom_title_bar


class ProfileManager:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.active_sessions: Dict[str, Any] = {}
        self.extensions = get_file_names(config.EXTENSIONS_DIR, files=False)
        self.running = True
        self.profile_map = {}  # Добавляем маппинг индексов к именам профилей
        self.setup_gui()
        release = check_for_updates()
        if release:
            if messagebox.askyesno("Update Available", "A new update is available. Do you want to install it?"):
                script_path = os.path.join(config.ROOT_DIR, "updater", "update_functions.py")
                if config.OS_TYPE == 'win':
                    subprocess.Popen(["start", "cmd", "/K", sys.executable, script_path], shell=True)
                elif config.OS_TYPE =='mac':
                    subprocess.Popen(["open", "-a", "Terminal", sys.executable, script_path])
                else:
                    subprocess.Popen(["gnome-terminal", "--", sys.executable, script_path])  # Для Linux
                sys.exit(0)
        else:
            messagebox.showinfo("Update", "No updates available.")

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Vortex Antidetect Browser")

        # create_custom_title_bar(self.root)

        # Настройка размеров окна
        window_width = 800
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        # Разрешаем изменение размера окна
        self.root.resizable(True, True)

        # Создаем основной фрейм, который будет растягиваться
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Заголовок
        title_label = tk.Label(
            main_frame,
            text="Available Profiles:",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Создаем фрейм для списка с полосой прокрутки
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Добавляем скроллбар
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Создаем список профилей с форматированным текстом
        self.profile_list = tk.Listbox(
            list_frame,
            font=("Consolas", 12),  # Моноширинный шрифт для лучшего выравнивания
            selectmode=tk.SINGLE,
            activestyle='none',
            selectbackground='#0078D7',
            selectforeground='black',
            highlightthickness=0,
            bd=0,
        )
        self.profile_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Привязываем скроллбар к списку
        scrollbar.config(command=self.profile_list.yview)
        self.profile_list.config(yscrollcommand=scrollbar.set)

        # Добавляем обработчик двойного клика
        self.profile_list.bind('<Double-Button-1>', self.on_double_click)

        # Добавляем контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit Note", command=self.edit_note)
        self.context_menu.add_command(label="Edit Proxy", command=self.edit_proxy)

        # Привязываем правый клик к показу меню
        self.profile_list.bind('<Button-3>', self.show_context_menu)

        # Загрузка профилей с форматированным отображением
        for profile in load_profiles():
            # Форматируем строку для отображения
            display_text = self.format_profile_display(profile)
            # Сохраняем имя профиля в дополнительных данных
            self.profile_list.insert(tk.END, display_text)
            # Сохраняем маппинг индекса к имени профиля
            self.profile_map[self.profile_list.size() - 1] = profile.name

        # Добавляем обработчик изменения размера окна
        self.root.bind('<Configure>', self.on_window_configure)

        # Создаем frame для кнопок
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10, fill=tk.X)

        # Стиль для кнопок
        button_style = {
            'font': ('Arial', 10),
            'padx': 20,
            'pady': 5,
            'bd': 1,
            'relief': tk.RAISED
        }

        more_button1 = tk.Button(
            button_frame,
            text="Import Settings ⚙️",
            command=self.open_submenu1,
            **button_style
        )
        more_button1.pack(side=tk.LEFT, padx=5)

        more_button2 = tk.Button(
            button_frame,
            text="Import seed phrases and private keys",
            command=self.open_submenu2,
            **button_style
        )
        more_button2.pack(side=tk.LEFT, padx=5)

        modules_button = tk.Button(
            button_frame,
            text="Modules",
            command=self.open_submenu_modules,
            **button_style
        )
        modules_button.pack(side=tk.LEFT, padx=5)

        social_button = tk.Button(
            button_frame,
            text="Social",
            command=self.open_submenu_social,
            **button_style
        )
        social_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(
            button_frame,
            text="Delete Profiles",
            command=self.open_submenu_deletion,
            **button_style
        )
        delete_button.pack(side=tk.LEFT, padx=5)

        # Добавляем кнопку синхронизации
        # sync_button = tk.Button(
        #     button_frame,
        #     text="Sync Profiles",
        #     command=self.on_sync_profiles,
        #     **button_style
        # )
        # sync_button.pack(side=tk.LEFT, padx=5)

        # Кроссплатформенная установка иконки
        try:
            logger.debug(f"OS type: {config.OS_TYPE}")
            if config.OS_TYPE == 'win':
                if is_dark_mode_win():
                    # icon_path = os.path.join(config.ASSETS_DIR, "Vortex-logo-white.ico")
                    # Применяем темную тему
                    apply_dark_theme(self.root)
                else:
                    # icon_path = os.path.join(config.ASSETS_DIR, "Vortex-logo-black.ico")
                    pass

                icon_path = os.path.join(config.ASSETS_DIR, "Vortex-logo-black.ico")
                self.root.iconbitmap(icon_path)

            else:
                if config.OS_TYPE == 'mac':
                    if is_dark_mode_mac():
                        icon_path = os.path.join(config.ASSETS_DIR, "Vortex-logo-white.png")
                        apply_dark_theme(self.root)
                    else:
                        icon_path = os.path.join(config.ASSETS_DIR, "Vortex-logo-black.png")
                else:
                    icon_path = os.path.join(config.ASSETS_DIR, "Vortex-logo-black.png")

                img = tk.PhotoImage(file=icon_path)
                self.root.tk.call('wm', 'iconphoto', self.root._w, img)

        except Exception as e:
            logger.error(f"Failed to load icon or set dark theme: {e}")


    def on_window_configure(self, event=None):
        """Обработчик изменения размера окна"""
        if event and event.widget == self.root:
            # Получаем новые размеры окна
            window_width = event.width
            window_height = event.height

            # Можно настроить размер шрифта в зависимости от размера окна
            font_size = max(10, min(16, window_height // 40))
            self.profile_list.configure(font=("Arial", font_size))

    def open_submenu1(self):
        """Открывает дополнительное меню"""
        submenu = SubMenu1(self.root, self.loop)
        submenu.transient(self.root)
        submenu.grab_set()

    def open_submenu2(self):
        submenu = SubMenu2(self.root, self.loop)
        submenu.transient(self.root)
        submenu.grab_set()

    def open_submenu_modules(self):
        submenu = SubMenuModules(self.root, self.loop)
        submenu.transient(self.root)
        submenu.grab_set()

    def open_submenu_social(self):
        submenu = SubMenuSocial(self.root, self.loop)
        submenu.transient(self.root)
        submenu.grab_set()

    def open_submenu_deletion(self):
        submenu = DeleteProfilesDialog(self.root, self.loop)
        submenu.transient(self.root)
        submenu.grab_set()

    def on_double_click(self, event):
        """Обработчик двойного клика по профилю"""
        selection = self.profile_list.curselection()
        if selection:
            index = selection[0]
            # Получаем имя профиля из маппинга
            profile_name = self.profile_map[index]
            profile = get_profile(profile_name)
            if profile:
                logger.debug(f"Launching profile {profile_name}...")
                # Запускаем профиль и обновляем список после запуска
                asyncio.run_coroutine_threadsafe(
                    self.launch_and_update(profile),
                    self.loop
                )

    async def launch_and_update(self, profile):
        """Запускает профиль и обновляет список"""
        try:
            async with async_playwright() as playwright_instance:
                await launch_profile_async(playwright_instance, profile, self.extensions)
            logger.debug(f"Profile {profile.name} closed")
            # Обновляем список профилей
            self.update_profile_list()
        except Exception as e:
            logger.error(f"Error launching profile {profile.name}: {e}")

    def update_profile_list(self):
        """Обновляет список профилей"""
        # Сохраняем текущее выделение
        current_selection = self.profile_list.curselection()

        # Очищаем список
        self.profile_list.delete(0, tk.END)
        self.profile_map.clear()

        # Перезагружаем профили
        for profile in load_profiles():
            display_text = self.format_profile_display(profile)
            self.profile_list.insert(tk.END, display_text)
            self.profile_map[self.profile_list.size() - 1] = profile.name

        # Восстанавливаем выделение, если оно было
        if current_selection:
            try:
                self.profile_list.selection_set(current_selection)
            except:
                pass


    def run(self):
        """Запускает главный цикл приложения"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.loop.create_task(self.update_gui())
        self.root.mainloop()

    def on_closing(self):
        """Обработчик закрытия окна"""
        self.running = False
        for session in self.active_sessions.values():
            if session:
                close_profile(session, self.active_sessions)
        self.root.quit()
        self.loop.call_soon_threadsafe(self.loop.stop)

    async def update_gui(self):
        while self.running:
            try:
                self.root.update()
                await asyncio.sleep(0.01)
            except tk.TclError:
                break
        self.running = False

    @staticmethod
    def format_profile_display(profile: Profile):
        """Форматирует строку для отображения профиля"""
        name = f"{profile.name:<20}"  # Имя профиля, минимум 20 символов

        last_opening_time = f"{profile.last_opening_time}"

        # Форматируем прокси для отображения
        proxy = profile.proxy if profile.proxy else "No proxy"
        if proxy != "No proxy":
            protocol = proxy.split('//')[0]
            proxy = proxy.split('@')[1]
            proxy = ''.join([protocol, '//', proxy])
        proxy = f"{proxy:<30}"  # Фиксированная ширина для прокси
        # print(len(proxy))
        # for _ in range(len(proxy), 30):
        #     proxy = "".join([proxy, ' '])

        # Форматируем примечание
        note = profile.note if profile.note else ""
        note = f"{note[:30]}..." if len(note) > 30 else note

        return f"{name} │ {last_opening_time} │ {proxy} {note}"  # todo: разобраться с пайпом после прокси

    # Добавим метод для редактирования примечания
    def edit_note(self):
        selection = self.profile_list.curselection()
        if selection:
            index = selection[0]
            profile_name = self.profile_map[index]
            profile = get_profile(profile_name)
            if profile:
                new_note = simpledialog.askstring(
                    "Edit Note",
                    "Enter note for profile:\t\t\t\t\t",
                    initialvalue=profile.note or ""
                )
                if new_note is not None:  # None если пользователь нажал Cancel
                    profile.note = new_note
                    db.commit()
                    # Обновляем отображение
                    self.profile_list.delete(index)
                    self.profile_list.insert(index, self.format_profile_display(profile))

    def edit_proxy(self):
        selection = self.profile_list.curselection()
        if selection:
            index = selection[0]
            profile_name = self.profile_map[index]
            profile = get_profile(profile_name)
            if profile:
                new_proxy = simpledialog.askstring(
                    "Edit Proxy",
                    "Enter new proxy for profile:\t\t\t\t\t\t\t",
                    initialvalue=profile.proxy or ""
                )
                if new_proxy is not None:  # None если пользователь нажал Cancel
                    profile.proxy = Proxy.from_str(new_proxy).as_url
                    db.commit()
                    # Обновляем отображение
                    self.profile_list.delete(index)
                    self.profile_list.insert(index, self.format_profile_display(profile))

    def show_context_menu(self, event):
        """Показывает контекстное меню при правом клике"""
        try:
            # Получаем индекс элемента под курсором
            index = self.profile_list.nearest(event.y)
            # Выделяем элемент
            self.profile_list.selection_clear(0, tk.END)
            self.profile_list.selection_set(index)
            # Показываем меню
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    # def on_sync_profiles(self):
    #     """Запускает синхронизированные профили"""
    #     from gui_functions.sync_dialog import SyncProfilesDialog
    #
    #     dialog = SyncProfilesDialog(self.root)
    #     self.root.wait_window(dialog)
    #
    #     if dialog.result:
    #         main_name, follower_names = dialog.result
    #         main_profile = get_profile(main_name)
    #         follower_profiles = [get_profile(name) for name in follower_names]
    #
    #         asyncio.run_coroutine_threadsafe(
    #             launch_synced_profiles(main_profile, follower_profiles, self.extensions),
    #             self.loop
    #         )
