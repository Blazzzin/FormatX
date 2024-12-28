from flask import Flask, request, render_template, send_file, jsonify
import os
from PyPDF2 import PdfMerger

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
            merger = PdfMerger()
            for file_path in saved_files:
                merger.append(file_path)

            merged_file_path = os.path.join(app.config['MERGED_FOLDER'], 'merged_output.pdf')
            merger.write(merged_file_path)
            merger.close()

            # Clean up individual uploaded files if needed
            for file_path in saved_files:
                os.remove(file_path)

            # Return a JSON response with the download URL for the merged PDF
            return jsonify({"message": "PDFs merged successfully", "merged_file_url": f'/download/{os.path.basename(merged_file_path)}'})

        return jsonify({"error": "No PDFs to merge"}), 400

    return render_template('pdf-merge.html')

@app.route('/download/<filename>')
def download(filename):
    merged_file_path = os.path.join(app.config['MERGED_FOLDER'], filename)
    return send_file(merged_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)