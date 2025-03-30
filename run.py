import subprocess

def run_user_service():
    subprocess.Popen(["python", "services/user-service/app.py"])

def run_api_gateway():
    subprocess.Popen(["python", "api-gateway/app.py"])

if __name__ == "__main__":
    run_user_service()
    run_api_gateway()
    print("Both services are running!")