#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главный файл приложения
Содержит только вызовы окон приложений
"""

from graph.autorization import open_login_window

def main():
    """Главная функция приложения"""
    print("Запуск приложения...")
    open_login_window()

if __name__ == "__main__":
    main()

