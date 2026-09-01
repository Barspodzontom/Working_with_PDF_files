import re
from datetime import datetime
import json
from pathlib import Path

from modules.pdf_extractor import PDFParser
from modules.lab_results_parser import parse_lab_result_table
from modules.excel_exporter import save_to_excel
from modules.utils import get_pdf_files_from_config


def extract_date_from_filename(filename):
    """
    Извлекает дату в формате YYYY-MM-DD из имени файла.
    Пример: LaboratoryResearch-2026-08-18 (14).pdf -> 2026-08-18
    """
    match = re.search(r'\d{4}-\d{2}-\d{2}', filename)
    return match.group() if match else filename


if __name__ == "__main__":
    try:
        with open("config.json", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Файл config.json не найден!")
        exit(1)

    files = get_pdf_files_from_config(config["input_folder"])
    print(f"Найдено PDF-файлов: {len(files)}")

    all_rows = []
    unique_rows = set()

    for file_path in files:
        print(f"📄 Обрабатываем файл: {file_path}")

        try:
            parser = PDFParser(file_path)
            pages_data = parser.parse_pages()

            if not pages_data:
                print(f"⚠️ В файле {file_path} не найдено данных.")
                continue

            doc_date = extract_date_from_filename(Path(file_path).name)

            # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
            # Раньше был цикл: for table in tables: parse_lab_result_table({'tables': [table]})
            # Теперь передаем всю страницу (список таблиц) сразу.
            # parse_lab_result_table сам пройдет по всем таблицам на странице.

            parsed_data = parse_lab_result_table({'tables': [p.get('tables', []) for p in pages_data]})
            # ^^^ Внимание: структура данных зависит от того, что возвращает parser.parse_pages()

            # ВАЖНО: Если parser.parse_pages() возвращает список словарей, где у каждого есть ключ 'tables',
            # то правильный вызов будет таким (см. ниже), чтобы не ломать структуру:

            # Правильный вариант для вашей текущей структуры pages_data:
            # Мы передаем список всех таблиц со всех страниц сразу, либо обрабатываем страницу за страницей.
            # Самый надежный способ - собрать все таблицы в один список и передать их.

            all_tables_on_page = []
            for page_info in pages_data:
                tables = page_info.get('tables', [])
                all_tables_on_page.extend(tables)

            # Передаем все таблицы одной страницы (или всего файла) в парсер
            parsed_data = parse_lab_result_table({'tables': all_tables_on_page})

            for row in parsed_data:
                raw_indicator = (row.get("Показатель") or "").strip()
                raw_value = (row.get("Значение") or "").strip()
                raw_norm = (row.get("Норма") or "").strip()
                raw_comment = (row.get("Комментарий") or "").strip()

                if not raw_indicator:
                    continue

                # Логика исправления сдвига (осталась без изменений)
                final_value = ""
                final_norm = ""
                final_comment = raw_comment

                has_digits_in_value = bool(re.search(r'\d', raw_value))
                has_digits_in_norm = bool(re.search(r'\d', raw_norm))

                if not has_digits_in_value and has_digits_in_norm:
                    final_value = raw_norm
                    final_norm = ""
                    print(f"   🔧 Сдвиг: '{raw_indicator}' -> значение из Нормы.")
                elif has_digits_in_value:
                    final_value = raw_value
                    final_norm = raw_norm
                else:
                    final_value = ""
                    final_norm = raw_norm

                # Защита от дублей
                row_key = (doc_date, raw_indicator, final_value, final_norm, final_comment)
                if row_key in unique_rows:
                    continue

                unique_rows.add(row_key)

                new_row = {
                    "Документ": doc_date,
                    "Показатель": raw_indicator,
                    "Значение": final_value,
                    "Норма": final_norm,
                    "Комментарий": final_comment
                }

                all_rows.append(new_row)

        except Exception as e:
            print(f"❌ Ошибка: {file_path}: {e}")
            continue

    print(f"✅ Всего строк данных: {len(all_rows)} (дубликатов удалено: {len(unique_rows) - len(all_rows)})")

    if not all_rows:
        print("⚠️ Предупреждение: данные не найдены!")
    else:
        current_date = datetime.now().strftime('%Y-%m-%d')
        output_folder = config.get('output_folder', './output')
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        filename = f"{output_folder}/анализы_{current_date}.xlsx"

        # Очистка переносов строк для Excel
        for row in all_rows:
            for key, value in row.items():
                if isinstance(value, str):
                    row[key] = value.replace('\n', ' ')

        save_to_excel(all_rows, filename)
        print(f"💾 Файл сохранен: {filename}")
