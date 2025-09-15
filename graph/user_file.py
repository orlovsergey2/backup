import tkinter as tk
from tkinter import ttk, messagebox

from .logger import get_logger
from .styles import set_styles
class UserStorage:
    def __init__(self, root, username, show_back_button=False, back_callback=None):
        self.root = root
        self.username = username
        self.root.title(f"Хранилище пользователя - {username}")
        self.root.geometry("700x500")
        self.root.configure(bg="#f5f5f5")
        self.show_back_button = show_back_button
        self.back_callback = back_callback

        # Инициализируем логгер
        self.logger = get_logger()
        set_styles(self.root)
        self.create_widgets()

    def create_widgets(self):
        # Основной контейнер
        main_container = tk.Frame(self.root, bg="#f5f5f5", padx=30, pady=30)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        title = tk.Label(main_container,
                         text=f"Мое хранилище - {self.username}",
                         font=("Arial", 18, "bold"),
                         bg="#f5f5f5",
                         fg="#2c3e50")
        title.pack(pady=(0, 20))

        # Описание
        description = tk.Label(main_container,
                               text="Здесь ваши личные файлы и папки.\n"
                                    "Вы можете скачивать, загружать и управлять\n"
                                    "своими файлами.",
                               font=("Arial", 12),
                               bg="#f5f5f5",
                               fg="#34495e",
                               justify=tk.LEFT)
        description.pack(pady=(0, 20))

        # Список файлов
        list_frame = tk.Frame(main_container, bg="white", relief=tk.SUNKEN, bd=2)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Создаем список
        self.file_listbox = tk.Listbox(list_frame,
                                       font=("Arial", 11),
                                       selectmode=tk.SINGLE,
                                       relief=tk.FLAT)

        # Загружаем сохраненные файлы пользователя
        self.load_file_info()

        # Scrollbar для списка
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)

        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки действий
        button_frame = tk.Frame(main_container, bg="#f5f5f5")
        button_frame.pack(pady=10)

        # Создаем кнопки для пользователя (убераем "Сделать общими")
        buttons = [
            ("Скачать", self.download),
            ("Открыть файл", self.open_file),
            ("Загрузить", self.upload),
            ("Удалить", self.delete),
            ("Переименовать", self.rename),
        ]

        for text, command in buttons:
            btn = tk.Button(button_frame,
                            text=text,
                            command=command,
                            bg="#3498db",
                            fg="white",
                            font=("Arial", 10),
                            padx=12,
                            pady=6,
                            relief=tk.RAISED,
                            bd=2)
            btn.pack(side=tk.LEFT, padx=5)

        # Добавляем кнопку "Назад" если нужно
        if self.show_back_button and self.back_callback:
            back_btn = tk.Button(button_frame,
                                 text="Назад",
                                 command=self.back_callback,
                                 bg="#e74c3c",
                                 fg="white",
                                 font=("Arial", 10, "bold"),
                                 padx=12,
                                 pady=6,
                                 relief=tk.RAISED,
                                 bd=2)
            back_btn.pack(side=tk.RIGHT, padx=5)

    def download(self):
        """Обработчик кнопки Скачать"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите файл для скачивания")
            return

        file_info = self.file_listbox.get(selection[0])

        # Извлекаем путь к файлу
        if " -> " in file_info:
            file_path = file_info.split(" -> ")[1]
            filename = file_info.split(" -> ")[0].split(" ", 1)[1]  # Убираем иконку
        else:
            file_path = file_info
            filename = file_info

        # Проверяем существование файла
        import os
        if os.path.exists(file_path):
            self.logger.log_file_operation(self.username, "DOWNLOAD", filename, True)
            messagebox.showinfo("Скачивание", f"Файл найден: {file_path}")
            # Здесь можно добавить реальное скачивание
        else:
            messagebox.showerror("Ошибка", f"Файл не найден: {file_path}")

    def open_file(self):
        """Открыть выбранный файл"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите файл для открытия")
            return

        file_info = self.file_listbox.get(selection[0])

        # Извлекаем путь к файлу
        if " -> " in file_info:
            file_path = file_info.split(" -> ")[1]
            filename = file_info.split(" -> ")[0].split(" ", 1)[1]  # Убираем иконку
        else:
            file_path = file_info
            filename = file_info

        # Проверяем существование файла и открываем его
        import os
        import subprocess
        import platform

        if os.path.exists(file_path):
            try:
                if platform.system() == 'Windows':
                    os.startfile(file_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(['open', file_path])
                else:  # Linux
                    subprocess.call(['xdg-open', file_path])
                self.logger.log_file_operation(self.username, "OPEN_FILE", filename, True)
                messagebox.showinfo("Успех", f"Файл открыт: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")
        else:
            messagebox.showerror("Ошибка", f"Файл не найден: {file_path}")

    def upload(self):
        """Обработчик кнопки Загрузить"""
        from tkinter import filedialog, simpledialog

        # Открываем диалог выбора файлов/папок
        file_paths = filedialog.askopenfilenames(
            title="Выберите файлы для загрузки",
            filetypes=[
                ("Все файлы", "*.*"),
                ("Документы", "*.pdf;*.doc;*.docx;*.txt"),
                ("Изображения", "*.jpg;*.jpeg;*.png;*.gif"),
                ("Архивы", "*.zip;*.rar;*.7z"),
                ("Видео", "*.mp4;*.avi;*.mkv"),
                ("Аудио", "*.mp3;*.wav;*.flac")
            ]
        )

        if file_paths:
            # Спрашиваем путь сохранения
            save_path = simpledialog.askstring(
                "Путь сохранения",
                "Введите путь для сохранения файлов (или оставьте пустым для текущей папки):",
                initialvalue=""
            )

            if save_path is None:  # Пользователь отменил
                return

            if not save_path:
                save_path = "."  # Текущая папка

            # Создаем папку если её нет
            import os
            try:
                os.makedirs(save_path, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать папку: {str(e)}")
                return

            added_files = []
            for file_path in file_paths:
                filename = os.path.basename(file_path)
                destination = os.path.join(save_path, filename)

                try:
                    # Копируем файл
                    import shutil
                    shutil.copy2(file_path, destination)

                    # Определяем иконку по расширению
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in ['.pdf']:
                        icon = "📄"
                    elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
                        icon = "🖼️"
                    elif ext in ['.mp4', '.avi', '.mkv']:
                        icon = "🎥"
                    elif ext in ['.mp3', '.wav', '.flac']:
                        icon = "🎵"
                    elif ext in ['.zip', '.rar', '.7z']:
                        icon = "📦"
                    elif ext in ['.doc', '.docx']:
                        icon = "📝"
                    elif ext in ['.xls', '.xlsx']:
                        icon = "📊"
                    else:
                        icon = "📄"

                    # Добавляем файл в список с путем
                    file_info = f"{icon} {filename} -> {destination}"
                    self.file_listbox.insert(tk.END, file_info)
                    added_files.append(file_info)
                    self.logger.log_file_operation(self.username, "UPLOAD", filename, True)

                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось скопировать {filename}: {str(e)}")

            # Сохраняем информацию о файлах в файл
            self.save_file_info(added_files)

            messagebox.showinfo("Успех", f"Загружено файлов: {len(added_files)}")
        else:
            messagebox.showinfo("Информация", "Файлы не выбраны")

    def save_file_info(self, files):
        """Сохраняет информацию о файлах пользователя в файл"""
        try:
            filename = f"{self.username}_files.txt"
            with open(filename, "a", encoding="utf-8") as f:
                for file in files:
                    f.write(f"{file}\n")
        except Exception as e:
            print(f"Ошибка сохранения информации о файлах: {e}")

    def load_file_info(self):
        """Загружает информацию о файлах пользователя из файл"""
        try:
            filename = f"{self.username}_files.txt"
            with open(filename, "r", encoding="utf-8") as f:
                files = f.readlines()
                for file in files:
                    if file.strip():
                        self.file_listbox.insert(tk.END, file.strip())
        except FileNotFoundError:
            pass  # Файл не существует, это нормально
        except Exception as e:
            print(f"Ошибка загрузки информации о файлах: {e}")

    def delete(self):
        """Обработчик кнопки Удалить"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите файл для удаления")
            return

        file = self.file_listbox.get(selection[0])
        if messagebox.askyesno("Удаление", f"Удалить файл '{file}'?"):
            self.file_listbox.delete(selection[0])
            self.logger.log_file_operation(self.username, "DELETE", file, True)
            messagebox.showinfo("Успех", f"Файл '{file}' удален")

    def rename(self):
        """Обработчик кнопки Переименовать"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите файл для переименования")
            return

        file = self.file_listbox.get(selection[0])
        new_name = tk.simpledialog.askstring("Переименование", f"Введите новое имя для '{file}':")
        if new_name:
            self.file_listbox.delete(selection[0])
            self.file_listbox.insert(selection[0], new_name)
            self.logger.log_file_operation(self.username, "RENAME", f"{file} -> {new_name}", True)
            messagebox.showinfo("Успех", f"Файл переименован в '{new_name}'")
def main():
    root = tk.Tk()
    app = UserStorage(root)
    root.mainloop()


if __name__ == "__main__":
    main()