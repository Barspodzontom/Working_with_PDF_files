#excel_exporter.py

import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from openpyxl.utils import get_column_letter


def save_to_excel(data, filename):
    if not data:
        print("⚠️ Предупреждение: нет данных для сохранения в Excel.")
        df = pd.DataFrame(columns=["Документ", "Показатель", "Значение", "Норма", "Комментарий"])
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(filename, index=False)
        return

    # Берем ключи ТОЛЬКО из первого элемента списка
    headers = list(data[0].keys())

    # Важно: явно указываем порядок колонок, чтобы избежать случайного перемешивания
    expected_columns = ["Документ", "Показатель", "Значение", "Норма", "Комментарий"]

    # Фильтруем и сортируем колонки, чтобы в Excel они шли строго в нужном порядке
    final_columns = [col for col in expected_columns if col in headers]

    df = pd.DataFrame(data, columns=final_columns)

    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(filename, index=False)
    print(f"✅ Данные успешно сохранены в: {filename}")
