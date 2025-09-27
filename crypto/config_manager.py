# config_manager.py
import os
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class ConfigManager:
    def __init__(self, config_file="config.enc", key_file="key.key"):
        self.config_file = config_file
        self.key_file = key_file
        self.credentials = None

    def generate_key(self, password: str, salt: bytes = None) -> tuple:
        """Генерирует ключ из пароля"""
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt

    def encrypt_data(self, data: str, password: str) -> bytes:
        """Шифрует данные"""
        key, salt = self.generate_key(password)
        fernet = Fernet(key)

        encrypted = fernet.encrypt(data.encode())
        return salt + encrypted  # Сохраняем salt с зашифрованными данными

    def decrypt_data(self, encrypted_data: bytes, password: str) -> str:
        """Расшифровывает данные"""
        salt = encrypted_data[:16]  # Первые 16 байт - salt
        encrypted = encrypted_data[16:]

        key, _ = self.generate_key(password, salt)
        fernet = Fernet(key)

        try:
            decrypted = fernet.decrypt(encrypted)
            return decrypted.decode()
        except Exception:
            raise ValueError("Неверный пароль для расшифровки")

    def create_config(self, username: str, password: str, config_password: str):
        """Создает зашифрованный конфигурационный файл"""
        config_data = {
            "username": username,
            "password": password
        }

        encrypted_data = self.encrypt_data(json.dumps(config_data), config_password)

        with open(self.config_file, 'wb') as f:
            f.write(encrypted_data)

        print("Конфигурационный файл создан успешно!")

    def load_config(self, config_password: str) -> dict:
        """Загружает и расшифровывает конфигурационный файл"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError("Конфигурационный файл не найден")

        with open(self.config_file, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = self.decrypt_data(encrypted_data, config_password)
        return json.loads(decrypted_data)

    def check_credentials(self, input_username: str, input_password: str, config_password: str) -> bool:
        """Проверяет введенные учетные данные"""
        try:
            config = self.load_config(config_password)
            return config["username"] == input_username and config["password"] == input_password
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            return False

    def config_exists(self) -> bool:
        """Проверяет существование конфигурационного файла"""
        return os.path.exists(self.config_file)


# Глобальный экземпляр менеджера конфигурации
config_manager = ConfigManager()