import asyncio
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox
from loguru import logger
import tkinter.ttk as ttk
from typing import Dict, Any
import threading

from browser_functions.functions import close_profile, launch_profile_async
from db.db_api import load_profiles, get_profile
from file_functions.Import import import_profiles, import_wallets
from file_functions.create_files import create_files


active_sessions = {}
extensions = []

class SubMenu(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Дополнительные функции")
        
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
            ("Настройки профилей", self.on_profile_settings),
            ("Управление прокси", self.on_proxy_management),
            ("Настройки браузера", self.on_browser_settings),
            # ("Импорт/Экспорт", self.on_import_export),
            ("Import profiles from profiles.xlsx", import_profiles),
            ("Import wallets for profiles from profiles.xlsx", import_wallets)
        ]
        
        for text, command in buttons:
            btn = tk.Button(button_frame, text=text, command=command)
            btn.pack(pady=5, fill=tk.X)
            
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

class ProfileManager:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.active_sessions: Dict[str, Any] = {}
        self.extensions = []
        self.running = True  # Флаг для контроля работы цикла
        self.setup_gui()
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Profile Manager")
        
        # Настройка размеров окна
        window_width = 800
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")
        
        # Создание элементов интерфейса
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        
        tk.Label(frame, text="Available Profiles:").pack()
        self.profile_list = tk.Listbox(frame, selectmode=tk.MULTIPLE, width=100, height=20)
        self.profile_list.pack()
        
        # Загрузка профилей
        for profile in load_profiles():
            self.profile_list.insert(tk.END, profile.name)
            
        # Создаем frame для кнопок
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        
        # Основные кнопки в один ряд
        launch_button = tk.Button(button_frame, text="Launch Selected", command=self.on_launch)
        launch_button.pack(side=tk.LEFT, padx=5)
        
        close_button = tk.Button(button_frame, text="Close Selected", command=self.on_close)
        close_button.pack(side=tk.LEFT, padx=5)
        
        # import_button = tk.Button(button_frame, text="Import profiles", command=import_profiles)
        # import_button.pack(side=tk.LEFT, padx=5)
        
        # Кнопка дополнительного меню
        more_button = tk.Button(button_frame, text="Дополнительно ⚙", command=self.open_submenu)
        more_button.pack(side=tk.LEFT, padx=5)
        
    def on_launch(self):
        selected_profiles = [self.profile_list.get(idx) for idx in self.profile_list.curselection()]
        if not selected_profiles:
            messagebox.showwarning("Warning", "No profiles selected!")
            return
            
        for profile_name in selected_profiles:
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

    def open_submenu(self):
        """Открывает дополнительное меню"""
        submenu = SubMenu(self.root)
        submenu.transient(self.root)  # Делаем окно зависимым от основного
        submenu.grab_set()  # Захватываем фокус

def main():
    # Создаем и настраиваем event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    create_files()
    
    # Создаем и запускаем приложение
    app = ProfileManager(loop)
    
    # Запускаем event loop в отдельном потоке
    loop_thread = threading.Thread(target=lambda: loop.run_forever())
    loop_thread.daemon = True
    loop_thread.start()
    
    # Запускаем главный цикл Tkinter
    try:
        app.run()
    finally:
        # Ждем завершения всех задач
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        
        # Останавливаем loop и ждем завершения потока
        loop.call_soon_threadsafe(loop.stop)
        loop_thread.join(timeout=1.0)
        
        # Закрываем loop только если он остановлен
        if not loop.is_running():
            loop.close()

if __name__ == "__main__":
    main()
