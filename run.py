import platform
from rag.com.app import app
from rag.com.config import API_HOST, API_PORT, DEBUG_MODE

def run_server():
    """Run the server based on the operating system"""
    if platform.system() == 'Windows':
        from waitress import serve
        print(f"Starting Waitress server on http://{API_HOST}:{API_PORT}")
        serve(app, host=API_HOST, port=API_PORT)
    else:
        print(f"Starting Flask server on http://{API_HOST}:{API_PORT}")
        app.run(host=API_HOST, port=API_PORT, debug=DEBUG_MODE)

if __name__ == "__main__":
    run_server()
