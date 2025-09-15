import tkinter as tk
from tkinter import messagebox
import os
import crypto.crypto_utils as crypto


class HiddenFilesWindow:
    def __init__(self, master, admin_app):
        self.master = master
        self.admin_app = admin_app
        self.master.title("Скрытые файлы")
        self.master.geometry("600x400")
        self.master.configure(bg="#f5f5f5")

        self.listbox = tk.Listbox(self.master,
                                  font=("Arial", 11),
                                  selectmode=tk.SINGLE,
                                  relief=tk.FLAT)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self.master, bg="#f5f5f5")
        btn_frame.pack(pady=10)

        restore_btn = tk.Button(btn_frame,
                                text="Восстановить",
                                command=self.restore_file,
                                bg="#2ecc71", fg="white", font=("Arial", 10))
        restore_btn.pack(side=tk.LEFT, padx=5)

        delete_btn = tk.Button(btn_frame,
                               text="Удалить",
                               command=self.delete_file,
                               bg="#e74c3c", fg="white", font=("Arial", 10))
        delete_btn.pack(side=tk.LEFT, padx=5)

        self.load_hidden_files()

    def load_hidden_files(self):
        self.listbox.delete(0, tk.END)
        if not os.path.exists("hidden_files.txt"):
            return
        with open("hidden_files.txt", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    enc_path, original_path = line.strip().split("|")
                    self.listbox.insert(tk.END, f"{os.path.basename(original_path)} -> {original_path}")

    def restore_file(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        selected_text = self.listbox.get(selection[0])

        with open("hidden_files.txt", "r", encoding="utf-8") as f:
            hidden_files = f.readlines()

        for line in hidden_files:
            enc_path, original_path = line.strip().split("|")
            if original_path in selected_text:
                try:
                    crypto.decrypt_file(enc_path, original_path)

                    if os.path.exists(enc_path):
                        os.remove(enc_path)

                    # Добавляем в список админского окна
                    file_info = f"📄 {os.path.basename(original_path)} -> {original_path}"
                    self.admin_app.file_listbox.insert(tk.END, file_info)
                    self.admin_app.save_file_info([file_info])

                    # Убираем из списка скрытых
                    with open("hidden_files.txt", "w", encoding="utf-8") as f2:
                        for l in hidden_files:
                            if l.strip() != line.strip():
                                f2.write(l)

                    messagebox.showinfo("Восстановление", f"Файл восстановлен: {original_path}")
                    self.load_hidden_files()
                    return
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))
                    return

    def delete_file(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        selected_text = self.listbox.get(selection[0])

        with open("hidden_files.txt", "r", encoding="utf-8") as f:
            hidden_files = f.readlines()

        for line in hidden_files:
            enc_path, original_path = line.strip().split("|")
            if original_path in selected_text:
                if messagebox.askyesno("Удаление", f"Удалить '{original_path}' окончательно?"):
                    if os.path.exists(enc_path):
                        os.remove(enc_path)

                    with open("hidden_files.txt", "w", encoding="utf-8") as f2:
                        for l in hidden_files:
                            if l.strip() != line.strip():
                                f2.write(l)

                    messagebox.showinfo("Удаление", f"Файл '{original_path}' удалён")
                    self.load_hidden_files()
                return
