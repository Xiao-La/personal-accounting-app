#!/usr/bin/env python3
"""
Personal Accounting App - macOS Launcher
Launches the Flask app and automatically opens it in the default browser.
"""

import os
import sys
import time
import threading
import webbrowser
import logging

# Set up logging to help debug issues
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure we're in the right directory
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    bundle_dir = sys._MEIPASS
    os.chdir(os.path.dirname(sys.executable))
else:
    # Running as script
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(bundle_dir)

logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Bundle directory: {bundle_dir}")

# Now import after setting up the directory
try:
    from main import init_db, app
    logger.info("Successfully imported main module")
except Exception as e:
    logger.error(f"Failed to import main: {e}")
    sys.exit(1)

def find_free_port():
    """Find a free port starting from 5000"""
    import socket
    for port in range(5000, 5100):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except:
            continue
    return 5000

def open_browser(port):
    """Open the app in the default browser after a short delay"""
    time.sleep(2)  # Give Flask time to start
    webbrowser.open(f'http://127.0.0.1:{port}')

def main():
    """Main launcher function"""
    try:
        print("🏦 Starting Personal Accounting App...")
        logger.info("Starting app launcher")
        
        # Initialize database
        init_db()
        print("✅ Database initialized")
        logger.info("Database initialized successfully")
        
        # Find available port
        port = find_free_port()
        print(f"🌐 Starting server on port {port}")
        logger.info(f"Using port {port}")
        
        # Start browser opener in background thread
        browser_thread = threading.Thread(target=open_browser, args=(port,))
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start Flask app
        print(f"🚀 Opening Personal Accounting App at http://127.0.0.1:{port}")
        print("💡 To quit, press Ctrl+C or close this window")
        
        logger.info("Starting Flask server")
        app.run(
            host='127.0.0.1',
            port=port,
            debug=False,  # Disable debug for app mode
            use_reloader=False,  # Disable reloader for packaging
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Personal Accounting App closed")
        logger.info("App closed by user")
    except Exception as e:
        logger.error(f"Error starting app: {e}")
        print(f"❌ Error: {e}")
        print(f"Working directory: {os.getcwd()}")
        print(f"Files in directory: {os.listdir('.')}")
        input("Press Enter to close...")
        sys.exit(1)

if __name__ == '__main__':
    main()