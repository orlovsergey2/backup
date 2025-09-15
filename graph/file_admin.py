import tkinter as tk
from tkinter import messagebox, filedialog
import os
import shutil
import subprocess
import platform
import crypto.crypto_utils as crypto  # наш модуль


class SimpleAdminStorage:
    def __init__(self, root, show_back_button=False, back_callback=None):
        self.root = root
        self.root.title("Хранилище администратора")
        self.root.geometry("900x550")
        self.root.configure(bg="#f5f5f5")
        self.show_back_button = show_back_button
        self.back_callback = back_callback

        # доступные файлы
        self.public_dir = r"D:\save"
        os.makedirs(self.public_dir, exist_ok=True)

        # скрытые (зашифрованные) файлы храним в папке проекта
        self.hidden_dir = os.path.abspath(".")

        self.create_widgets()

    def create_widgets(self):
        main_container = tk.Frame(self.root, bg="#f5f5f5", padx=30, pady=30)
        main_container.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(main_container,
                         text="Хранилище администратора",
                         font=("Arial", 18, "bold"),
                         bg="#f5f5f5",
                         fg="#2c3e50")
        title.pack(pady=(0, 20))

        list_frame = tk.Frame(main_container, bg="white", relief=tk.SUNKEN, bd=2)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        self.file_listbox = tk.Listbox(list_frame,
                                       font=("Arial", 11),
                                       selectmode=tk.SINGLE,
                                       relief=tk.FLAT)
        self.load_file_info()

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)

        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        button_frame = tk.Frame(main_container, bg="#f5f5f5")
        button_frame.pack(pady=10)

        buttons = [
            ("Скачать", self.download),
            ("Открыть файл", self.open_file),
            ("Удалить", self.delete),
            ("Скрыть из общедоступных", self.hide),
            ("Сделать доступным", self.make_visible),
            ("Добавить файл", self.add_file)
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

    # ---------- Методы ----------
    def save_file_info(self, files):
        with open("admin_files.txt", "a", encoding="utf-8") as f:
            for file in files:
                f.write(f"{file}\n")

    def load_file_info(self):
        if os.path.exists("admin_files.txt"):
            with open("admin_files.txt", "r", encoding="utf-8") as f:
                for file in f:
                    if file.strip():
                        self.file_listbox.insert(tk.END, file.strip())

    def remove_file_info(self, file_info):
        if not os.path.exists("admin_files.txt"):
            return
        with open("admin_files.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open("admin_files.txt", "w", encoding="utf-8") as f:
            for line in lines:
                if line.strip() != file_info.strip():
                    f.write(line)

    def download(self):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        file_info = self.file_listbox.get(selection[0])
        messagebox.showinfo("Скачивание", f"Файл: {file_info}")

    def open_file(self):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        file_info = self.file_listbox.get(selection[0])
        if " -> " in file_info:
            file_path = file_info.split(" -> ")[1]
        else:
            file_path = file_info
        if os.path.exists(file_path):
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', file_path])
            else:
                subprocess.call(['xdg-open', file_path])

    def delete(self):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        file_info = self.file_listbox.get(selection[0])
        if messagebox.askyesno("Удаление", f"Удалить '{file_info}'?"):
            self.file_listbox.delete(selection[0])
            self.remove_file_info(file_info)

            if " -> " in file_info:
                file_path = file_info.split(" -> ")[1]
            else:
                file_path = file_info
            if os.path.exists(file_path):
                os.remove(file_path)

    def hide(self):
        """Шифруем файл и переносим его в папку проекта"""
        selection = self.file_listbox.curselection()
        if not selection:
            return
        file_info = self.file_listbox.get(selection[0])
        if " -> " not in file_info:
            return

        file_path = file_info.split(" -> ")[1]
        filename = os.path.basename(file_path)

        try:
            enc_path = crypto.encrypt_file(file_path, self.hidden_dir)

            if os.path.exists(file_path):
                os.remove(file_path)

            self.file_listbox.delete(selection[0])
            self.remove_file_info(file_info)

            with open("hidden_files.txt", "a", encoding="utf-8") as f:
                f.write(f"{enc_path}|{file_path}\n")

            messagebox.showinfo("Скрытие", f"Файл '{filename}' скрыт и зашифрован")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def make_visible(self):
        """Расшифровываем файл и возвращаем в исходное место"""
        if not os.path.exists("hidden_files.txt"):
            messagebox.showinfo("Инфо", "Нет скрытых файлов")
            return

        with open("hidden_files.txt", "r", encoding="utf-8") as f:
            hidden_files = f.readlines()

        if not hidden_files:
            messagebox.showinfo("Инфо", "Нет скрытых файлов")
            return

        entry = hidden_files[0].strip()
        enc_path, original_path = entry.split("|")

        try:
            crypto.decrypt_file(enc_path, original_path)

            if os.path.exists(enc_path):
                os.remove(enc_path)

            file_info = f"📄 {os.path.basename(original_path)} -> {original_path}"
            self.file_listbox.insert(tk.END, file_info)
            self.save_file_info([file_info])

            with open("hidden_files.txt", "w", encoding="utf-8") as f:
                for line in hidden_files[1:]:
                    f.write(line)

            messagebox.showinfo("Доступ", f"Файл снова доступен: {original_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def add_file(self):
        file_paths = filedialog.askopenfilenames(title="Выберите файлы")
        if file_paths:
            added = []
            for file_path in file_paths:
                filename = os.path.basename(file_path)
                destination = os.path.join(self.public_dir, filename)
                shutil.copy2(file_path, destination)
                file_info = f"📄 {filename} -> {destination}"
                self.file_listbox.insert(tk.END, file_info)
                added.append(file_info)
            self.save_file_info(added)


def main():
    root = tk.Tk()
    app = SimpleAdminStorage(root)
    root.mainloop()


if __name__ == "__main__":
    main()
