
#pdf_extractor.py

from pypdf import PdfReader  # Для работы с физическими страницами PDF
import pdfplumber          # Для анализа структуры документа
from pathlib import Path   # Для работы с путями к файлам
import re
import os


class PDFParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse_pages(self):
        """
        Возвращает список словарей:
        [{'page_num': 1, 'text': '...', 'tables': [[...], [...]]}, ...]
        """
        pages_data = []

        if not os.path.exists(self.file_path):
            print(f"❌ Файл не найден: {self.file_path}")
            return pages_data

        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_info = {
                        'page_num': page_num,
                        'text': '',
                        'tables': []
                    }

                    # 1. Извлекаем обычный текст (для метаданных: дата, врач и т.д.)
                    try:
                        page_info['text'] = page.extract_text() or ""
                    except Exception:
                        page_info['text'] = ""

                    # 2. Извлекаем таблицы (это решит проблему с 'Результат')
                    # extract_tables() возвращает список таблиц, каждая таблица - список строк, каждая строка - список ячеек
                    try:
                        tables = page.extract_tables()
                        if tables:
                            page_info['tables'] = tables
                    except Exception as e:
                        print(f"⚠️ Не удалось извлечь таблицы на странице {page_num}: {e}")

                    pages_data.append(page_info)

        except Exception as e:
            print(f"❌ Критическая ошибка при открытии файла {self.file_path}: {e}")

        return pages_data
