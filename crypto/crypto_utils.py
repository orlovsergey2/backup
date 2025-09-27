import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Файл, где хранится ключ
KEY_FILE = "key.bin"


def generate_key_from_password(password: str, salt: bytes = None) -> tuple:
    """Генерирует ключ из пароля (совместимость с ConfigManager)"""
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


def load_or_generate_key():
    """
    Загружает ключ из файла KEY_FILE,
    либо генерирует новый, если его нет.
    """
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            key = f.read()
        if len(key) != 32:
            raise ValueError("Неверный ключ в key.bin (должно быть 32 байта)")
        return key
    else:
        key = get_random_bytes(32)  # 256 бит
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key


# Загружаем или генерируем ключ при старте
SECRET_KEY = load_or_generate_key()


def encrypt_file(file_path, output_path, password=None):
    """
    Шифрует файл AES-256 (CBC).
    Если указан пароль - использует Fernet шифрование (совместимость с ConfigManager)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if password:
        # Используем Fernet шифрование с паролем
        key, salt = generate_key_from_password(password)
        fernet = Fernet(key)

        with open(file_path, "rb") as f:
            plaintext = f.read()

        encrypted = fernet.encrypt(plaintext)

        # Сохраняем salt + зашифрованные данные
        with open(output_path, "wb") as f:
            f.write(salt + encrypted)
    else:
        # Используем AES шифрование с фиксированным ключом
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC)
        iv = cipher.iv

        with open(file_path, "rb") as f:
            plaintext = f.read()

        ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))

        with open(output_path, "wb") as f:
            f.write(iv + ciphertext)

    return output_path


def decrypt_file(enc_path, output_path, password=None):
    """
    Расшифровывает файл.
    Если указан пароль - использует Fernet дешифрование
    """
    if not os.path.exists(enc_path):
        raise FileNotFoundError(f"Файл не найден: {enc_path}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(enc_path, "rb") as f:
        data = f.read()

    if password:
        # Fernet дешифрование
        salt = data[:16]
        encrypted = data[16:]

        key, _ = generate_key_from_password(password, salt)
        fernet = Fernet(key)

        try:
            decrypted = fernet.decrypt(encrypted)
            with open(output_path, "wb") as f:
                f.write(decrypted)
        except Exception:
            raise ValueError("Неверный пароль для расшифровки")
    else:
        # AES дешифрование
        iv = data[:16]
        ciphertext = data[16:]

        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv=iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

        with open(output_path, "wb") as f:
            f.write(plaintext)

    return output_path


def is_encrypted(file_path):
    """
    Проверяет, имеет ли файл расширение .enc
    """
    return file_path.endswith(".enc")


def detect_encryption_type(file_path):
    """
    Определяет тип шифрования файла
    """
    if not is_encrypted(file_path):
        return "none"

    with open(file_path, "rb") as f:
        data = f.read(32)  # Читаем первые 32 байта для анализа

    # Fernet файлы начинаются с salt (16 байт)
    # AES файлы начинаются с IV (16 байт)
    # Пока не можем точно определить, возвращаем оба варианта
    return "fernet_or_aes"