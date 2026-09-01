# launcher.py
import sys
import os
import streamlit.web.cli as stcli
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    # 1. Determine where the bundle extracted the files
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
        log_dir = os.path.dirname(sys.executable)
        logger.info(f"Running as PyInstaller bundle, base path: {base_path}")
    else:
        # Running as normal python script
        base_path = os.path.dirname(os.path.abspath(__file__))
        log_dir = base_path
        logger.info(f"Running normally, base path: {base_path}")

    logger.info(f"Working directory will be: {base_path}")
    logger.info(f"Files in base_path: {os.listdir(base_path)}")

    # 2. CRITICAL: Change working directory to the app folder
    # This ensures app.py can find "icons/" and "fonts/" using relative paths
    os.chdir(base_path)

    # 3. Path to your main app file
    app_path = os.path.join(base_path, "app.py")
    logger.info(f"Looking for app.py at: {app_path}")

    # 4. Configure Streamlit arguments (simulates the command line)
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
        "--server.port=8501",
        "--server.headless=false",
        "--browser.gatherUsageStats=false",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false"
    ]

    # 5. Start Streamlit
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()