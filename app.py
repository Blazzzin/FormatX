from flask import Flask, request, render_template, send_file
import os
from converters.image import convert_image, selected_options

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure uploads directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/image', methods=['GET', 'POST'])
def image():
    if request.method == 'POST':
        file = request.files['file']
        conversion_type = request.form.get('conversion_type')

        if file and conversion_type:
            filename = file.filename
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)

            extension = selected_options(conversion_type)
            if extension is None:
                return "Invalid conversion type", 400

            base, _ = os.path.splitext(input_path)
            output_path = base + extension
            
            convert_image(input_path, output_path)
            return send_file(output_path, as_attachment=True)
        
        return "No file or conversion type selected", 400
    
    return render_template('image.html')

if __name__ == '__main__':
    app.run(debug=True)