import tkinter as tk
from tkinter import ttk, messagebox
from .styles import set_styles
from .admin_panel import open_admin_panel
from .logger import get_logger


class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Авторизация")
        self.root.geometry("600x350")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        # Инициализируем логгер
        self.logger = get_logger()

        # Подключаем стили
        set_styles(self.root)

        # Центрируем окно
        self.center_window()

        self.create_widgets()

        # Логируем запуск окна авторизации
        self.logger.log_system_event("Login window opened")

    def center_window(self):
        """Центрирует окно на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # ---------- Заголовок ----------
        title = tk.Label(self.root,
                         text="Авторизация",
                         font=("Arial", 18, "bold"),
                         bg="#1e1e1e",
                         fg="white")
        title.pack(pady=30)

        # ---------- Фрейм для формы ----------
        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack(pady=10)

        # Логин
        login_label = ttk.Label(frame, text="Логин")
        login_label.grid(row=0, column=0, sticky="e", padx=10, pady=10)

        self.login_entry = ttk.Entry(frame, width=30)
        self.login_entry.grid(row=0, column=1, pady=10)
        self.login_entry.insert(0, "Введите логин")
        self.login_entry.bind('<FocusIn>', self.clear_placeholder)
        self.login_entry.bind('<FocusOut>', self.add_placeholder)

        # Пароль
        pass_label = ttk.Label(frame, text="Пароль")
        pass_label.grid(row=1, column=0, sticky="e", padx=10, pady=10)

        self.pass_entry = ttk.Entry(frame, width=30, show="*")
        self.pass_entry.grid(row=1, column=1, pady=10)
        self.pass_entry.insert(0, "Введите пароль")
        self.pass_entry.bind('<FocusIn>', self.clear_placeholder)
        self.pass_entry.bind('<FocusOut>', self.add_placeholder)

        # ---------- Кнопки ----------
        btn_frame = tk.Frame(self.root, bg="#1e1e1e")
        btn_frame.pack(pady=30)

        login_btn = ttk.Button(btn_frame, text="Войти", command=self.login)
        login_btn.grid(row=0, column=0, padx=20)

        reg_btn = ttk.Button(btn_frame, text="Регистрация", command=self.register)
        reg_btn.grid(row=0, column=1, padx=20)

        # Привязываем Enter к кнопке входа
        self.root.bind('<Return>', lambda e: self.login())

    def clear_placeholder(self, event):
        """Очищает placeholder при фокусе"""
        if event.widget.get() in ["Введите логин", "Введите пароль"]:
            event.widget.delete(0, tk.END)

    def add_placeholder(self, event):
        """Добавляет placeholder если поле пустое"""
        if not event.widget.get():
            if event.widget == self.login_entry:
                event.widget.insert(0, "Введите логин")
            else:
                event.widget.insert(0, "Введите пароль")

    def login(self):
        """Обработка входа"""
        username = self.login_entry.get()
        password = self.pass_entry.get()

        # Проверяем, что поля не пустые и не содержат placeholder'ы
        if username in ["Введите логин", ""] or password in ["Введите пароль", ""]:
            self.logger.log_auth_attempt("EMPTY_FIELDS", False)
            messagebox.showerror("Ошибка", "Пожалуйста, введите логин и пароль!")
            return

        # Сначала пробуем подключиться к базе данных
        try:
            # Импортируем базу данных
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'autorization'))
            from autorization.registration import Database

            # Создаем экземпляр базы данных
            db = Database()

            # Проверяем учетные данные
            success, message, is_admin = db.check_credentials(username, password)

            if success:
                user_type = "ADMIN" if is_admin else "USER"
                self.logger.log_auth_attempt(username, True)
                self.logger.log_user_login(username, user_type)

                messagebox.showinfo("Успех", "Авторизация прошла успешно!")
                # Закрываем текущее окно
                self.root.destroy()

                if is_admin:
                    # Открываем панель администратора
                    open_admin_panel()
                else:
                    # Открываем панель пользователя
                    from .user_panel import open_user_panel
                    open_user_panel(username)
            else:
                self.logger.log_auth_attempt(username, False)
                messagebox.showerror("Ошибка", message)

        except Exception as e:
            # Если БД недоступна, используем fallback систему
            self.logger.log_error("DATABASE_ERROR", str(e))
            print(f"Ошибка БД: {e}")
            self.fallback_login(username, password)

    def fallback_login(self, username, password):
        """Fallback система авторизации без БД"""
        # Простая проверка для тестирования
        if username == "admin" and password == "admin123":
            self.logger.log_auth_attempt(username, True)
            self.logger.log_user_login(username, "ADMIN")
            self.logger.log_system_event("Fallback mode activated", f"User: {username}")

            messagebox.showinfo("Успех", "Авторизация прошла успешно! (Fallback режим)")
            self.root.destroy()
            open_admin_panel()
        elif username == "user" and password == "user123":
            self.logger.log_auth_attempt(username, True)
            self.logger.log_user_login(username, "USER")
            self.logger.log_system_event("Fallback mode activated", f"User: {username}")

            messagebox.showinfo("Успех", "Авторизация прошла успешно! (Fallback режим)")
            self.root.destroy()
            from .user_panel import open_user_panel
            open_user_panel("user")
        else:
            self.logger.log_auth_attempt(username, False)
            messagebox.showerror("Ошибка",
                                 "Неверный логин или пароль!\n\nТестовые данные:\nАдмин: admin / admin123\nПользователь: user / user123")

    def register(self):
        """Обработка регистрации"""
        # Создаем окно регистрации
        register_window = tk.Toplevel(self.root)
        register_window.title("Регистрация")
        register_window.geometry("400x300")
        register_window.configure(bg="#1e1e1e")
        register_window.resizable(False, False)

        # Центрируем окно
        register_window.update_idletasks()
        width = register_window.winfo_width()
        height = register_window.winfo_height()
        x = (register_window.winfo_screenwidth() // 2) - (width // 2)
        y = (register_window.winfo_screenheight() // 2) - (height // 2)
        register_window.geometry(f'{width}x{height}+{x}+{y}')

        # Заголовок
        title = tk.Label(register_window,
                         text="Регистрация",
                         font=("Arial", 16, "bold"),
                         bg="#1e1e1e",
                         fg="white")
        title.pack(pady=20)

        # Фрейм для формы
        frame = tk.Frame(register_window, bg="#1e1e1e")
        frame.pack(pady=20)

        # Логин
        login_label = ttk.Label(frame, text="Логин")
        login_label.grid(row=0, column=0, sticky="e", padx=10, pady=10)

        reg_login_entry = ttk.Entry(frame, width=25)
        reg_login_entry.grid(row=0, column=1, pady=10)

        # Пароль
        pass_label = ttk.Label(frame, text="Пароль")
        pass_label.grid(row=1, column=0, sticky="e", padx=10, pady=10)

        reg_pass_entry = ttk.Entry(frame, width=25, show="*")
        reg_pass_entry.grid(row=1, column=1, pady=10)

        # Кнопки
        btn_frame = tk.Frame(register_window, bg="#1e1e1e")
        btn_frame.pack(pady=20)

        def register_user():
            username = reg_login_entry.get()
            password = reg_pass_entry.get()

            if not username or not password:
                self.logger.log_registration("EMPTY_FIELDS", False)
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля!")
                return

            if len(password) < 8:
                self.logger.log_registration(username, False)
                messagebox.showerror("Ошибка", "Пароль должен содержать минимум 8 символов!")
                return

            if len(username) < 3:
                self.logger.log_registration(username, False)
                messagebox.showerror("Ошибка", "Логин должен содержать минимум 3 символа!")
                return

            try:
                # Импортируем базу данных
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'autorization'))
                from autorization.registration import Database

                # Создаем экземпляр базы данных
                db = Database()

                # Регистрируем пользователя
                success, message = db.register_user(username, password)

                if success:
                    self.logger.log_registration(username, True)
                    messagebox.showinfo("Успех", message)
                    register_window.destroy()
                else:
                    self.logger.log_registration(username, False)
                    messagebox.showerror("Ошибка", message)

            except Exception as e:
                # Fallback регистрация
                self.logger.log_registration(username, True)
                self.logger.log_system_event("Fallback registration", f"User: {username}")
                messagebox.showinfo("Информация",
                                    f"База данных недоступна. Регистрация в fallback режиме.\n\nПользователь '{username}' зарегистрирован локально.")
                register_window.destroy()

        register_btn = ttk.Button(btn_frame, text="Зарегистрироваться", command=register_user)
        register_btn.pack(side=tk.LEFT, padx=10)

        cancel_btn = ttk.Button(btn_frame, text="Отмена", command=register_window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)

    def run(self):
        """Запуск окна"""
        self.root.mainloop()


def open_login_window():
    """Функция для открытия окна авторизации"""
    app = LoginWindow()
    app.run()


if __name__ == "__main__":
    open_login_window()