import tkinter as tk
from tkinter import ttk, messagebox
from .styles import set_styles
from .backup_storage import open_backup_storage
from .logger import get_logger
from crypto.config_manager import config_manager
from .setup import run_setup


class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Авторизация в системе резервного копирования")
        self.root.geometry("500x350")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        self.logger = get_logger()
        set_styles(self.root)
        self.center_window()

        # Проверяем, существует ли конфигурационный файл
        if not config_manager.config_exists():
            self.show_setup_message()
        else:
            self.create_widgets()

        self.logger.log_system_event("Login window opened")

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def show_setup_message(self):
        """Показывает сообщение о необходимости настройки"""
        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack(expand=True)

        message = tk.Label(frame,
                           text="Система не настроена\nНеобходима первоначальная настройка",
                           font=("Arial", 14),
                           bg="#1e1e1e",
                           fg="white",
                           justify=tk.CENTER)
        message.pack(pady=20)

        btn_frame = tk.Frame(frame, bg="#1e1e1e")
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Настроить", command=self.open_setup).pack(pady=10)
        ttk.Button(btn_frame, text="Выход", command=self.root.quit).pack(pady=10)

    def create_widgets(self):
        title = tk.Label(self.root,
                         text="Система резервного копирования",
                         font=("Arial", 16, "bold"),
                         bg="#1e1e1e",
                         fg="white")
        title.pack(pady=20)

        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack(pady=10)

        # Логин
        ttk.Label(frame, text="Логин:").grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.username_entry = ttk.Entry(frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=10)

        # Пароль
        ttk.Label(frame, text="Пароль:").grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.password_entry = ttk.Entry(frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=10)

        # Пароль шифрования
        ttk.Label(frame, text="Пароль шифрования:").grid(row=2, column=0, sticky="e", padx=10, pady=10)
        self.encrypt_password_entry = ttk.Entry(frame, width=30, show="*")
        self.encrypt_password_entry.grid(row=2, column=1, pady=10)

        btn_frame = tk.Frame(self.root, bg="#1e1e1e")
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Войти", command=self.login).pack(pady=10, ipadx=20, ipady=5)
        self.root.bind('<Return>', lambda e: self.login())

    def open_setup(self):
        """Открывает окно настройки"""
        self.root.destroy()
        run_setup()

    def login(self):
        """Обработка входа"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        encrypt_password = self.encrypt_password_entry.get()

        if not all([username, password, encrypt_password]):
            self.logger.log_auth_attempt("SYSTEM", False)
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            if config_manager.check_credentials(username, password, encrypt_password):
                self.logger.log_auth_attempt("SYSTEM", True)
                self.logger.log_system_event("Authentication successful")

                messagebox.showinfo("Успех", "Авторизация прошла успешно!")
                self.root.destroy()
                open_backup_storage()
            else:
                self.logger.log_auth_attempt("SYSTEM", False)
                messagebox.showerror("Ошибка", "Неверные учетные данные!")

        except Exception as e:
            self.logger.log_auth_attempt("SYSTEM", False)
            messagebox.showerror("Ошибка", f"Ошибка при проверке учетных данных: {e}")

    def run(self):
        self.root.mainloop()


def open_login_window():
    app = LoginWindow()
    app.run()


if __name__ == "__main__":
    open_login_window()