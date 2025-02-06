import asyncio
import sys
import os
import tkinter as tk
import traceback
from tkinter import messagebox, simpledialog
from loguru import logger
from typing import Dict, Any

from browser_functions.functions import close_profile, launch_profile_async
from db import config
from db.db_api import load_profiles, get_profile, flush_wallets
from db.models import db
from file_functions.Import import import_profiles, import_wallets
from file_functions.utils import get_file_names


class SubMenu1(tk.Toplevel):
    def __init__(self, parent, loop):
        super().__init__(parent)
        self.loop = loop
        self.title("Import Functions")

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
            ("Export selected cookies from AdsBrowser profiles", self.on_export_cookies),
            ("Import profiles to database from profiles.xlsx", import_profiles),
            ("Import cookies from profiles_ads.xlsx", self.on_import_cookies),
            ("Import wallets to database for profiles from profiles.xlsx", import_wallets),
            ("Flush all seed phrases and private keys from database", self.on_flush_wallets),
            ("Fetch all extension ids to database", self.on_fetch_extension_ids),
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
        import subprocess

        script_path = os.path.join(config.ROOT_DIR, "file_functions", "selected_cookies_from_ads.py")
        subprocess.Popen([sys.executable, script_path])

    @staticmethod
    def on_import_cookies():
        # if not os.path.exists(config.COOKIES_TABLE):
        #     messagebox.showwarning("Warning", f"Not found table with cookies, should be: {config.COOKIES_TABLE}!")
        #     # raise FileNotFoundError(f"Папка '{directory_path}' не существует.")
        # else:
        # Запускаем установку в отдельном процессе
        import subprocess

        script_path = os.path.join(config.ROOT_DIR, "file_functions", "import_cookies.py")
        subprocess.Popen([sys.executable, script_path])

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
            import subprocess

            script_path = os.path.join(config.ROOT_DIR, "file_functions", "get_ext_ids.py")
            subprocess.Popen([sys.executable, script_path])
        else:
            messagebox.showwarning("Warning", "No extension folders in user_files/extensions!")


class SubMenu2(tk.Toplevel):
    def __init__(self, parent, loop):
        super().__init__(parent)
        self.loop = loop
        self.title("Import Extensions Functions")

        # Настройка размеров окна
        window_width = 400
        window_height = 150
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        # Создаем и размещаем текст
        tk.Label(
            self, 
            text="Importing Wallets Under Construction...",
            font=("Arial", 12)
        ).pack(expand=True)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()


class ProfileManager:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.active_sessions: Dict[str, Any] = {}
        self.extensions = get_file_names(config.EXTENSIONS_DIR, files=False)
        self.running = True
        self.profile_map = {}  # Добавляем маппинг индексов к именам профилей
        self.setup_gui()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Vortex Antidetect Browser")

        # Кроссплатформенная установка иконки
        try:
            if os.name == 'nt':  # Windows
                icon_path = os.path.join(config.ASSETS_DIR, "logo.ico")
                self.root.iconbitmap(icon_path)
            else:  # Linux/Mac
                icon_path = os.path.join(config.ASSETS_DIR, "logo.png")
                img = tk.PhotoImage(file=icon_path)
                self.root.tk.call('wm', 'iconphoto', self.root._w, img)
        except Exception as e:
            logger.error(f"Failed to load icon: {e}")

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

        # Добавляем обработчик изменения размера окна
        self.root.bind('<Configure>', self.on_window_configure)

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
                asyncio.run_coroutine_threadsafe(
                    launch_profile_async(profile, self.extensions),
                    self.loop
                )

    def on_close(self):
        selected_profiles = [self.profile_list.get(idx) for idx in self.profile_list.curselection()]
        for profile in selected_profiles:
            close_profile(profile, self.active_sessions)

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

    def format_profile_display(self, profile):
        """Форматирует строку для отображения профиля"""
        name = f"{profile.name:<20}"  # Имя профиля, минимум 20 символов
        
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
#
        # Максимум 27 символов в прокси
        # минимум 23
        #

        # formatted_string =
        
        return f"{name} │ {proxy} │ {note}"

    # Добавим метод для редактирования примечания
    def edit_note(self, event=None):
        selection = self.profile_list.curselection()
        if selection:
            index = selection[0]
            profile_name = self.profile_map[index]
            profile = get_profile(profile_name)
            if profile:
                new_note = simpledialog.askstring(
                    "Edit Note",
                    "Enter note for profile:",
                    initialvalue=profile.note or ""
                )
                if new_note is not None:  # None если пользователь нажал Cancel
                    profile.note = new_note
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


class ExtensionDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        
        self.title("Install Extension")
        
        # Настройка размеров окна
        window_width = 500
        window_height = 150
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")
        
        # Создаем и размещаем элементы
        tk.Label(self, text="Installing extension...\nPlease wait while the extension is being installed in all profiles.").pack(pady=20)
        
        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()
        
        # Обновляем окно
        self.update()

    def on_install_extension(self):
        """Открывает диалог для установки расширения"""
        extension_url = tk.simpledialog.askstring(
            "Install Extension",
            "Enter Chrome Web Store link:\n" +
            "(e.g. https://chromewebstore.google.com/detail/rabby-wallet/acmacodkjbdgmoleebolmdjonilkdbch)"
        )
        
        if extension_url:
            # Показываем информационное окно
            dialog = ExtensionDialog(self)
            
            # Запускаем установку в отдельном процессе
            import subprocess
            import sys
            import os
            
            script_path = os.path.join(os.path.dirname(__file__), "file_functions", "install_extensions.py")
            process = subprocess.Popen([sys.executable, script_path, extension_url])
            
            # Периодически проверяем, завершился ли процесс
            def check_process():
                if process.poll() is None:
                    # Процесс еще работает, проверяем снова через 1 секунду
                    self.after(1000, check_process)
                else:
                    # Процесс завершен, закрываем диалог
                    dialog.destroy()
            
            # Начинаем проверку
            check_process()
