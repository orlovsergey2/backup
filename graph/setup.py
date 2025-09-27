# setup.py
import tkinter as tk
from tkinter import ttk, messagebox
from crypto.config_manager import config_manager
from .styles import set_styles

class SetupWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Первоначальная настройка системы")
        self.root.geometry("500x400")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        set_styles(self.root)
        self.center_window()
        self.create_widgets()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        title = tk.Label(self.root,
                         text="Первоначальная настройка",
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

        # Пароль для шифрования
        ttk.Label(frame, text="Пароль шифрования:").grid(row=2, column=0, sticky="e", padx=10, pady=10)
        self.encrypt_password_entry = ttk.Entry(frame, width=30, show="*")
        self.encrypt_password_entry.grid(row=2, column=1, pady=10)

        # Подтверждение пароля шифрования
        ttk.Label(frame, text="Подтвердите пароль:").grid(row=3, column=0, sticky="e", padx=10, pady=10)
        self.confirm_password_entry = ttk.Entry(frame, width=30, show="*")
        self.confirm_password_entry.grid(row=3, column=1, pady=10)

        btn_frame = tk.Frame(self.root, bg="#1e1e1e")
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Сохранить", command=self.save_config).pack(pady=10)

    def save_config(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        encrypt_password = self.encrypt_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not all([username, password, encrypt_password, confirm_password]):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        if encrypt_password != confirm_password:
            messagebox.showerror("Ошибка", "Пароли шифрования не совпадают!")
            return

        if len(encrypt_password) < 8:
            messagebox.showerror("Ошибка", "Пароль шифрования должен содержать минимум 8 символов!")
            return

        try:
            config_manager.create_config(username, password, encrypt_password)
            messagebox.showinfo("Успех", "Конфигурация сохранена успешно!\nТеперь вы можете войти в систему.")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении конфигурации: {e}")

    def run(self):
        self.root.mainloop()

def run_setup():
    app = SetupWindow()
    app.run()