from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import socket
import threading
import pyautogui
import cv2
import numpy as np
import platform
import subprocess
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

LICENSE_TEXT = """
MIT License

Copyright (c) 2024 Darkspace Software and Security, Michael James Blenkinsop (DARK ANGEL)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

clients = []  # List to store connected clients
client_details = {}  # Dictionary to store client details (name, email, phone)
video_chat_windows = []  # List to store video chat windows for each client

def setup_environment():
    """Checks the platform and sets up the environment accordingly."""
    system_platform = platform.system().lower()
    print(f"Detected platform: {system_platform.title()}")

    # Install dependencies
    if system_platform in ['windows', 'linux', 'darwin']:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            dependencies = ['pyqt5', 'pyautogui', 'opencv-python', 'numpy', 'pillow']
            for package in dependencies:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except Exception as e:
            print(f"Failed to set up dependencies: {e}")
            sys.exit(1)
    else:
        print(f"Unsupported platform: {system_platform.title()}")
        sys.exit(1)

def send_email_notification(to_email, subject, body):
    """Function to send an email using Gmail's SMTP server."""
    from_email = "youremail@gmail.com"  # Replace with your email
    from_password = "yourpassword"  # Replace with your app-specific password

    try:
        message = MIMEMultipart()
        message['From'] = from_email
        message['To'] = to_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Securing the connection
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, message.as_string())
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")

class RemoteAccessDashboard(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.notification_email = "mickyblenk@gmail.com"  # Default notification email
        self.initUI()
        self.server_socket = None
        self.network_connected = False

    def initUI(self):
        self.setWindowTitle("Ethical Remote Access Tool - Instructor Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #333333; color: white;")

        # Logo and Branding
        logo_label = QtWidgets.QLabel(self)
        logo_label.setGeometry(20, 20, 150, 150)
        logo_label.setPixmap(QtGui.QPixmap("anaconda_logo.png").scaled(150, 150, QtCore.Qt.KeepAspectRatio))
        
        branding_label = QtWidgets.QLabel("DARKSPACE SOFTWARE AND SECURITY LLC", self)
        branding_label.setGeometry(200, 20, 400, 50)
        branding_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffcc00;")

        # Navigation and Instructions Section
        instructions = QtWidgets.QTextBrowser(self)
        instructions.setGeometry(650, 20, 500, 350)
        instructions.setStyleSheet("background-color: #222222; color: white; font-size: 14px;")
        instructions.setText("""
        <h3>Instructions for Server (Instructor):</h3>
        <ol>
            <li>Submit your details to proceed.</li>
            <li>Set your email address to receive notifications when students connect.</li>
            <li>Click 'Start Network Server' to allow students to connect.</li>
            <li>Use 'View Screens' to view all connected students' screens.</li>
            <li>Use 'Group Chat' to communicate with all students.</li>
            <li>Use 'Start Video Chat' to initiate video sessions with each student.</li>
        </ol>
        <br>
        <h3>Instructions for Clients (Students):</h3>
        <ol>
            <li>Connect to the server by entering the IP address provided by the instructor.</li>
            <li>Submit your contact details before proceeding.</li>
            <li>After successful connection, follow instructions from the instructor for screen sharing and communication.</li>
        </ol>
        """)

        # Profile Information Fields
        self.name_field = QtWidgets.QLineEdit(self)
        self.name_field.setGeometry(50, 200, 300, 30)
        self.name_field.setPlaceholderText("Enter your name...")
        self.name_field.setStyleSheet("background-color: white; color: black;")

        self.email_field = QtWidgets.QLineEdit(self)
        self.email_field.setGeometry(50, 240, 300, 30)
        self.email_field.setPlaceholderText("Enter your email...")
        self.email_field.setStyleSheet("background-color: white; color: black;")

        self.phone_field = QtWidgets.QLineEdit(self)
        self.phone_field.setGeometry(50, 280, 300, 30)
        self.phone_field.setPlaceholderText("Enter your phone number...")
        self.phone_field.setStyleSheet("background-color: white; color: black;")

        self.submit_details_button = QtWidgets.QPushButton('Submit Details', self)
        self.submit_details_button.setGeometry(50, 320, 200, 40)
        self.submit_details_button.setStyleSheet("background-color: blue; color: white;")
        self.submit_details_button.setToolTip("Submit your details to proceed with the remote access tool.")
        self.submit_details_button.clicked.connect(self.submit_details)

        # Email Notification Input
        self.notification_email_field = QtWidgets.QLineEdit(self)
        self.notification_email_field.setGeometry(50, 380, 300, 30)
        self.notification_email_field.setPlaceholderText("Enter notification email...")
        self.notification_email_field.setStyleSheet("background-color: white; color: black;")
        self.notification_email_field.setText(self.notification_email)

        self.set_notification_email_button = QtWidgets.QPushButton('Set Notification Email', self)
        self.set_notification_email_button.setGeometry(50, 420, 200, 40)
        self.set_notification_email_button.setStyleSheet("background-color: blue; color: white;")
        self.set_notification_email_button.setToolTip("Set the email address to receive student notifications.")
        self.set_notification_email_button.clicked.connect(self.set_notification_email)

        # Buttons for functionalities
        view_screens_button = QtWidgets.QPushButton('View Screens', self)
        view_screens_button.setGeometry(50, 480, 200, 50)
        view_screens_button.setStyleSheet("background-color: blue; color: white;")
        view_screens_button.setToolTip("View the screens of all connected students.")
        view_screens_button.clicked.connect(self.start_view_screens)

        group_chat_button = QtWidgets.QPushButton('Group Chat', self)
        group_chat_button.setGeometry(50, 550, 200, 50)
        group_chat_button.setStyleSheet("background-color: blue; color: white;")
        group_chat_button.setToolTip("Start a group chat session with all connected students.")
        group_chat_button.clicked.connect(self.start_group_chat)

        video_chat_button = QtWidgets.QPushButton('Start Video Chat', self)
        video_chat_button.setGeometry(50, 620, 200, 50)
        video_chat_button.setStyleSheet("background-color: blue; color: white;")
        video_chat_button.setToolTip("Start video chats with each connected student.")
        video_chat_button.clicked.connect(self.start_video_chat)

        network_button = QtWidgets.QPushButton('Start Network Server', self)
        network_button.setGeometry(50, 690, 200, 50)
        network_button.setStyleSheet("background-color: green; color: white;")
        network_button.setToolTip("Start the network server to allow students to connect.")
        network_button.clicked.connect(self.start_server)

    def upload_profile_picture(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Profile Picture", "",
                                                             "Images (*.png *.jpg *.jpeg *.bmp *.gif)", options=options)
        if file_name:
            self.profile_pic_label.setPixmap(QtGui.QPixmap(file_name).scaled(100, 100, QtCore.Qt.KeepAspectRatio))

    def submit_details(self):
        name = self.name_field.text().strip()
        email = self.email_field.text().strip()
        phone = self.phone_field.text().strip()

        if not name or not email or not phone:
            QtWidgets.QMessageBox.warning(self, "Incomplete Details", "Please fill in all fields.")
            return

        message = f"Name: {name}\nEmail: {email}\nPhone: {phone}"
        QtWidgets.QMessageBox.information(self, "User Details Submitted", message)

        # Store client details
        client_details[name] = {"email": email, "phone": phone}

        # Send email notification
        self.send_client_details_email(name, email, phone)

    def set_notification_email(self):
        self.notification_email = self.notification_email_field.text().strip()
        QtWidgets.QMessageBox.information(self, "Notification Email Set", f"Notification email set to: {self.notification_email}")

    def send_client_details_email(self, name, email, phone):
        """Function to send client details to the tutor."""
        subject = f"New Student Details - {name}"
        body = f"Student Name: {name}\nEmail: {email}\nPhone: {phone}"
        send_email_notification(self.notification_email, subject, body)

    def start_view_screens(self):
        if not clients:
            QtWidgets.QMessageBox.warning(self, "No Clients Connected", "No students are currently connected.")
            return
        for i, client in enumerate(clients):
            screen_window = ScreenWindow(client, f"Student {i+1} Screen")
            screen_window.show()
            video_chat_windows.append(screen_window)

    def start_group_chat(self):
        if not clients:
            QtWidgets.QMessageBox.warning(self, "No Clients Connected", "No students are currently connected.")
            return
        self.group_chat_window = GroupChatWindow()
        self.group_chat_window.show()

    def start_video_chat(self):
        if not clients:
            QtWidgets.QMessageBox.warning(self, "No Clients Connected", "No students are currently connected.")
            return
        for i, client in enumerate(clients):
            video_window = VideoChatWindow(client, f"Student {i+1} Video")
            video_window.show()
            video_chat_windows.append(video_window)

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', 12345))
        self.server_socket.listen(5)
        QtWidgets.QMessageBox.information(self, "Server Started", "Server started. Waiting for connections...")
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            QtWidgets.QMessageBox.information(self, "Client Connected", f"A student has connected from {client_address}")

    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    if message.startswith("SCREEN:"):
                        # Handle screen capture data
                        pass
                    else:
                        for client in clients:
                            if client != client_socket:
                                client.send(message.encode('utf-8'))
            except:
                clients.remove(client_socket)
                break

# Classes for ScreenWindow, GroupChatWindow, and VideoChatWindow would remain unchanged or be similarly enhanced.


def main():
    # Step 1: Set up environment based on platform
    setup_environment()

    # Step 2: Start the application
    app = QtWidgets.QApplication(sys.argv)
    main_window = RemoteAccessDashboard()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
