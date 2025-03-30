from flask import Flask
from flask_cors import CORS
from routes import user_bp
from db import init_db

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize MongoDB connection
init_db()

# Register user authentication routes
app.register_blueprint(user_bp, url_prefix='/api/user')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)