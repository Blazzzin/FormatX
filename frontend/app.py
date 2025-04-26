from flask import Flask, render_template
import webbrowser

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pdf-merge')
def pdf_merge():
    return render_template('pdf-merge.html')

@app.route('/pdf-organize')
def pdf_organize():
    return render_template('pdf-organize.html')

@app.route('/pdf-split')
def pdf_split():
    return render_template('pdf-split.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/pdf-to-word')
def pdf_to_word():
    return render_template('pdf-to-word.html')

@app.route('/word-to-pdf')
def word_to_pdf():
    return render_template('word-to-pdf.html')

@app.route('/pdf-to-powerpoint')
def pdf_to_powerpoint():
    return render_template('pdf-to-powerpoint.html')

@app.route('/powerpoint-to-pdf')
def powerpoint_to_pdf():
    return render_template('powerpoint-to-pdf.html')

@app.route('/pdf-to-image')
def pdf_to_image():
    return render_template('pdf-to-image.html')

@app.route('/image-to-pdf')
def image_to_pdf():
    return render_template('image-to-pdf.html')

if __name__ == '__main__':
    webbrowser.open('http://localhost:8000')
    app.run(debug=True, port=8000, use_reloader=False)