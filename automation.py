import os
import platform
import subprocess
import sys

def install_dependencies():
    system_platform = platform.system().lower()
    
    # Determine platform and install dependencies accordingly
    if system_platform == 'windows':
        print("Detected platform: Windows")
        # Using pip to install required dependencies
        dependencies = [
            'pyqt5', 'pyautogui', 'opencv-python', 'pillow', 'flask', 'paramiko', 'pyinstaller'
        ]
        for package in dependencies:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    elif system_platform == 'linux' or system_platform == 'darwin':  # Linux or macOS
        print(f"Detected platform: {system_platform.title()}")
        # Update package manager for Linux/macOS and install dependencies
        if system_platform == 'linux':
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'python3-pip'], check=True)
        
        dependencies = [
            'pyqt5', 'pyautogui', 'opencv-python', 'pillow', 'flask', 'paramiko', 'pyinstaller'
        ]
        for package in dependencies:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    else:
        print("Unsupported platform detected. Exiting.")
        sys.exit(1)

def set_permissions():
    system_platform = platform.system().lower()
    
    # Set necessary permissions
    if system_platform == 'linux' or system_platform == 'darwin':  # Linux or macOS
        print("Setting executable permissions for Linux/macOS")
        os.system('chmod +x automation.py')
    else:
        print("No specific permissions to set for Windows.")

def create_project_structure(base_dir):
    # Create the required directory structure
    dirs_to_create = [
        os.path.join(base_dir, 'src'),
        os.path.join(base_dir, 'certs'),
        os.path.join(base_dir, 'dist')
    ]

    for directory in dirs_to_create:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def create_sample_scripts(base_dir):
    # Create sample Python files in the src directory to bootstrap the application
    src_dir = os.path.join(base_dir, 'src')

    main_script_content = """
from PyQt5 import QtWidgets
import sys

class RemoteAccessDashboard(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Ethical Remote Access Tool")
        self.setGeometry(100, 100, 800, 600)
        
        desktop_button = QtWidgets.QPushButton('Desktop Capture', self)
        desktop_button.setGeometry(50, 50, 200, 50)
        desktop_button.clicked.connect(self.start_desktop_capture)

        chat_button = QtWidgets.QPushButton('Live Chat', self)
        chat_button.setGeometry(50, 120, 200, 50)
        chat_button.clicked.connect(self.start_chat)

    def start_desktop_capture(self):
        pass
    
    def start_chat(self):
        pass

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = RemoteAccessDashboard()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
"""

    # Write the main Python script
    main_script_path = os.path.join(src_dir, 'remote_access_tool.py')
    with open(main_script_path, 'w') as main_script:
        main_script.write(main_script_content)
        print(f"Created main script: {main_script_path}")

def build_executable(base_dir):
    # Build the executable using PyInstaller
    src_dir = os.path.join(base_dir, 'src')
    main_script_path = os.path.join(src_dir, 'remote_access_tool.py')
    
    print("Building executable using PyInstaller...")
    subprocess.check_call(['pyinstaller', '--onefile', '--windowed', main_script_path])

def main():
    # Define the base directory
    base_dir = r"C:\Users\micky\OneDrive\Desktop\Remote-Desktop"

    # Step 1: Install Dependencies
    install_dependencies()

    # Step 2: Set Permissions
    set_permissions()

    # Step 3: Create Project Structure
    create_project_structure(base_dir)

    # Step 4: Create Sample Scripts
    create_sample_scripts(base_dir)

    # Step 5: Build Executable
    build_executable(base_dir)

    print("Automation completed successfully.")

if __name__ == "__main__":
    main()
