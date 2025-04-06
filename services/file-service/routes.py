from flask import Blueprint, request, jsonify, send_file
import jwt
import os
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime, timedelta
from db import files_collection
from models import File
from dotenv import load_dotenv
load_dotenv()

file_bp = Blueprint('file', __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MERGED_FOLDER = os.path.join(BASE_DIR, 'merged_pdfs')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MERGED_FOLDER, exist_ok=True)

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
        if file.filename.endswith('.pdf'):
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            saved_files.append(file_path)

    if saved_files:
        merger = PdfWriter()
        for file_path in saved_files:
            reader = PdfReader(file_path)
            for page in reader.pages:
                merger.add_page(page)

        merged_filename = f'merged_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.pdf'
        merged_file_path = os.path.join(MERGED_FOLDER, merged_filename)
        with open(merged_file_path, 'wb') as merged_pdf:
            merger.write(merged_pdf)

        for file_path in saved_files:
            os.remove(file_path)

        user_id = get_user_id_from_token()
        file_entry = File(
            user_id=user_id, filename=merged_filename, s3_url=merged_file_path)
        files_collection.insert_one(file_entry.to_dict())
        
        merged_file_url = f'/download/{merged_filename}'
        
        return jsonify({"message": "PDFs merged successfully", "merged_file_url": merged_file_url})

    return jsonify({"error": "No PDFs to merge"}), 400

@file_bp.route('/organize', methods=['POST'])
def pdf_organize():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Uploaded file is not a valid PDF"}), 400

    uploaded_file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(uploaded_file_path)

    try:
        pages_order = request.form.get('pages')
        if not pages_order:
            return jsonify({"error": "Page order not provided"}), 400
        pages_order = list(map(int, pages_order.strip('[]').split(',')))
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

        organized_filename = f'organized_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.pdf'
        organized_file_path = os.path.join(MERGED_FOLDER, organized_filename)
        with open(organized_file_path, 'wb') as organized_pdf:
            writer.write(organized_pdf)

        os.remove(uploaded_file_path)

        user_id = get_user_id_from_token()
        file_entry = File(
            user_id=user_id, filename=organized_filename, s3_url=organized_file_path)
        files_collection.insert_one(file_entry.to_dict())

        return jsonify({"message": "PDF reorganized successfully", "organized_file_url": f'/download/{organized_filename}'})

    except Exception as e:
        return jsonify({"error": f"Failed to reorganize PDF: {str(e)}"}), 500

@file_bp.route('/split', methods=['POST'])
def pdf_split():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Uploaded file is not a valid PDF"}), 400

    uploaded_file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(uploaded_file_path)

    try:
        ranges_text = request.form.get('ranges')
        if not ranges_text:
            return jsonify({"error": "Page ranges not provided"}), 400

        ranges = []
        for range_str in ranges_text.split(','):
            range_str = range_str.strip()
            if '-' in range_str:
                start, end = map(int, range_str.split('-'))
                ranges.append((start, end))
            else:
                page = int(range_str)
                ranges.append((page, page))

        split_files = []
        reader = PdfReader(uploaded_file_path)
        total_pages = len(reader.pages)

        for start, end in ranges:
            if start < 1 or end > total_pages or start > end:
                return jsonify({"error": f"Invalid page range: {start}-{end}"}), 400

            writer = PdfWriter()
            for page_num in range(start - 1, end):
                writer.add_page(reader.pages[page_num])

            split_filename = f'split_{start}_{end}_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.pdf'
            split_path = os.path.join(MERGED_FOLDER, split_filename)
            with open(split_path, 'wb') as split_pdf:
                writer.write(split_pdf)
            
            user_id = get_user_id_from_token()
            file_entry = File(user_id=user_id, filename=split_filename, s3_url=split_path)
            files_collection.insert_one(file_entry.to_dict())

            split_files.append(f'/download/{split_filename}')

        os.remove(uploaded_file_path)
        return jsonify({"message": "PDF split successfully", "split_files": split_files})
    except Exception as e:
        return jsonify({"error": f"Failed to split PDF: {str(e)}"}), 500

@file_bp.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(MERGED_FOLDER, filename)
    return send_file(file_path, as_attachment=True)