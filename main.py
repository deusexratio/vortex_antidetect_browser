import asyncio
import threading

from browser_functions.patch import StealthPlaywrightPatcher
from file_functions.create_files import create_files
from gui_functions.profile_manager import ProfileManager

# Патчим Playwright
StealthPlaywrightPatcher().apply_patches()

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
