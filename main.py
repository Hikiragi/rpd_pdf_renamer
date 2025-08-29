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




