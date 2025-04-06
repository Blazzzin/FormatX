import subprocess
import os
import sys
import time
import signal

processes = []

def run_services():
    user_service = subprocess.Popen(["python", "services/user-service/app.py"])
    processes.append(user_service)
    
    api_gateway = subprocess.Popen(["python", "api-gateway/app.py"])
    processes.append(api_gateway)
    
    file_service = subprocess.Popen(["python", "services/file-service/app.py"])
    processes.append(file_service)
    
    frontend_service = subprocess.Popen(["python", "frontend/app.py"])
    processes.append(frontend_service)
    
    print("All services are running!")
    print("Frontend is available at http://localhost:8000")
    print("Press Ctrl+C to stop all services")

def cleanup():
    print("\nShutting down all services...")
    for process in processes:
        process.terminate()
    
    time.sleep(2)
    
    for process in processes:
        if process.poll() is None:
            process.kill()
    
    print("All services stopped")

def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        run_services()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()