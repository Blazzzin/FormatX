from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import os
from dotenv import load_dotenv
from helpers import extract_files_data

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
FILE_SERVICE_URL = os.getenv("FILE_SERVICE_URL")
TASK_SERVICE_URL = os.getenv("TASK_SERVICE_URL")

@app.route('/api/user/<path:path>', methods=['GET', 'POST'])
def user_service_proxy(path):
    response = requests.request(
        method=request.method,
        url=f"{USER_SERVICE_URL}/{path}",
        headers={key: value for (key, value) in request.headers if key != "Host"},
        json=request.get_json()
    )
    return jsonify(response.json()), response.status_code

@app.route('/api/files/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def file_service_proxy(path):
    if request.method == 'POST' and request.files:
        files_data = extract_files_data(request.files)
        response = requests.request(
            method=request.method,
            url=f"{FILE_SERVICE_URL}/{path}",
            headers={key: value for (key, value) in request.headers if key not in ['Host', 'Content-Type']},
            files=files_data,
            data=request.form
        )
    else:
        response = requests.request(
            method=request.method,
            url=f"{FILE_SERVICE_URL}/{path}",
            headers={key: value for (key, value) in request.headers if key != "Host"},
            json=request.get_json(silent=True)
        )
        
    return response.content, response.status_code, {
        'Content-Type': response.headers.get('Content-Type', 'application/json')
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)