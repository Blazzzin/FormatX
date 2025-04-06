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

if __name__ == '__main__':
    webbrowser.open('http://localhost:8000')
    app.run(debug=True, port=8000, use_reloader=False)