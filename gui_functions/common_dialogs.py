import tkinter as tk
from tkinter import messagebox


class PasswordThreadsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None

        self.title("Enter password for wallet and number of threads")

        # Настройка размеров окна
        window_width = 350
        window_height = 150
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        # Создаем и размещаем элементы
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Поле для пароля
        tk.Label(frame, text="Password:").grid(row=0, column=0, sticky='w', pady=5)
        self.password_entry = tk.Entry(frame) # show="*"
        self.password_entry.grid(row=0, column=1, sticky='ew', pady=5)
        self.password_entry.insert(0, "12345678")  # Значение по умолчанию

        # Поле для количества потоков
        tk.Label(frame, text="Threads:").grid(row=1, column=0, sticky='w', pady=5)
        self.threads_entry = tk.Entry(frame)
        self.threads_entry.grid(row=1, column=1, sticky='ew', pady=5)
        self.threads_entry.insert(0, "3")  # Значение по умолчанию

        # Кнопки
        button_frame = tk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        tk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.LEFT, padx=5)

        # Настройка grid
        frame.columnconfigure(1, weight=1)

        # Делаем диалог модальным
        self.transient(parent)
        self.grab_set()

        # Фокус на поле пароля
        self.password_entry.focus_set()

        # Привязываем Enter к OK
        self.bind('<Return>', lambda e: self.on_ok())

    def on_ok(self):
        try:
            threads = int(self.threads_entry.get())
            if threads <= 0:
                raise ValueError("Threads must be positive")
            password = self.password_entry.get()
            if not password:
                raise ValueError("Password cannot be empty")
            self.result = (password, threads)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def on_cancel(self):
        self.destroy()