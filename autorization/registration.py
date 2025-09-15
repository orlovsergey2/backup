# registration.py
import mysql.connector
from mysql.connector import Error
import bcrypt
from typing import Tuple, Optional, Dict
from contextlib import contextmanager


class Database:
    def __init__(self):
        self.config = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "myuser",
            "password": "mypassword",
            "database": "registration"
        }
        self.connection = None

    @contextmanager
    def get_cursor(self):
        """Контекстный менеджер для работы с курсором"""
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)
            yield cursor
            conn.commit()
        except Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def create_database(self):
        """Создает базу данных и таблицы"""
        try:
            # Подключаемся без указания базы данных
            with mysql.connector.connect(
                    host=self.config["host"],
                    port=self.config["port"],
                    user=self.config["user"],
                    password=self.config["password"]
            ) as temp_conn:
                with temp_conn.cursor() as cursor:
                    # Создаем базу данных если не существует
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")

                    # Создаем таблицу пользователей
                    cursor.execute(f"""
                        CREATE TABLE IF NOT EXISTS {self.config['database']}.users (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            username VARCHAR(255) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            is_admin BOOLEAN DEFAULT FALSE
                        )
                    """)

                    # Добавляем администратора по умолчанию
                    admin_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cursor.execute(f"""
                        INSERT IGNORE INTO {self.config['database']}.users 
                        (username, password_hash, is_admin)
                        VALUES ('admin', %s, TRUE)
                    """, (admin_hash,))

                    temp_conn.commit()
            return True
        except Error as e:
            print(f"Ошибка создания базы данных: {e}")
            return False

    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Регистрирует нового пользователя"""
        if len(password) < 8:
            return False, "Пароль должен содержать минимум 8 символов"

        try:
            with self.get_cursor() as cursor:
                # Проверяем существование пользователя
                cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    return False, "Пользователь уже существует"

                # Хешируем пароль и добавляем пользователя
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                    (username, password_hash)
                )
            return True, "Пользователь успешно зарегистрирован"
        except Error as e:
            return False, f"Ошибка регистрации: {str(e)}"

    def check_credentials(self, username: str, password: str) -> Tuple[bool, str, bool]:
        """Проверяет учетные данные пользователя"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "SELECT password_hash, is_admin FROM users WHERE username = %s",
                    (username,)
                )
                user = cursor.fetchone()

                if not user:
                    return False, "Пользователь не найден", False

                if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                    return True, "Аутентификация успешна", user['is_admin']
                return False, "Неверный пароль", False
        except Error as e:
            return False, f"Ошибка аутентификации: {str(e)}", False


if __name__ == "__main__":
    db = Database()
    db.create_database()