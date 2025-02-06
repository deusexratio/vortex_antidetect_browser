import os
import sys
import venv
import subprocess
import platform
from pathlib import Path
import ctypes
from tkinter import messagebox
import tkinter as tk

from db import config


def is_windows():
    return platform.system() == "Windows"

def is_admin():
    """Проверяет права администратора для Windows или root для Unix"""
    if is_windows():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.geteuid() == 0  # Проверка root прав для Unix

def create_shortcut(python_path, script_path):
    """Создает ярлык/desktop entry в зависимости от ОС"""
    if is_windows():
        import winshell
        desktop = Path(winshell.desktop())
        path = os.path.join(desktop, "Vortex Antidetect Browser.lnk")

        with winshell.shortcut(path) as shortcut:
            shortcut.path = python_path
            shortcut.arguments = script_path
            shortcut.working_directory = os.path.dirname(script_path)
            shortcut.icon_location = (os.path.join(config.ROOT_DIR, "db", "assets", "logo.ico"), 0)
            shortcut.description = "Vortex Antidetect Browser"
    else:
        # Создаем .desktop файл для Linux/MacOS
        desktop_entry = f"""[Desktop Entry]
Name=Profile Manager
Exec={python_path} {script_path}
Icon={os.path.join(config.ROOT_DIR, "db", "assets", "logo.ico")}
Type=Application
Terminal=false
Categories=Utility;
"""
        if platform.system() == "Linux":
            desktop_path = os.path.expanduser("~/.local/share/applications/profile-manager.desktop")
        else:  # MacOS
            desktop_path = os.path.expanduser("~/Applications/Profile Manager.app")
            
        os.makedirs(os.path.dirname(desktop_path), exist_ok=True)
        with open(desktop_path, "w") as f:
            f.write(desktop_entry)
        
        if platform.system() == "Linux":
            # Делаем файл исполняемым
            os.chmod(desktop_path, 0o755)

def install_dependencies(pip_path):
    """Устанавливает зависимости с учетом ОС"""
    try:
        if is_windows():
            # Windows-специфичная установка
            subprocess.run([pip_path, "install", "pywin32>=223"], check=True)
            subprocess.run([pip_path, "install", "winshell"], check=True)
            
            # Запускаем post-install скрипт pywin32
            python_path = os.path.dirname(pip_path)
            post_install = os.path.join(python_path, "Scripts", "pywin32_postinstall.py")
            subprocess.run([os.path.join(python_path, "python.exe"), post_install, "-install"], check=True)
        
        # Общие зависимости для всех ОС
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to install dependencies: {str(e)}")

def main():
    # Проверяем права администратора/root
    if not is_admin():
        if is_windows():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        else:
            messagebox.showerror("Error", "Please run the installer with sudo privileges")
        return

    root = tk.Tk()
    root.withdraw()

    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        venv_dir = os.path.join(current_dir, "venv")
        
        # Создаем виртуальное окружение
        messagebox.showinfo("Installation", "Creating virtual environment...")
        venv.create(venv_dir, with_pip=True)
        
        # Определяем пути в зависимости от ОС
        if is_windows():
            scripts_dir = "Scripts"
        else:
            scripts_dir = "bin"
            
        python_path = os.path.join(venv_dir, scripts_dir, "python")
        pip_path = os.path.join(venv_dir, scripts_dir, "pip")
        
        if is_windows():
            python_path += ".exe"
            pip_path += ".exe"
        
        # Обновляем pip
        messagebox.showinfo("Installation", "Updating pip...")
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        
        # Устанавливаем зависимости
        messagebox.showinfo("Installation", "Installing dependencies...")
        install_dependencies(pip_path)
        
        # Устанавливаем patchright
        messagebox.showinfo("Installation", "Installing Patchright...")
        subprocess.run([pip_path, "install", "patchright"], check=True)
        subprocess.run([python_path, "-m", "patchright", "install"], check=True)
        
        # Создаем необходимые директории
        os.makedirs(os.path.join(current_dir, "user_files", "extensions"), exist_ok=True)
        os.makedirs(os.path.join(current_dir, "user_files", "cookies"), exist_ok=True)
        os.makedirs(os.path.join(current_dir, "db", "browser_data"), exist_ok=True)
        os.makedirs(os.path.join(current_dir, "assets"), exist_ok=True)
        
        # Создаем ярлык/desktop entry
        main_script = os.path.join(current_dir, "main.py")
        create_shortcut(python_path, main_script)
        
        messagebox.showinfo("Installation", "Installation completed successfully!")
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during installation:\n{str(e)}")
        raise

if __name__ == "__main__":
    main()
