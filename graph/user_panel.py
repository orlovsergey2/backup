import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from .styles import set_styles
from .logger import get_logger
from .user_file import UserStorage

class UserPanel:
    def __init__(self, username):
        self.username = username
        self.root = tk.Tk()
        self.root.title("Панель пользователя")
        self.root.geometry("500x400")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        # Инициализируем логгер
        self.logger = get_logger()

        # Подключаем стили
        set_styles(self.root)

        # Центрируем окно
        self.center_window()

        self.create_widgets()

        # Логируем открытие панели пользователя
        self.logger.log_user_action(username, "USER_PANEL_OPENED")

    def center_window(self):
        """Центрирует окно на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Заголовок
        title = tk.Label(self.root,
                         text="Панель пользователя",
                         font=("Arial", 18, "bold"),
                         bg="#1e1e1e",
                         fg="white")
        title.pack(pady=30)

        # Информация о пользователе
        user_info = tk.Label(self.root,
                             text=f"Добро пожаловать, {self.username}!",
                             font=("Arial", 12),
                             bg="#1e1e1e",
                             fg="#3498db")
        user_info.pack(pady=10)

        # Фрейм для кнопок
        btn_frame = tk.Frame(self.root, bg="#1e1e1e")
        btn_frame.pack(pady=40)

        # Кнопка хранилища
        storage_btn = ttk.Button(btn_frame,
                                 text="Мое хранилище",
                                 command=self.open_storage)
        storage_btn.pack(pady=10, ipadx=20, ipady=10)

        # Кнопка выхода
        logout_btn = ttk.Button(btn_frame,
                                text="Выйти",
                                command=self.logout)
        logout_btn.pack(pady=20, ipadx=20, ipady=10)

    def open_storage(self):
        """Открыть хранилище файлов пользователя"""
        # Логируем действие
        self.logger.log_user_action(self.username, "OPEN_USER_STORAGE")

        # Закрываем панель пользователя
        self.root.destroy()

        # Создаем новое окно хранилища
        storage_window = tk.Tk()
        storage_window.title("Мое хранилище")
        storage_window.geometry("700x500")
        storage_window.configure(bg="#f5f5f5")

        # Центрируем окно
        storage_window.update_idletasks()
        width = storage_window.winfo_width()
        height = storage_window.winfo_height()
        x = (storage_window.winfo_screenwidth() // 2) - (width // 2)
        y = (storage_window.winfo_screenheight() // 2) - (height // 2)
        storage_window.geometry(f'{width}x{height}+{x}+{y}')

        # Обработчик закрытия окна
        def on_closing():
            storage_window.destroy()
            # Возвращаемся к панели пользователя
            from .user_panel import open_user_panel
            open_user_panel(self.username)

        storage_window.protocol("WM_DELETE_WINDOW", on_closing)

        # Создаем экземпляр хранилища пользователя
        storage_app = UserStorage(storage_window, self.username, show_back_button=True, back_callback=on_closing)

    def logout(self):
        """Выход из системы"""
        # Логируем выход
        self.logger.log_user_logout(self.username, "USER")

        # Закрываем текущее окно
        self.root.destroy()
        # Импортируем здесь, чтобы избежать циклического импорта
        from .autorization import open_login_window
        open_login_window()

    def run(self):
        """Запуск окна"""
        self.root.mainloop()


def open_user_panel(username):
    """Функция для открытия панель пользователя"""
    app = UserPanel(username)
    app.run()



if __name__ == "__main__":
    open_user_panel("test_user")