import logging
import os
from datetime import datetime
from typing import Optional

class AppLogger:
    """Класс для ведения журнала приложения"""
    
    def __init__(self, log_file: str = "logs/app.log"):
        self.log_file = log_file
        self.setup_logger()
    
    def setup_logger(self):
        """Настройка логгера"""
        # Создаем папку для логов если её нет
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Настраиваем логгер
        self.logger = logging.getLogger('AppLogger')
        self.logger.setLevel(logging.INFO)
        
        # Очищаем существующие обработчики
        self.logger.handlers.clear()
        
        # Создаем форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Обработчик для файла
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Обработчик для консоли
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Добавляем обработчики
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_auth_attempt(self, username: str, success: bool, ip: str = "localhost"):
        """Логирование попытки авторизации"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"AUTH_ATTEMPT - User: {username}, Status: {status}, IP: {ip}")
    
    def log_user_login(self, username: str, user_type: str, ip: str = "localhost"):
        """Логирование успешного входа пользователя"""
        self.logger.info(f"USER_LOGIN - User: {username}, Type: {user_type}, IP: {ip}")
    
    def log_user_logout(self, username: str, user_type: str, ip: str = "localhost"):
        """Логирование выхода пользователя"""
        self.logger.info(f"USER_LOGOUT - User: {username}, Type: {user_type}, IP: {ip}")
    
    def log_registration(self, username: str, success: bool, ip: str = "localhost"):
        """Логирование регистрации пользователя"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"REGISTRATION - User: {username}, Status: {status}, IP: {ip}")
    
    def log_admin_action(self, admin_username: str, action: str, details: str = "", ip: str = "localhost"):
        """Логирование действий администратора"""
        self.logger.info(f"ADMIN_ACTION - Admin: {admin_username}, Action: {action}, Details: {details}, IP: {ip}")
    
    def log_user_action(self, username: str, action: str, details: str = "", ip: str = "localhost"):
        """Логирование действий пользователя"""
        self.logger.info(f"USER_ACTION - User: {username}, Action: {action}, Details: {details}, IP: {ip}")
    
    def log_file_operation(self, username: str, operation: str, filename: str, success: bool, ip: str = "localhost"):
        """Логирование операций с файлами"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"FILE_OPERATION - User: {username}, Operation: {operation}, File: {filename}, Status: {status}, IP: {ip}")
    
    def log_error(self, error_type: str, error_message: str, username: str = "SYSTEM", ip: str = "localhost"):
        """Логирование ошибок"""
        self.logger.error(f"ERROR - Type: {error_type}, Message: {error_message}, User: {username}, IP: {ip}")
    
    def log_system_event(self, event: str, details: str = "", ip: str = "localhost"):
        """Логирование системных событий"""
        self.logger.info(f"SYSTEM_EVENT - Event: {event}, Details: {details}, IP: {ip}")
    
    def get_recent_logs(self, lines: int = 50) -> list:
        """Получение последних записей лога"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except FileNotFoundError:
            return ["Лог файл не найден"]
        except Exception as e:
            return [f"Ошибка чтения лога: {str(e)}"]
    
    def clear_logs(self):
        """Очистка логов"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("")
            self.logger.info("SYSTEM_EVENT - Logs cleared")
        except Exception as e:
            self.logger.error(f"ERROR - Failed to clear logs: {str(e)}")

# Глобальный экземпляр логгера
app_logger = AppLogger()

def get_logger() -> AppLogger:
    """Получение экземпляра логгера"""
    return app_logger

