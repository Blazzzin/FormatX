from flask import Flask
from flask_cors import CORS
from routes import file_bp
from db import init_db

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})

init_db()

app.register_blueprint(file_bp, url_prefix='/api/files')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)