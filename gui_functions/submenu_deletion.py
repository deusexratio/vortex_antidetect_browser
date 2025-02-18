import os
import tkinter as tk
from tkinter import messagebox

from loguru import logger

from db.db_api import load_profiles, get_profile
from db.models import db


class DeleteProfilesDialog(tk.Toplevel):
    def __init__(self, parent, loop):
        super().__init__(parent)
        self.result = None
        self.parent = parent
        self.loop = loop
        self.names_to_delete = None

        self.title("Select Profiles to delete:")

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

        # Фрейм для списка с прокруткой
        list_frame = tk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Добавляем скроллбар
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Список профилей
        tk.Label(frame, text="Select profiles to delete:").pack()
        self.profiles_list = tk.Listbox(list_frame, height=25, selectmode=tk.MULTIPLE, exportselection=0)
        self.profiles_list.pack(fill=tk.X, pady=5)

        # Загружаем профили
        for profile in load_profiles():
            self.profiles_list.insert(tk.END, profile.name)

        # Привязываем скроллбар к списку
        scrollbar.config(command=self.profiles_list.yview)
        self.profiles_list.config(yscrollcommand=scrollbar.set)

        # Кнопки
        tk.Button(frame, text="Cancel", command=self.destroy).pack(side=tk.BOTTOM, padx=5)
        tk.Button(frame, text="Delete", command=self.on_delete_choice).pack(side=tk.BOTTOM, padx=5)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()

        parent.wait_window(self)


    def on_delete_choice(self):
        profiles_selection = self.profiles_list.curselection()

        if not profiles_selection:
            messagebox.showerror("Error", "Please select profiles")
            return

        self.names_to_delete = [self.profiles_list.get(i) for i in profiles_selection]

        choose_method_dialog = ChooseDeletionMethod(self)
        self.wait_window(choose_method_dialog)

        # if choose_method_dialog.result:
        #     method = choose_method_dialog.result
        #
        #     self.result = profile_names, taps_range, password, threads
        #     self.destroy()

    def delete_from_db(self):
        count_ = 0
        for profile_name in self.names_to_delete:
            profile = get_profile(profile_name)
            logger.debug(f"Got profile entity {profile} from database, deleting it")
            db.delete(profile)
            logger.success(f"Deleted profile {profile_name} entity from database")
            count_ += 1

        return count_

    def delete_completely(self):
        count_ = 0
        for profile_name in self.names_to_delete:
            profile = get_profile(profile_name)
            logger.debug(f"Got profile entity {profile} from database, deleting it's browser cache")
            os.rmdir(profile.user_data_dir)
            logger.success(f"Deleted profile {profile_name} browser cache in {profile.user_data_dir}")
            count_ += 1

        self.delete_from_db()
        return count_


    def on_delete_completely(self):
        deleted = self.delete_completely()
        messagebox.showinfo("Success", f"Deleted {deleted} profiles browser cache folders")
        self.destroy()

    def on_delete_from_db(self):
        deleted = self.delete_from_db()
        messagebox.showinfo("Success", f"Deleted {deleted} profiles entities from database")
        self.destroy()




class ChooseDeletionMethod(tk.Toplevel):
    def __init__(self, parent: DeleteProfilesDialog):
        super().__init__(parent)
        self.result = None
        self.parent = parent

        self.title("Choose deletion method")

        # Настройка размеров окна
        window_width = 400
        window_height = 150
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        # Настройка окна
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Кнопки
        tk.Button(frame, text="Cancel", command=self.destroy).pack(side=tk.BOTTOM, padx=5)
        tk.Button(frame, text="Delete only from database", command=self.parent.on_delete_from_db).pack(side=tk.BOTTOM, padx=5)
        tk.Button(frame, text="Delete completely with all browser cache", command=self.parent.on_delete_completely).pack(side=tk.BOTTOM, padx=5)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()
