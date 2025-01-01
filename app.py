from flask import Flask, request, render_template, send_file, jsonify
import os
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)

# Directories for uploaded and merged files
UPLOAD_FOLDER = 'uploads'
MERGED_FOLDER = 'merged'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MERGED_FOLDER'] = MERGED_FOLDER

# Ensure the directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MERGED_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pdf-merge', methods=['GET', 'POST'])
def pdf_merge():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            return jsonify({"error": "No files uploaded"}), 400

        files = request.files.getlist('files[]')
        if not files or all(file.filename == '' for file in files):
            return jsonify({"error": "No valid files uploaded"}), 400

        # Save uploaded PDF files
        saved_files = []
        for file in files:
            if file.filename.endswith('.pdf'):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                saved_files.append(file_path)

        # Merge PDFs using PyPDF2
        if saved_files:
            merger = PdfWriter()
            for file_path in saved_files:
                merger.append(file_path)

            merged_file_path = os.path.join(app.config['MERGED_FOLDER'], 'merged_output.pdf')
            with open(merged_file_path, 'wb') as merged_pdf:
                merger.write(merged_pdf)

            # Clean up individual uploaded files if needed
            for file_path in saved_files:
                os.remove(file_path)

            # Return a JSON response with the download URL for the merged PDF
            return jsonify({"message": "PDFs merged successfully", "merged_file_url": f'/download/{os.path.basename(merged_file_path)}'})

        return jsonify({"error": "No PDFs to merge"}), 400

    return render_template('pdf-merge.html')

@app.route('/pdf-organize', methods=['GET', 'POST'])
def pdf_organize():
    if request.method == 'POST':
        if 'file' not in request.files or not request.files['file']:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "Uploaded file is not a valid PDF"}), 400

        # Save the uploaded PDF
        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(uploaded_file_path)

        # Get the new page order from the client
        try:
            pages_order = request.form.get('pages')
            if not pages_order:
                return jsonify({"error": "Page order not provided"}), 400

            pages_order = list(map(int, pages_order.strip('[]').split(',')))
        except ValueError:
            return jsonify({"error": "Invalid page order format"}), 400

        try:
            # Reorganize the PDF pages
            reader = PdfReader(uploaded_file_path)
            writer = PdfWriter()

            for page_num in pages_order:
                if 0 < page_num <= len(reader.pages):
                    writer.add_page(reader.pages[page_num - 1])
                else:
                    return jsonify({"error": f"Page number {page_num} is out of range"}), 400

            # Save the reorganized PDF
            organized_file_path = os.path.join(app.config['MERGED_FOLDER'], 'organized_output.pdf')
            with open(organized_file_path, 'wb') as organized_pdf:
                writer.write(organized_pdf)

            # Clean up the uploaded file
            os.remove(uploaded_file_path)

            # Return a JSON response with the download URL
            return jsonify({"message": "PDF reorganized successfully", 
                            "organized_file_url": f'/download/{os.path.basename(organized_file_path)}'})

        except Exception as e:
            return jsonify({"error": f"Failed to reorganize PDF: {str(e)}"}), 500

    return render_template('pdf-organize.html')

@app.route('/pdf-split', methods=['GET', 'POST'])
def pdf_split():
    return render_template('pdf-split.html')

@app.route('/download/<filename>')
def download(filename):
    merged_file_path = os.path.join(app.config['MERGED_FOLDER'], filename)
    return send_file(merged_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)