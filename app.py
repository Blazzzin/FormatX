from flask import Flask, request, render_template, send_file, jsonify
import os
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)

# Directories for uploaded and merged/organized files
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
                reader = PdfReader(file_path)  # Open each PDF
                for page in reader.pages:
                    merger.add_page(page)

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
    if request.method == 'POST':
        if 'file' not in request.files or not request.files['file']:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "Uploaded file is not a valid PDF"}), 400

        # Save the uploaded PDF
        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(uploaded_file_path)

        # Get the page ranges from the client
        try:
            ranges_text = request.form.get('ranges')
            if not ranges_text:
                return jsonify({"error": "Page ranges not provided"}), 400

            # Parse the page ranges (e.g., "1-3, 4-6, 7-10")
            ranges = []
            for range_str in ranges_text.split(','):
                range_str = range_str.strip()
                if '-' in range_str:
                    start, end = map(int, range_str.split('-'))
                    ranges.append((start, end))
                else:
                    page = int(range_str)
                    ranges.append((page, page))

            # Create a list to store the paths of split files
            split_files = []
            reader = PdfReader(uploaded_file_path)

            # Validate page ranges
            total_pages = len(reader.pages)
            for start, end in ranges:
                if start < 1 or end > total_pages or start > end:
                    return jsonify({"error": f"Invalid page range: {start}-{end}"}), 400

            # Split the PDF according to the ranges
            for i, (start, end) in enumerate(ranges):
                writer = PdfWriter()
                
                # Add pages for this range (converting to 0-based index)
                for page_num in range(start - 1, end):
                    writer.add_page(reader.pages[page_num])

                # Save this split
                split_filename = f'split_{i + 1}.pdf'
                split_path = os.path.join(app.config['MERGED_FOLDER'], split_filename)
                with open(split_path, 'wb') as split_pdf:
                    writer.write(split_pdf)
                
                split_files.append(f'/download/{split_filename}')

            # Clean up the uploaded file
            os.remove(uploaded_file_path)

            # Return the URLs for all split files
            return jsonify({
                "message": "PDF split successfully",
                "split_files": split_files
            })

        except ValueError as e:
            return jsonify({"error": f"Invalid page range format: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"error": f"Failed to split PDF: {str(e)}"}), 500

    return render_template('pdf-split.html')

@app.route('/download/<filename>')
def download(filename):
    merged_file_path = os.path.join(app.config['MERGED_FOLDER'], filename)
    return send_file(merged_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)