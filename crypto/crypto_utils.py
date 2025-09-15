import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# Файл, где хранится ключ
KEY_FILE = "key.bin"


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


def encrypt_file(file_path, output_dir):
    """
    Шифрует файл AES-256 (CBC).
    Сохраняет зашифрованный файл с расширением .enc в output_dir.
    Возвращает путь к зашифрованному файлу.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.basename(file_path)
    encrypted_path = os.path.join(output_dir, filename + ".enc")

    cipher = AES.new(SECRET_KEY, AES.MODE_CBC)
    iv = cipher.iv  # вектор инициализации

    with open(file_path, "rb") as f:
        plaintext = f.read()

    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))

    with open(encrypted_path, "wb") as f:
        f.write(iv + ciphertext)

    return encrypted_path


def decrypt_file(enc_path, output_path):
    """
    Расшифровывает файл AES-256 (CBC).
    enc_path — путь к .enc файлу
    output_path — куда сохранять расшифрованный файл
    """
    if not os.path.exists(enc_path):
        raise FileNotFoundError(f"Файл не найден: {enc_path}")

    with open(enc_path, "rb") as f:
        data = f.read()

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
