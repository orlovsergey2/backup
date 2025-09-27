import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import hashlib
from datetime import datetime
from .logger import get_logger  # Подключаем логгер
from crypto.crypto_utils import encrypt_file, decrypt_file


class BackupStorage:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Система резервного копирования")
        self.root.geometry("900x650")
        self.root.configure(bg="#1e1e1e")

        # Инициализируем логгер
        self.logger = get_logger()

        # Переменные для хранения путей
        self.source_path = tk.StringVar()
        self.backup_path = tk.StringVar()
        self.encryption_key = tk.StringVar()
        self.is_directory = tk.BooleanVar(value=True)  # True - папка, False - файл

        # Словарь для отслеживания хешей файлов
        self.file_hashes = {}

        self.setup_ui()

        # Логируем открытие хранилища
        self.logger.log_system_event("Backup storage opened")

    def setup_ui(self):
        # Заголовок
        title = tk.Label(self.root,
                         text="Система резервного копирования",
                         font=("Arial", 16, "bold"),
                         bg="#1e1e1e",
                         fg="white")
        title.pack(pady=20)

        # Фрейм для выбора типа источника
        type_frame = tk.Frame(self.root, bg="#1e1e1e")
        type_frame.pack(pady=10, padx=20, fill=tk.X)

        ttk.Label(type_frame, text="Тип источника:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Radiobutton(type_frame, text="Папка", variable=self.is_directory, value=True,
                        command=self.update_source_browse).grid(row=0, column=1, padx=5)
        ttk.Radiobutton(type_frame, text="Файл", variable=self.is_directory, value=False,
                        command=self.update_source_browse).grid(row=0, column=2, padx=5)

        # Фрейм для выбора путей
        path_frame = tk.Frame(self.root, bg="#1e1e1e")
        path_frame.pack(pady=10, padx=20, fill=tk.X)

        # Исходный путь (папка или файл)
        self.source_label = ttk.Label(path_frame, text="Исходная папка:")
        self.source_label.grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(path_frame, textvariable=self.source_path, width=50).grid(row=0, column=1, padx=5)
        self.browse_source_btn = ttk.Button(path_frame, text="Обзор", command=self.browse_source)
        self.browse_source_btn.grid(row=0, column=2, padx=5)

        # Резервная директория
        ttk.Label(path_frame, text="Резервная директория:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(path_frame, textvariable=self.backup_path, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(path_frame, text="Обзор", command=self.browse_backup).grid(row=1, column=2, padx=5)

        # Ключ шифрования (обязательный)
        ttk.Label(path_frame, text="Пароль шифрования*:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(path_frame, textvariable=self.encryption_key, width=50, show="*").grid(row=2, column=1, padx=5)

        # Фрейм для кнопок действий
        action_frame = tk.Frame(self.root, bg="#1e1e1e")
        action_frame.pack(pady=20)

        ttk.Button(action_frame, text="Создать резервную копию",
                   command=self.create_backup).pack(side=tk.LEFT, padx=10)
        ttk.Button(action_frame, text="Проверить изменения",
                   command=self.check_changes).pack(side=tk.LEFT, padx=10)
        ttk.Button(action_frame, text="Восстановить из резервной копии",
                   command=self.restore_backup).pack(side=tk.LEFT, padx=10)
        ttk.Button(action_frame, text="Сбросить настройки",
                   command=self.reset_settings).pack(side=tk.LEFT, padx=10)

        # Фрейм для лога операций
        log_frame = tk.Frame(self.root, bg="#2d2d2d")
        log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, height=15, bg="#1e1e1e", fg="white")
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопка выхода
        ttk.Button(self.root, text="Выход", command=self.root.quit).pack(pady=10)

    def update_source_browse(self):
        """Обновляет текст метки в зависимости от выбранного типа"""
        if self.is_directory.get():
            self.source_label.configure(text="Исходная папка:")
        else:
            self.source_label.configure(text="Исходный файл:")

    def browse_source(self):
        """Выбор источника (папки или файла)"""
        if self.is_directory.get():
            path = filedialog.askdirectory(title="Выберите исходную папку")
        else:
            path = filedialog.askopenfilename(title="Выберите исходный файл")

        if path:
            self.source_path.set(path)
            source_type = "папка" if self.is_directory.get() else "файл"
            self.log_operation(f"Выбран исходный {source_type}: {path}")

    def browse_backup(self):
        path = filedialog.askdirectory(title="Выберите резервную директорию")
        if path:
            self.backup_path.set(path)
            self.log_operation(f"Выбрана резервная директория: {path}")

    def calculate_file_hash(self, file_path):
        """Вычисляет хеш файла для отслеживания изменений"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.log_operation(f"Ошибка вычисления хеша {file_path}: {e}")
            return None

    def log_operation(self, message):
        """Добавляет запись в лог операций"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)

        # Логируем через логгер
        self.logger.log_system_event(message)

    def create_backup(self):
        """Оптимизированное создание резервной копии"""
        # Валидация входных данных
        if not self._validate_backup_inputs():
            return

        try:
            source_path = self.source_path.get()
            backup_dir = self.backup_path.get()
            key = self.encryption_key.get()

            # Выполняем резервное копирование
            backed_up_count = self._execute_backup(source_path, backup_dir, key)

            # Показываем результат
            self._show_backup_result(backed_up_count)

        except Exception as e:
            self._handle_backup_error(e)

    def _validate_backup_inputs(self):
        """Проверка корректности входных данных"""
        source_path = self.source_path.get()
        backup_dir = self.backup_path.get()
        key = self.encryption_key.get()

        errors = []

        if not source_path:
            errors.append("Укажите исходный путь!")
        elif not os.path.exists(source_path):
            errors.append(f"Указанный путь не существует: {source_path}")
        elif self.is_directory.get() and not os.path.isdir(source_path):
            errors.append("Указанный исходный путь не является папкой!")
        elif not self.is_directory.get() and not os.path.isfile(source_path):
            errors.append("Указанный исходный путь не является файлом!")

        if not backup_dir:
            errors.append("Укажите резервную директорию!")

        if not key:
            errors.append("Введите пароль шифрования!")

        if errors:
            error_msg = "\n".join(errors)
            messagebox.showerror("Ошибка", error_msg)
            self.logger.log_error("Backup Validation Error", "; ".join(errors))
            return False

        return True

    def _execute_backup(self, source_path, backup_dir, key):
        """Выполнение резервного копирования"""
        self.logger.log_system_event(f"Starting backup: {source_path} -> {backup_dir}")

        if self.is_directory.get():
            return self._backup_directory(source_path, backup_dir, key)
        else:
            return self._backup_single_file(source_path, backup_dir, key)

    def _backup_directory(self, source_dir, backup_dir, key):
        """Оптимизированное резервное копирование директории"""
        backed_up_count = 0
        # Создаем папку с именем файла (без расширения)
        filename = os.path.basename(source_dir)
        filename_without_ext = os.path.splitext(filename)[0]
        file_backup_dir = os.path.join(backup_dir, filename_without_ext)
        os.makedirs(file_backup_dir, exist_ok=True)

        for root, dirs, files in os.walk(source_dir):
            rel_path = os.path.relpath(root, source_dir)
            backup_subdir = os.path.join(backup_dir, rel_path)
            os.makedirs(backup_subdir, exist_ok=True)

            for file in files:
                source_file = os.path.join(root, file)
                encrypted_file = os.path.join(backup_subdir, file + '.enc')

                if self._process_file_backup(source_file, encrypted_file, key):
                    backed_up_count += 1

        self.log_operation(f"Резервное копирование директории завершено. Обработано файлов: {backed_up_count}")
        self.logger.log_system_event(f"Directory backup completed. Files: {backed_up_count}")

        return backed_up_count

    def _backup_single_file(self, source_file, backup_dir, key):
        """Оптимизированное резервное копирование отдельного файла с собственной папкой"""
        filename = os.path.basename(source_file)
        filename_without_ext = os.path.splitext(filename)[0]

        # Создаем папку с именем файла (без расширения)
        file_backup_dir = os.path.join(backup_dir, filename_without_ext)
        os.makedirs(file_backup_dir, exist_ok=True)

        # Шифрованный файл сохраняем в папке с именем файла
        encrypted_file = os.path.join(file_backup_dir, filename + '.enc')

        success = self._process_file_backup(source_file, encrypted_file, key)

        if success:
            self.log_operation(f"Файл зашифрован и сохранен в папке: {filename_without_ext}")
            return 1
        return 0

    def _process_file_backup(self, source_file, encrypted_file, key):
        """
        Универсальная обработка файла для резервного копирования
        Возвращает True если файл был обработан успешно
        """
        # Проверка изменений через хеш
        current_hash = self.calculate_file_hash(source_file)
        if source_file in self.file_hashes and self.file_hashes[source_file] == current_hash:
            return False  # Файл не изменился

        try:
            # Шифрование файла
            encrypt_file(source_file, encrypted_file, key)

            # Обновление хеша и логирование
            self.file_hashes[source_file] = current_hash
            filename = os.path.basename(source_file)

            self.logger.log_file_operation("System", "Backup", filename, True)
            return True

        except Exception as e:
            error_msg = f"Ошибка шифрования {os.path.basename(source_file)}: {e}"
            self.log_operation(error_msg)
            self.logger.log_file_operation("System", "Backup", os.path.basename(source_file), False)
            return False

    def _show_backup_result(self, backed_up_count):
        """Отображение результата резервного копирования"""
        if backed_up_count > 0:
            messagebox.showinfo("Успех", f"Резервное копирование завершено! Обработано файлов: {backed_up_count}")
            self.logger.log_system_event(f"Backup completed successfully. Files: {backed_up_count}")
        else:
            messagebox.showinfo("Инфо", "Не найдено новых или измененных файлов для резервного копирования")
            self.logger.log_system_event("No new or modified files found for backup")

    def _handle_backup_error(self, error):
        """Обработка ошибок резервного копирования"""
        error_msg = f"Ошибка при резервном копировании: {error}"
        messagebox.showerror("Ошибка", error_msg)
        self.logger.log_error("Backup Execution Error", str(error))

    def check_changes(self):
        """Проверяет изменения в исходных файлах"""
        source = self.source_path.get()
        if not source:
            messagebox.showerror("Ошибка", "Выберите исходный путь!")
            self.logger.log_error("Check Changes Error", "Source path not selected")
            return

        changed_files = []
        try:
            self.logger.log_system_event(f"Checking for changes in: {source}")

            if self.is_directory.get():
                if not os.path.isdir(source):
                    messagebox.showerror("Ошибка", "Указанный путь не является папкой!")
                    self.logger.log_error("Check Changes Error", f"Path is not a directory: {source}")
                    return
                for root, dirs, files in os.walk(source):
                    for file in files:
                        file_path = os.path.join(root, file)
                        self._check_file_changes(file_path, changed_files)
            else:
                if not os.path.isfile(source):
                    messagebox.showerror("Ошибка", "Указанный путь не является файлом!")
                    self.logger.log_error("Check Changes Error", f"Path is not a file: {source}")
                    return
                self._check_file_changes(source, changed_files)

            if changed_files:
                self.log_operation(f"Обнаружены изменения в файлах: {', '.join(changed_files)}")
                messagebox.showinfo("Проверка изменений", f"Обнаружены изменения в {len(changed_files)} файлах")
                self.logger.log_system_event(f"Changes detected in {len(changed_files)} files")
            else:
                self.log_operation("Изменений не обнаружено")
                messagebox.showinfo("Проверка изменений", "Изменений не обнаружено")
                self.logger.log_system_event("No changes detected")

        except Exception as e:
            error_msg = f"Ошибка при проверке изменений: {e}"
            messagebox.showerror("Ошибка", error_msg)
            self.logger.log_error("Check Changes Error", str(e))

    def _check_file_changes(self, file_path, changed_files):
        """Проверяет изменения в отдельном файле"""
        current_hash = self.calculate_file_hash(file_path)
        filename = os.path.basename(file_path)

        if file_path in self.file_hashes:
            if self.file_hashes[file_path] != current_hash:
                changed_files.append(filename)
        else:
            changed_files.append(filename)

    def restore_backup(self):
        """Расшифровывает файлы из резервной копии и восстанавливает в указанное место"""
        backup_dir = self.backup_path.get()
        key = self.encryption_key.get()

        if not backup_dir:
            messagebox.showerror("Ошибка", "Укажите резервную директорию!")
            self.logger.log_error("Restore Error", "Backup directory not specified")
            return

        restore_path = filedialog.askdirectory(title="Выберите папку для восстановления")
        if not restore_path:
            return

        if not key:
            messagebox.showerror("Ошибка", "Введите пароль шифрования!")
            self.logger.log_error("Restore Error", "Encryption key not provided")
            return

        try:
            restored_count = 0
            self.logger.log_system_event(f"Starting restore: {backup_dir} -> {restore_path}")

            # Восстанавливаем всю резервную директорию
            if os.path.isdir(backup_dir):
                for root, dirs, files in os.walk(backup_dir):
                    rel_path = os.path.relpath(root, backup_dir)
                    restore_subdir = os.path.join(restore_path, rel_path)
                    os.makedirs(restore_subdir, exist_ok=True)

                    for file in files:
                        if file.endswith('.enc'):
                            encrypted_file = os.path.join(root, file)
                            original_filename = file[:-4]  # Убираем .enc
                            restored_file = os.path.join(restore_subdir, original_filename)

                            try:
                                decrypt_file(encrypted_file, restored_file, key)
                                restored_count += 1
                                self.log_operation(f"Восстановлен: {original_filename}")
                                self.logger.log_file_operation("System", "Restore", original_filename, True)
                            except Exception as e:
                                error_msg = f"Ошибка восстановления {file}: {e}"
                                self.log_operation(error_msg)
                                self.logger.log_file_operation("System", "Restore", original_filename, False)
                                continue

            # Восстанавливаем отдельный зашифрованный файл
            elif os.path.isfile(backup_dir) and backup_dir.endswith('.enc'):
                original_filename = os.path.basename(backup_dir)[:-4]
                restored_file = os.path.join(restore_path, original_filename)

                decrypt_file(backup_dir, restored_file, key)
                restored_count = 1
                self.log_operation(f"Восстановлен: {original_filename}")
                self.logger.log_file_operation("System", "Restore", original_filename, True)

            if restored_count > 0:
                messagebox.showinfo("Успех", f"Восстановление завершено! Восстановлено файлов: {restored_count}")
                self.log_operation(f"Восстановление завершено. Файлов: {restored_count}")
                self.logger.log_system_event(f"Restore completed. Files restored: {restored_count}")
            else:
                messagebox.showinfo("Инфо", "Не найдено файлов для восстановления")
                self.log_operation("Не найдено зашифрованных файлов для восстановления")
                self.logger.log_system_event("No encrypted files found for restore")

        except Exception as e:
            error_msg = f"Ошибка при восстановлении: {e}"
            messagebox.showerror("Ошибка", error_msg)
            self.log_operation(error_msg)
            self.logger.log_error("Restore Error", str(e))

    def reset_settings(self):
        """Сброс всех настроек и полей"""
        self.source_path.set("")
        self.backup_path.set("")
        self.encryption_key.set("")
        self.file_hashes.clear()
        self.log_text.delete(1.0, tk.END)
        self.log_operation("Настройки сброшены")
        messagebox.showinfo("Сброс", "Все настройки успешно сброшены!")
        self.logger.log_system_event("Settings reset")

    def run(self):
        """Запуск окна"""
        self.root.mainloop()


def open_backup_storage():
    """Функция для открытия окна резервного хранилища"""
    app = BackupStorage()
    app.run()


if __name__ == "__main__":
    open_backup_storage()