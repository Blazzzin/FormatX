from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})

USER_SERVICE_URL = "http://localhost:5001/api/user"
FILE_SERVICE_URL = "http://localhost:5002/api/files"
TASK_SERVICE_URL = "http://localhost:5003/api/tasks"

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
    print(f"Received request to {path}")
    print(f"Request method: {request.method}")
    print(f"Request headers: {request.headers}")
    print(f"Request form: {request.form}")

    response = None

    if request.method == 'POST' and request.files:
        print("Request contains files")
        
        files_data = []
        for name, file_list in request.files.items():
            if name.endswith('[]'):
                for file in request.files.getlist(name):
                    files_data.append(
                        (name, (file.filename, file.stream, file.content_type))
                    )
            else:
                files_data.append(
                    (name, (file_list.filename, file_list.stream, file_list.content_type))
                )

        print(f"Files data: {files_data}")

        response = requests.request(
            method=request.method,
            url=f"{FILE_SERVICE_URL}/{path}",
            headers={key: value for (key, value) in request.headers if key not in ['Host', 'Content-Type']},
            files=files_data,
            data=request.form
        )
    else:
        print("Request is JSON")
        response = requests.request(
            method=request.method,
            url=f"{FILE_SERVICE_URL}/{path}",
            headers={key: value for (key, value) in request.headers if key != "Host"},
            json=request.get_json(silent=True)
        )
        

    print(f"File service response status: {response.status_code}")

    return response.content, response.status_code, {'Content-Type': response.headers.get('Content-Type', 'application/json')}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)