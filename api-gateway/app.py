from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)