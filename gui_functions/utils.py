import ctypes
import os
import subprocess
import sys
import tkinter as tk

from loguru import logger

from db import config


def is_dark_mode_win():
    try:
        # Открываем ключ реестра
        registry = ctypes.windll.advapi32.RegOpenKeyExW
        hkey = ctypes.c_void_p()
        registry(0x80000001, "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", 0, 0x20019,
                 ctypes.byref(hkey))

        # Читаем значение реестра
        value = ctypes.c_ulong()
        ctypes.windll.advapi32.RegQueryValueExW(hkey, "AppsUseLightTheme", 0, None, ctypes.byref(value),
                                                ctypes.byref(ctypes.c_ulong()))

        # Закрываем ключ реестра
        ctypes.windll.advapi32.RegCloseKey(hkey)

        # Если значение 0, то используется тёмная тема
        return value.value == 0
    except Exception as e:
        print(f"Error checking dark mode: {e}")
        return False

def is_dark_mode_mac():
    try:
        # Выполняем команду defaults для получения текущей темы
        result = subprocess.run(
            ["defaults", "read", "-g", "AppleInterfaceStyle"],
            capture_output=True,
            text=True
        )
        # Если результат содержит "Dark", то используется тёмная тема
        return "Dark" in result.stdout
    except Exception as e:
        print(f"Error checking dark mode: {e}")
        return False


def apply_dark_theme(root):
    """Применяет темную тему к интерфейсу"""
    # Устанавливаем цвета для темной темы
    dark_bg = "#2E2E2E"
    dark_fg = "#FFFFFF"
    dark_button_bg = "#3E3E3E"
    dark_button_fg = "#FFFFFF"

    # Применяем цвета к основному окну
    root.configure(bg=dark_bg)

    def apply_theme(widget):
        """Рекурсивно применяет тему к виджету и его дочерним элементам"""
        if isinstance(widget, tk.Label):
            widget.configure(bg=dark_bg, fg=dark_fg)
        elif isinstance(widget, tk.Button):
            widget.configure(bg=dark_button_bg, fg=dark_button_fg, activebackground=dark_bg, activeforeground=dark_fg)
        elif isinstance(widget, tk.Listbox):
            widget.configure(bg=dark_bg, fg=dark_fg, selectbackground="#5E5E5E", selectforeground=dark_fg)
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=dark_bg, fg=dark_fg, insertbackground=dark_fg)
        elif isinstance(widget, tk.Text):
            widget.configure(bg=dark_bg, fg=dark_fg, insertbackground=dark_fg)
        elif isinstance(widget, tk.Frame):
            widget.configure(bg=dark_bg)

        # Рекурсивно применяем тему к дочерним виджетам
        for child in widget.winfo_children():
            apply_theme(child)

    # Применяем тему ко всем виджетам в окне
    apply_theme(root)


def create_custom_title_bar(root):
    # Скрываем стандартный заголовок окна
    root.overrideredirect(True)

    try:
        os_type = 'win' if sys.platform.startswith('win') else 'mac' if sys.platform.startswith(
            'darwin') else 'linux' if sys.platform.startswith('linux') else 'unknown'
        if os_type == 'win':
            if is_dark_mode_win():
                icon_path = os.path.join(config.ASSETS_DIR, "Vortex-logo-white.ico")
                # Применяем темную тему
                apply_dark_theme(root)
            else:
                icon_path = os.path.join(config.ASSETS_DIR, "Vortex-logo-black.ico")

            root.iconbitmap(icon_path)

        else:
            if os_type == 'mac':
                if is_dark_mode_mac():
                    icon_path = os.path.join(config.ASSETS_DIR, "Vortex-logo-white.png")
                    apply_dark_theme(root)
                else:
                    icon_path = os.path.join(config.ASSETS_DIR, "Vortex-logo-black.png")
            else:
                icon_path = os.path.join(config.ASSETS_DIR, "Vortex-logo-black.png")

            img = tk.PhotoImage(file=icon_path)
            root.tk.call('wm', 'iconphoto', root._w, img)

    except Exception as e:
        logger.error(f"Failed to load icon: {e}")

    # Создаем фрейм для заголовка
    title_bar = tk.Frame(root, bg="#2E2E2E", relief="solid", bd=2)
    title_bar.pack(side="top", fill="x")

    # Добавляем текст заголовка
    title_label = tk.Label(title_bar, text="Vortex Antidetect Browser", bg="#2E2E2E", fg="#FFFFFF")
    title_label.pack(side="left", padx=10)

    # Добавляем кнопку закрытия
    close_button = tk.Button(title_bar, text="X", bg="#2E2E2E", fg="#FFFFFF", command=root.destroy)
    close_button.pack(side="right", padx=10)

    # Функции для перемещения окна
    def start_move(event):
        root.x = event.x
        root.y = event.y

    def stop_move(event):
        root.x = None
        root.y = None

    def on_motion(event):
        deltax = event.x - root.x
        deltay = event.y - root.y
        new_x = root.winfo_x() + deltax
        new_y = root.winfo_y() + deltay
        root.geometry(f"+{new_x}+{new_y}")

    # Привязываем события
    title_bar.bind("<ButtonPress-1>", start_move)
    title_bar.bind("<ButtonRelease-1>", stop_move)
    title_bar.bind("<B1-Motion>", on_motion)

    if os_type == 'win':
        # Добавляем окно в панель задач
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        style |= 0x00000080  # WS_EX_APPWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
        root.wm_withdraw()
        root.after(10, root.wm_deiconify)

