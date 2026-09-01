#utils.py

import os
from pathlib import Path


def ensure_dir_exists(folder):
    #Создаёт директорию, если её нет
    if isinstance(folder, str):  # Если передали простую строку
        folder = Path(folder)

    # Проверяем, является ли объект действительно папкой, а не файлом
    if not folder.is_dir():
        raise ValueError("Передан неверный аргумент. Ожидается путь к папке.")

    # Создаём всю цепочку папок, если они отсутствуют
    folder.mkdir(parents=True, exist_ok=True)  # Теперь эта строка безопасна

def get_pdf_files_from_config(input_folder):
    #Возвращает список всех PDF-файлов из заданной директории
    return list(Path(input_folder).glob("*.pdf"))
"""
import os
from pathlib import Path

def get_pdf_files_from_config(input_folder):
    # Приводим к Path и нормализуем путь
    folder = Path(input_folder).resolve()

    if not folder.exists():
        print(f"❌ Папка не существует: {folder}")
        return []

    if not folder.is_dir():
        print(f"❌ Путь не является папкой: {folder}")
        return []

    print(f"📂 Ищем PDF в: {folder}")

    pdf_files = []
    # Рекурсивный поиск по всем подпапкам
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith('.pdf'):
                full_path = Path(root) / f
                pdf_files.append(full_path)
                print(f"  ✅ Найден: {full_path.name}")

    print(f"📄 Всего найдено PDF-файлов: {len(pdf_files)}")
    return pdf_files
"""
