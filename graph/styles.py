from tkinter import ttk

def set_styles(root):
    style = ttk.Style()
    style.theme_use("clam")

    # Заголовки / подписи
    style.configure("TLabel",
                    background="#1e1e1e",
                    foreground="white",
                    font=("Arial", 11))

    # Поля ввода
    style.configure("TEntry",
                    fieldbackground="#2d2d2d",
                    foreground="white",
                    insertcolor="white",
                    padding=5)

    # Кнопки
    style.configure("TButton",
                    background="#3a3a3a",
                    foreground="white",
                    font=("Arial", 10, "bold"),
                    padding=6)

    style.map("TButton",
              background=[("active", "#505050")])
