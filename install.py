import os
import sys
import venv
import subprocess
import platform
from pathlib import Path
import ctypes
from tkinter import messagebox
import tkinter as tk

if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.parent.absolute()


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
        # Импортируем Windows-зависимости только когда они нужны
        try:
            import winshell
            # import win32com.client
        except ImportError as e:
            print(f"Error importing Windows modules: {e}")
            print("Attempting to fix by reinstalling dependencies...")
            # Пробуем переустановить необходимые пакеты
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pywin32>=223"], check=True)
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "winshell"], check=True)
            import winshell
            # import win32com.client
            
        desktop = Path(winshell.desktop())
        path = os.path.join(desktop, "Vortex Antidetect Browser.lnk")
        
        # Создаем bat-файл для запуска
        run_script = os.path.join(os.path.dirname(script_path), "run.bat")
        with open(run_script, "w", encoding='utf-8') as f:
            f.write(f"""@echo off
call "{os.path.dirname(python_path)}\\activate.bat"
start "" "{python_path}" "{script_path}"
""")
        
        try:
            # Создаем ярлык через winshell
            with winshell.shortcut(path) as shortcut:
                shortcut.path = run_script
                shortcut.working_directory = os.path.dirname(script_path)
                shortcut.icon_location = (os.path.join(ROOT_DIR, "db", "assets", "logo.ico"), 0)
                shortcut.description = "Vortex Antidetect Browser"
        except Exception as e:
            print(f"Error creating shortcut with winshell: {e}")
            print("Trying alternative method with win32com...")
            # Альтернативный метод создания ярлыка
            # shell = win32com.client.Dispatch("WScript.Shell")
            # shortcut = shell.CreateShortCut(path)
            # shortcut.TargetPath = run_script
            # shortcut.WorkingDirectory = os.path.dirname(script_path)
            # shortcut.IconLocation = os.path.join(ROOT_DIR, "db", "assets", "logo.ico")
            # shortcut.Description = "Vortex Antidetect Browser"
            # shortcut.Save()
    else:
        # Создаем .desktop файл для Linux/MacOS
        run_script = create_run_script(python_path, script_path)
        
        desktop_entry = f"""[Desktop Entry]
Name=Vortex Antidetect Browser
Exec="{run_script}"
Icon={os.path.join(ROOT_DIR, "db", "assets", "logo.png")}
Type=Application
Terminal=false
Categories=Utility;
StartupWMClass=vortex-browser
"""
        if platform.system() == "Linux":
            # Создаем ярлык в меню приложений
            desktop_path = os.path.expanduser("~/.local/share/applications/vortex-browser.desktop")
            # И на рабочем столе
            desktop_shortcut = os.path.expanduser("~/Desktop/vortex-browser.desktop")
        else:  # MacOS
            desktop_path = os.path.expanduser("~/Applications/Vortex Browser.app/Contents/MacOS/vortex-browser")
            desktop_shortcut = os.path.expanduser("~/Desktop/Vortex Browser.command")
            
        # Создаем ярлык в меню приложений
        os.makedirs(os.path.dirname(desktop_path), exist_ok=True)
        with open(desktop_path, "w", encoding='utf-8') as f:
            f.write(desktop_entry)
        
        # Создаем ярлык на рабочем столе
        with open(desktop_shortcut, "w", encoding='utf-8') as f:
            if platform.system() == "Linux":
                f.write(desktop_entry)
            else:  # MacOS
                f.write(f"""#!/bin/bash
"{run_script}"
""")
        
        # Делаем файлы исполняемыми
        os.chmod(desktop_path, 0o755)
        os.chmod(desktop_shortcut, 0o755)

def create_run_script(python_path, script_path):
    """Создает скрипт запуска в зависимости от ОС"""
    if is_windows():
        run_script = os.path.join(os.path.dirname(script_path), "run.bat")
        with open(run_script, "w", encoding='utf-8') as f:
            f.write(f"""@echo off
call "{os.path.dirname(python_path)}\\activate.bat"
start "" "{python_path}" "{script_path}"
""")
    else:
        run_script = os.path.join(os.path.dirname(script_path), "run.sh")
        with open(run_script, "w", encoding='utf-8') as f:
            f.write(f"""#!/bin/bash
source "{os.path.dirname(python_path)}/activate"
cd "{os.path.dirname(script_path)}"  # Переходим в директорию скрипта
exec "{python_path}" "{script_path}"
""")
        os.chmod(run_script, 0o755)
    
    return run_script

def install_dependencies(pip_path):
    """Устанавливает зависимости с учетом ОС"""
    try:
        # Обновляем pip до последней версии
        print("Upgrading pip...")
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True, encoding='utf-8')
        
        if is_windows():
            # Windows-специфичная установка
            print("Installing pywin32...")
            subprocess.run([pip_path, "install", "--upgrade", "--no-cache-dir", "pywin32>=223"], check=True, encoding='utf-8')
            
            # Запускаем post-install скрипт pywin32
            python_path = os.path.dirname(pip_path)  # путь к папке Scripts
            python_exe = os.path.join(python_path, "python.exe")
            
            # Проверяем разные возможные пути к post-install скрипту
            possible_paths = [
                os.path.join(python_path, "pywin32_postinstall.py"),
                os.path.join(python_path, "Scripts", "pywin32_postinstall.py"),
                os.path.join(os.path.dirname(python_path), "Scripts", "pywin32_postinstall.py")
            ]
            
            post_install = None
            for path in possible_paths:
                if os.path.exists(path):
                    post_install = path
                    break
            
            if post_install:
                print(f"Running pywin32 post-install script: {post_install}")
                subprocess.run([python_exe, post_install, "-install"], check=True, encoding='utf-8')
            else:
                print("pywin32_postinstall.py not found, trying alternative installation...")
                # Пробуем переустановить pywin32
                subprocess.run([pip_path, "uninstall", "pywin32", "-y"], check=True, encoding='utf-8')
                subprocess.run([pip_path, "install", "--no-cache-dir", "pywin32>=223"], check=True, encoding='utf-8')
            
            print("Installing winshell...")
            subprocess.run([pip_path, "install", "--no-cache-dir", "winshell"], check=True, encoding='utf-8')
        
        # Устанавливаем общие зависимости по одной
        print("Installing common dependencies...")
        with open("requirements.txt", "r", encoding='utf-8') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        for req in requirements:
            print(f"Installing {req}...")
            try:
                subprocess.run([pip_path, "install", "--no-cache-dir", req], check=True, encoding='utf-8')
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {req}, trying alternative installation...")
                # Пробуем установить через альтернативный источник
                subprocess.run([pip_path, "install", "--no-cache-dir", "--index-url", "https://pypi.org/simple", req], check=True, encoding='utf-8')
        
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

        # Устанавливаем зависимости
        messagebox.showinfo("Installation", "Installing dependencies...")
        install_dependencies(pip_path)
        
        # Устанавливаем playwright
        messagebox.showinfo("Installation", "Installing Playwright...")
        subprocess.run([pip_path, "install", "playwright"], check=True)
        subprocess.run([python_path, "-m", "playwright", "install"], check=True)

        # Создаем ярлык/desktop entry и скрипт запуска
        main_script = os.path.join(current_dir, "main.py")
        create_shortcut(python_path, main_script)
        create_run_script(python_path, main_script)
        
        messagebox.showinfo("Installation", "Installation completed successfully!")
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during installation:\n{str(e)}")
        raise

if __name__ == "__main__":
    main()
