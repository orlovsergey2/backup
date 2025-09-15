import tkinter as tk
from tkinter import ttk
from .styles import set_styles
from .file_admin import SimpleAdminStorage
from .logger import get_logger

class AdminPanel:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Панель администратора")
        self.root.geometry("550x550")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)
        
        # Инициализируем логгер
        self.logger = get_logger()
        
        # Подключаем стили
        set_styles(self.root)
        
        # Центрируем окно
        self.center_window()
        
        self.create_widgets()
        
        # Логируем открытие панели администратора
        self.logger.log_admin_action("admin", "ADMIN_PANEL_OPENED")

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
                         text="Панель администратора",
                         font=("Arial", 18, "bold"),
                         bg="#1e1e1e",
                         fg="white")
        title.pack(pady=30)

        # Информация о пользователе
        user_info = tk.Label(self.root,
                            text="Добро пожаловать, Администратор!",
                            font=("Arial", 12),
                            bg="#1e1e1e",
                            fg="#3498db")
        user_info.pack(pady=10)

        # Фрейм для кнопок
        btn_frame = tk.Frame(self.root, bg="#1e1e1e")
        btn_frame.pack(pady=40)

        # Кнопка списка пользователей
        users_btn = ttk.Button(btn_frame, 
                              text="Список пользователей", 
                              command=self.show_users)
        users_btn.pack(pady=10, ipadx=20, ipady=10)

        # Кнопка хранилища
        storage_btn = ttk.Button(btn_frame, 
                                text="Хранилище", 
                                command=self.open_storage)
        storage_btn.pack(pady=10, ipadx=20, ipady=10)

        # Кнопка просмотра логов
        logs_btn = ttk.Button(btn_frame, 
                             text="Просмотр логов", 
                             command=self.view_logs)
        logs_btn.pack(pady=10, ipadx=20, ipady=10)

        # Кнопка выхода
        logout_btn = ttk.Button(btn_frame, 
                               text="Выйти", 
                               command=self.logout)
        logout_btn.pack(pady=20, ipadx=20, ipady=10)

    def show_users(self):
        """Показать список пользователей"""
        # Логируем действие
        self.logger.log_admin_action("admin", "VIEW_USERS_LIST")
        
        # Закрываем панель администратора
        self.root.destroy()
        
        # Создаем новое окно списка пользователей
        users_window = tk.Tk()
        users_window.title("Список пользователей")
        users_window.geometry("450x400")
        users_window.configure(bg="#1e1e1e")
        
        # Центрируем окно
        users_window.update_idletasks()
        width = users_window.winfo_width()
        height = users_window.winfo_height()
        x = (users_window.winfo_screenwidth() // 2) - (width // 2)
        y = (users_window.winfo_screenheight() // 2) - (height // 2)
        users_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Обработчик закрытия окна
        def on_closing():
            users_window.destroy()
            # Возвращаемся к панели администратора
            from .admin_panel import open_admin_panel
            open_admin_panel()
        
        users_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        title = tk.Label(users_window,
                         text="Список пользователей",
                         font=("Arial", 16, "bold"),
                         bg="#1e1e1e",
                         fg="white")
        title.pack(pady=20)
        
        # Список пользователей
        users_list = tk.Listbox(users_window,
                               font=("Arial", 11),
                               bg="#2d2d2d",
                               fg="white",
                               selectbackground="#3498db")
        users_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Функция загрузки пользователей из БД
        def load_users():
            users_list.delete(0, tk.END)
            try:
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'autorization'))
                from autorization.registration import Database
                
                db = Database()
                with db.get_cursor() as cursor:
                    cursor.execute("SELECT username, is_admin FROM users")
                    users = cursor.fetchall()
                    
                    for user in users:
                        user_type = "👑 Администратор" if user['is_admin'] else "👤 Пользователь"
                        users_list.insert(tk.END, f"{user_type}: {user['username']}")
                        
            except Exception as e:
                # Fallback - тестовые пользователи
                users_list.insert(tk.END, "👑 Администратор: admin")
                users_list.insert(tk.END, "👤 Пользователь: user")
                users_list.insert(tk.END, "👤 Пользователь: user1")
                users_list.insert(tk.END, "👤 Пользователь: user2")
        
        # Загружаем пользователей
        load_users()
        
        # Функция удаления пользователя
        def delete_user(messagebox=None):
            selection = users_list.curselection()
            if not selection:
                messagebox.showwarning("Внимание", "Выберите пользователя для удаления")
                return
            
            user_text = users_list.get(selection[0])
            username = user_text.split(": ")[1]  # Извлекаем имя пользователя
            
            if username == "admin":
                messagebox.showerror("Ошибка", "Нельзя удалить администратора!")
                return
            
            if messagebox.askyesno("Подтверждение", f"Удалить пользователя '{username}'?"):
                try:
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'autorization'))
                    from autorization.registration import Database
                    
                    db = Database()
                    with db.get_cursor() as cursor:
                        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
                    
                    self.logger.log_admin_action("admin", "DELETE_USER", f"Deleted user: {username}")
                    messagebox.showinfo("Успех", f"Пользователь '{username}' удален")
                    load_users()  # Перезагружаем список
                    
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка удаления: {str(e)}")
        
        # Кнопки управления
        btn_frame = tk.Frame(users_window, bg="#1e1e1e")
        btn_frame.pack(pady=10)
        
        delete_btn = ttk.Button(btn_frame, 
                               text="Удалить пользователя", 
                               command=delete_user)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(btn_frame, 
                                text="Обновить", 
                                command=load_users)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка "Назад"
        back_btn = ttk.Button(btn_frame, 
                             text="Назад", 
                             command=on_closing)
        back_btn.pack(side=tk.LEFT, padx=5)

    def open_storage(self):
        """Открыть хранилище файлов"""
        # Логируем действие
        self.logger.log_admin_action("admin", "OPEN_ADMIN_STORAGE")
        
        # Закрываем панель администратора
        self.root.destroy()
        
        # Создаем новое окно хранилища
        storage_window = tk.Tk()
        storage_window.title("Хранилище администратора")
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
            # Возвращаемся к панели администратора
            from .admin_panel import open_admin_panel
            open_admin_panel()
        
        storage_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Создаем экземпляр хранилища с кнопкой назад
        storage_app = SimpleAdminStorage(storage_window, show_back_button=True, back_callback=on_closing)

    def view_logs(self):
        """Просмотр логов системы"""
        # Логируем действие
        self.logger.log_admin_action("admin", "VIEW_LOGS")
        
        # Создаем окно просмотра логов
        logs_window = tk.Toplevel(self.root)
        logs_window.title("Журнал системы")
        logs_window.geometry("800x600")
        logs_window.configure(bg="#1e1e1e")
        
        # Центрируем окно
        logs_window.update_idletasks()
        width = logs_window.winfo_width()
        height = logs_window.winfo_height()
        x = (logs_window.winfo_screenwidth() // 2) - (width // 2)
        y = (logs_window.winfo_screenheight() // 2) - (height // 2)
        logs_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Заголовок
        title = tk.Label(logs_window,
                         text="Журнал системы",
                         font=("Arial", 16, "bold"),
                         bg="#1e1e1e",
                         fg="white")
        title.pack(pady=20)
        
        # Фрейм для логов
        logs_frame = tk.Frame(logs_window, bg="#2d2d2d", relief=tk.SUNKEN, bd=2)
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Текстовое поле для логов
        logs_text = tk.Text(logs_frame,
                           font=("Consolas", 10),
                           bg="#1e1e1e",
                           fg="#00ff00",
                           wrap=tk.WORD,
                           state=tk.DISABLED)
        
        # Scrollbar для логов
        scrollbar = tk.Scrollbar(logs_frame, orient=tk.VERTICAL)
        logs_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=logs_text.yview)
        
        logs_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Загружаем логи
        logs = self.logger.get_recent_logs(100)
        logs_text.config(state=tk.NORMAL)
        for log in logs:
            logs_text.insert(tk.END, log)
        logs_text.config(state=tk.DISABLED)
        
        # Кнопки управления
        btn_frame = tk.Frame(logs_window, bg="#1e1e1e")
        btn_frame.pack(pady=10)
        
        def refresh_logs():
            logs_text.config(state=tk.NORMAL)
            logs_text.delete(1.0, tk.END)
            logs = self.logger.get_recent_logs(100)
            for log in logs:
                logs_text.insert(tk.END, log)
            logs_text.config(state=tk.DISABLED)
            logs_text.see(tk.END)
        
        def clear_logs():
            if tk.messagebox.askyesno("Подтверждение", "Очистить все логи?"):
                self.logger.clear_logs()
                refresh_logs()
        
        refresh_btn = ttk.Button(btn_frame, text="Обновить", command=refresh_logs)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(btn_frame, text="Очистить", command=clear_logs)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = ttk.Button(btn_frame, text="Закрыть", command=logs_window.destroy)
        close_btn.pack(side=tk.LEFT, padx=5)

    def logout(self):
        """Выход из системы"""
        # Логируем выход
        self.logger.log_user_logout("admin", "ADMIN")
        
        # Закрываем текущее окно
        self.root.destroy()
        # Импортируем здесь, чтобы избежать циклического импорта
        from .autorization import open_login_window
        # Открываем окно авторизации
        open_login_window()

    def run(self):
        """Запуск окна"""
        self.root.mainloop()

def open_admin_panel():
    """Функция для открытия панели администратора"""
    app = AdminPanel()
    app.run()

if __name__ == "__main__":
    open_admin_panel()
