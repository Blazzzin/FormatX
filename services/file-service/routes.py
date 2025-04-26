from flask import Blueprint, request, jsonify, send_file
import jwt
import os
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime, timedelta
from db import files_collection
from models import File
from dotenv import load_dotenv
from helpers import save_pdf, parse_page_ranges, write_pdf
import zipfile
import io
from pdf2docx import Converter

load_dotenv()

file_bp = Blueprint('file', __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MERGED_FOLDER = os.path.join(BASE_DIR, 'merged_pdfs')
CONVERTED_FOLDER = os.path.join(BASE_DIR, 'converted_docs')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MERGED_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

SECRET_KEY = os.getenv("SECRET_KEY")

def get_user_id_from_token():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return decoded.get("user_id")
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    return None

@file_bp.route('/merge', methods=['POST'])
def pdf_merge():
    if 'files[]' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist('files[]')
    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "No valid files uploaded"}), 400

    saved_files = []
    for file in files:
        try:
            file_path = save_pdf(file, UPLOAD_FOLDER, prefix='uploaded')
            saved_files.append(file_path)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    if saved_files:
        merger = PdfWriter()
        for file_path in saved_files:
            reader = PdfReader(file_path)
            for page in reader.pages:
                merger.add_page(page)

        merged_filename, merged_file_path = write_pdf(merger, MERGED_FOLDER, prefix='merged')

        for file_path in saved_files:
            os.remove(file_path)

        user_id = get_user_id_from_token()
        file_entry = File(user_id=user_id, filename=merged_filename, s3_url=merged_file_path)
        files_collection.insert_one(file_entry.to_dict())
        
        return jsonify({"message": "PDFs merged successfully", "file_url": f'/download/{merged_filename}'})

    return jsonify({"error": "No PDFs to merge"}), 400

@file_bp.route('/organize', methods=['POST'])
def pdf_organize():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    try:
        uploaded_file_path = save_pdf(file, UPLOAD_FOLDER, prefix='uploaded')
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        pages_order_text = request.form.get('pages')
        if not pages_order_text:
            return jsonify({"error": "Page order not provided"}), 400
        pages_order = list(map(int, pages_order_text.strip('[]').split(',')))
    except ValueError:
        return jsonify({"error": "Invalid page order format"}), 400

    try:
        reader = PdfReader(uploaded_file_path)
        writer = PdfWriter()
        for page_num in pages_order:
            if 0 < page_num <= len(reader.pages):
                writer.add_page(reader.pages[page_num - 1])
            else:
                return jsonify({"error": f"Page number {page_num} is out of range"}), 400

        organized_filename, organized_file_path = write_pdf(writer, MERGED_FOLDER, prefix='organized')
        os.remove(uploaded_file_path)

        user_id = get_user_id_from_token()
        file_entry = File(user_id=user_id, filename=organized_filename, s3_url=organized_file_path)
        files_collection.insert_one(file_entry.to_dict())

        return jsonify({"message": "PDF reorganized successfully", "file_url": f'/download/{organized_filename}'})

    except Exception as e:
        return jsonify({"error": f"Failed to reorganize PDF: {str(e)}"}), 500

@file_bp.route('/split', methods=['POST'])
def pdf_split():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    try:
        uploaded_file_path = save_pdf(file, UPLOAD_FOLDER, prefix='uploaded')
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        ranges_text = request.form.get('ranges')
        if not ranges_text:
            return jsonify({"error": "Page ranges not provided"}), 400

        ranges = parse_page_ranges(ranges_text)
        split_files = []
        reader = PdfReader(uploaded_file_path)
        total_pages = len(reader.pages)

        for start, end in ranges:
            if start < 1 or end > total_pages or start > end:
                return jsonify({"error": f"Invalid page range: {start}-{end}"}), 400

            writer = PdfWriter()
            for page_num in range(start - 1, end):
                writer.add_page(reader.pages[page_num])

            split_filename, split_path = write_pdf(writer, MERGED_FOLDER, prefix='split', extra=f"{start}_{end}")

            user_id = get_user_id_from_token()
            file_entry = File(user_id=user_id, filename=split_filename, s3_url=split_path)
            files_collection.insert_one(file_entry.to_dict())

            split_files.append(split_filename)

        os.remove(uploaded_file_path)

        if len(split_files) == 1:
            return jsonify({
                "message": "PDF split successfully",
                "file_url": f'/download/{split_files[0]}'
            })
        else:
            zip_filename = f'split_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.zip'
            zip_path = os.path.join(MERGED_FOLDER, zip_filename)

            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for filename in split_files:
                    file_path = os.path.join(MERGED_FOLDER, filename)
                    zipf.write(file_path, arcname=filename)

            for filename in split_files:
                file_path = os.path.join(MERGED_FOLDER, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)

            return jsonify({
                "message": "PDFs split and zipped successfully",
                "zip_url": f'/download/{zip_filename}'
            })

    except Exception as e:
        return jsonify({"error": f"Failed to split PDF: {str(e)}"}), 500
    
@file_bp.route('/convert/pdf-to-word', methods=['POST'])
def pdf_to_word():
    if 'files[]' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    pdf_files = request.files.getlist('files[]')
    if not pdf_files or all(f.filename == '' for f in pdf_files):
        return jsonify({"error": "No valid files uploaded"}), 400

    user_id = get_user_id_from_token()
    converted_paths = []

    for f in pdf_files:
        try:
            pdf_path = save_pdf(f, UPLOAD_FOLDER, prefix='uploaded')
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        name, _      = os.path.splitext(f.filename)
        timestamp    = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        docx_name    = f"{name}_{timestamp}.docx"
        docx_path    = os.path.join(CONVERTED_FOLDER, docx_name)

        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
        os.remove(pdf_path)

        entry = File(
            user_id=user_id,
            filename=docx_name,
            s3_url=docx_path
        )
        files_collection.insert_one(entry.to_dict())  

        converted_paths.append((docx_name, docx_path))

    if len(converted_paths) == 1:
        name, _ = converted_paths[0]
        return jsonify({
            "message": "Conversion successful",
            "file_url": f"/download/{name}",
            "filename": name
        }), 200

    zip_name = f"pdf2word_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.zip"
    zip_path = os.path.join(CONVERTED_FOLDER, zip_name)
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for name, path in converted_paths:
            zf.write(path, arcname=name)
            os.remove(path)

    return jsonify({
        "message": "Multiple conversions successful",
        "zip_url": f"/download/{zip_name}",
        "filename": zip_name
    }), 200

@file_bp.route('/download/<filename>')
def download(filename):
    for folder in (MERGED_FOLDER, CONVERTED_FOLDER):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404