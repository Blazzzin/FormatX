import os
from datetime import datetime

def save_pdf(file, folder, prefix=''):
    if not file.filename.endswith('.pdf'):
        raise ValueError("Uploaded file is not a valid PDF")
    file_path = os.path.join(folder, f"{prefix}_{file.filename}")
    file.save(file_path)
    return file_path

def parse_page_ranges(ranges_text):
    ranges = []
    for range_str in ranges_text.split(','):
        range_str = range_str.strip()
        if '-' in range_str:
            start, end = map(int, range_str.split('-'))
            ranges.append((start, end))
        else:
            page = int(range_str)
            ranges.append((page, page))
    return ranges

def write_pdf(writer, folder, prefix, extra=""):
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    if extra:
        filename = f"{prefix}_{extra}_{timestamp}.pdf"
    else:
        filename = f"{prefix}_{timestamp}.pdf"
    path = os.path.join(folder, filename)
    with open(path, 'wb') as f:
        writer.write(f)
    return filename, path

def save_word(file, folder, prefix=''):
    if not (file.filename.endswith('.docx') or file.filename.endswith('.doc')):
        raise ValueError("Uploaded file is not a valid Word document")
    file_path = os.path.join(folder, f"{prefix}_{file.filename}")
    file.save(file_path)
    return file_path