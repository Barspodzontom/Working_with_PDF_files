#lab_results_parser.py

def normalize_unit(unit_str):
    # Функция нормализации единиц измерения
    unit_map = {"Микромоль": "µmol"}
    return unit_map.get(unit_str.strip(), unit_str)

def parse_lab_result_table(page_data):
    """
    Парсит лабораторные данные из структуры page_data.
    page_data должен содержать ключ 'tables' со списком таблиц (каждая таблица - список строк).
    Возвращает список словарей с ключами: Показатель, Значение, Норма, Комментарий.
    """
    results = []
    tables = page_data.get('tables', [])

    if not tables:
        return results

    # Словарь вариантов заголовков для поиска
    header_variants = {
        'param': ['Лабораторные исследования', 'Наименование исследования', 'Показатель'],
        'result': ['Результат', 'Значение'],
        'ref': ['Мин. и макс. значения', 'Референсные значения', 'Норма'],
        'comment': ['Комментарий', 'Примечание']
    }

    for table in tables:
        # Пропускаем пустые таблицы или таблицы без заголовков
        if not table or len(table) < 2:
            continue

        headers_row = table
        if not headers_row:
            continue

        # Инициализируем индексы колонок
        idx_map = {'param': None, 'result': None, 'ref': None, 'comment': None}

        # Шаг 1: Поиск точных совпадений
        for idx, h in enumerate(headers_row):
            if h is None:
                continue
            h_str = str(h).strip()

            for key, variants in header_variants.items():
                if idx_map[key] is None and h_str in variants:
                    idx_map[key] = idx

        # Шаг 2: Если не нашли все колонки точно, пробуем частичное совпадение (регистронезависимое)
        if any(v is None for v in idx_map.values()):
            for idx, h in enumerate(headers_row):
                if h is None:
                    continue
                h_lower = str(h).lower().strip()

                for key, variants in header_variants.items():
                    if idx_map[key] is None and any(k.lower() in h_lower for k in variants):
                        idx_map[key] = idx

        # Критическая проверка: обязательно должны быть найдены колонки "Показатель" и "Результат"
        if idx_map['param'] is None or idx_map['result'] is None:
            # Для отладки можно раскомментировать:
            # print(f"⚠️ Не удалось распознать заголовки таблицы. Строка заголовков: {headers_row}")
            continue

        # Шаг 3: Парсинг строк данных (начиная со второй строки)
        for row in table[1:]:
            if not row:
                continue

            # Безопасное получение значений по индексам
            raw_param = row[idx_map['param']] if idx_map['param'] < len(row) else ""
            raw_res = row[idx_map['result']] if idx_map['result'] < len(row) else ""
            raw_ref = row[idx_map['ref']] if idx_map['ref'] is not None and idx_map['ref'] < len(row) else ""
            raw_comm = row[idx_map['comment']] if idx_map['comment'] is not None and idx_map['comment'] < len(row) else ""

            # Очистка данных
            param_str = str(raw_param).strip() if raw_param is not None else ""
            res_str = str(raw_res).strip() if raw_res is not None else ""
            ref_str = str(raw_ref).strip() if raw_ref is not None else ""
            comm_str = str(raw_comm).strip() if raw_comm is not None else ""

            if not param_str:
                continue

            results.append({
                "Показатель": param_str,
                "Значение": res_str,
                "Норма": ref_str,
                "Комментарий": comm_str
            })

    return results

