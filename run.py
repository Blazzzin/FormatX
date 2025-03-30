import subprocess
import os
import webbrowser
import time

def run_user_service():
    subprocess.Popen(["python", "services/user-service/app.py"])

def run_api_gateway():
    subprocess.Popen(["python", "api-gateway/app.py"])

def run_frontend():
    # Change to the 'frontend' directory where both 'templates' and 'static' are located
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    os.chdir(frontend_dir)
    
    # Start the simple HTTP server
    subprocess.Popen(["python", "-m", "http.server", "8000"])
    
    time.sleep(2)
    
    # Open the index.html in the browser
    webbrowser.open("http://localhost:8000/templates/index.html")

if __name__ == "__main__":
    run_user_service()
    run_api_gateway()
    run_frontend()

    print("Both services and frontend are running!")