import re
import PyPDF2


def extract_code_from_pdf(file_path):
    """Извлекает код дисциплины из PDF файла"""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        first_page = reader.pages[0]
        text = first_page.extract_text()

        # Ищем код в разных форматах, включая ФТД
        code_match = re.search(r'#\s*([А-Я]\d+\.[А-Я][\w.]*\d+)', text) or \
                     re.search(r'([А-Я]\d+\.[А-Я][\w.]*\d+)\s*\n', text) or \
                     re.search(r'(ФТД\.\d+)', text)
        return code_match.group(1) if code_match else None


def extract_discipline_name(filename):
    """Извлекает название дисциплины из имени файла"""
    # Основной вариант: между _plx_ и _Разработка
    match = re.search(r'_plx_([^_]+)_Разработка', filename)
    if match:
        return match.group(1).strip()

    # Альтернативный вариант: после _plx_ до следующего _ или_.
    match = re.search(r'_plx_([^_.]+)', filename)
    if match:
        return match.group(1).strip()

    # Если ничего не найдено, попробуем извлечь из текста перед .pdf
    match = re.search(r'([^_]+)\.pdf$', filename)
    return match.group(1).strip() if match else None


def process_filename(filename, code, file_path):
    """Формирует новое имя файла в формате: КОД НАЗВАНИЕ.pdf или РПД КОД НАЗВАНИЕ.pdf"""
    discipline = extract_discipline_name(filename)
    if not discipline:
        return None

    # Заменяем подчеркивания на пробелы в названии дисциплины
    discipline = discipline.replace('_', ' ')
    # Удаляем возможные двойные пробелы
    discipline = re.sub(r'\s+', ' ', discipline).strip()

    # Проверяем наличие 'annot' в пути файла
    if 'annot' in file_path.lower() or 'аннот' in file_path.lower():
        return f"{code} {discipline}.pdf"
    else:
        return f"РПД {code} {discipline}.pdf"


def is_already_renamed(filename, code, file_path):
    """
    Проверка названия на соответствие целевому формату
    """
    # Если код не передан, пытаемся извлечь его из имени файла
    if code is None:
        # Проверяем оба возможных формата: с РПД и без
        patterns = [
            r'^РПД ([А-Я]\d+\.[А-Я][\w.]*\d+) .+\.pdf$',
            r'^([А-Я]\d+\.[А-Я][\w.]*\d+) .+\.pdf$',
            r'^РПД ФТД\.\d+ .+\.pdf$',
            r'^ФТД\.\d+ .+\.pdf$'
        ]
        for pattern in patterns:
            if re.match(pattern, filename, re.IGNORECASE):
                return True
        return False

    # Остальная логика проверки с переданным кодом...
    discipline = extract_discipline_name(filename)
    if not discipline:
        return False

    discipline = discipline.replace('_', ' ')
    discipline = re.sub(r"\s+", " ", discipline).strip()

    if 'annot' in file_path.lower() or 'аннот' in file_path.lower():
        target_pattern = f'{code} {discipline}'
    else:
        target_pattern = f'РПД {code} {discipline}'

    base_match = filename.startswith(target_pattern + '.pdf')
    duplicate_match = re.match(re.escape(target_pattern) + r' \(\d+\)\.pdf', filename)

    return base_match or bool(duplicate_match)
