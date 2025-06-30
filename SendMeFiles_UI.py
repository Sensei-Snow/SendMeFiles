#-----------------------------------------------------------------Importations
import sys
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic
from PyQt6.QtCore import QStringListModel
import json
import socket
import subprocess
import os
import platform
import pyperclip

#-----------------------------------------------------------------Qt Launcher Window Class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #-----------------------------------------------------------------Set Style
        uic.loadUi("SendMeFiles.ui", self)
        QApplication.setStyle("Windows")  # Fusion or WindowsVista
        self.setWindowIcon(QIcon("static/assets/favicon.ico"))

        #-----------------------------------------------------------------Initialize List Model
        self.extensions_list = []
        self.model = QStringListModel(self.extensions_list)
        self.listView.setModel(self.model)

        #-----------------------------------------------------------------Connect Buttons to Functions
        self.button_add.clicked.connect(lambda: self.add_extension())
        self.button_remove.clicked.connect(lambda: self.remove_all_settings())
        self.slider_size.valueChanged.connect(self.slider_changed)
        self.button_save.clicked.connect(lambda: self.save_json())
        self.button_start.clicked.connect(lambda: self.start())
        self.button_stop.clicked.connect(lambda: self.stop())
        self.button_copy.clicked.connect(lambda: self.copy_address())

        #-----------------------------------------------------------------Hide Useless Widgets
        self.label_infinite.hide()
        self.label_ip.hide()
        self.button_stop.hide()
        self.button_copy.hide()

        #-----------------------------------------------------------------Initialize Settings
        self.init()

    #-----------------------------------------------------------------Initialize or update settings
    def init(self):
        with open("config.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        extensions_json = data["extensions"]
        size_json = data["size"]

        self.model.setStringList(extensions_json)
        if size_json == 1000:
            self.label_infinite.show()
            self.lcdNumber.hide()
            self.label_mo.hide()
            self.slider_size.setValue(size_json)
        else:
            self.lcdNumber.display(size_json)
            self.slider_size.setValue(size_json)

    #-----------------------------------------------------------------Add Extensions to Settings
    def add_extension(self):
        ext = self.textEdit_extensions.toPlainText().strip()

        if ext and not ext.startswith('.'):
            ext = '.' + ext

        if ext and ext not in self.extensions_list:
            self.extensions_list.append(ext)
            self.model.setStringList(self.extensions_list)

        self.textEdit_extensions.clear()

    #-----------------------------------------------------------------Add Size to Settings
    def slider_changed(self, valeur):
        if valeur == 1000:
            self.label_infinite.show()
            self.label_mo.hide()
            self.lcdNumber.hide()
        else:
            self.label_infinite.hide()
            self.label_mo.show()
            self.lcdNumber.show()
            self.lcdNumber.display(valeur)

    #-----------------------------------------------------------------Save All Settings
    def save_json(self):
        with open("config.json", "w") as f:
            json.dump({"extensions": self.extensions_list, "size": self.slider_size.value()}, f, indent=4)

    #-----------------------------------------------------------------Remove all Settings
    def remove_all_settings(self):
        self.extensions_list = []
        with open("config.json", "w") as f:
            json.dump({"extensions": [], "size": 0}, f, indent=4)
        self.init()

    #-----------------------------------------------------------------Get Local IP Address
    def get_preferred_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    #-----------------------------------------------------------------Copy Sharing Address
    def copy_address(self):
        address = f"http://{self.get_preferred_local_ip()}:5000"
        pyperclip.copy(address)

    #-----------------------------------------------------------------Start Sharing
    def start(self):
        script_name = "SendMeFiles_Server.py"

        script_path = os.path.join(os.path.dirname(__file__), script_name)

        system = platform.system()

        interpreter = sys.executable

        try:
            if system == "Windows":
                subprocess.Popen(f'start \"\" \"{interpreter}\" \"{script_path}\"', shell=True)

            elif system == "Linux":
                terminal_commands = [
                    f'gnome-terminal -- {interpreter} "{script_path}"',
                    f'x-terminal-emulator -e {interpreter} "{script_path}"',
                    f'xterm -e {interpreter} "{script_path}"',
                    f'konsole -e {interpreter} "{script_path}"',
                ]
                launched = False
                for cmd in terminal_commands:
                    try:
                        subprocess.Popen(cmd, shell=True)
                        launched = True
                        break
                    except FileNotFoundError:
                        continue

                if not launched:
                    print("[ERROR] -- Linux terminal not found")
                    print("Maybe you have a too specific distribution, desktop environment or terminal...")
                    print("If you want, the code to modify is in \"SendMeFiles_UI.py\" beyond the line 130")

            elif system == "Darwin":
                subprocess.Popen(["osascript", "-e", f'tell application "Terminal" to do script "{interpreter} \\"{script_path}\\""'])

            else:
                print("[ERROR] -- System not supported")

        except FileNotFoundError:
            print(f"[ERROR] -- {script_name} not found")
        except Exception as e:
            print(f"[ERROR] -- There was an error during starting {script_name} : {e}")

        self.label_ip.setText(f"Adresse de partage : http://{self.get_preferred_local_ip()}:5000")
        self.label_ip.show()
        self.button_start.hide()
        self.button_stop.show()
        self.button_copy.show()

    #-----------------------------------------------------------------Stop sharing
    def stop(self):
        script_name = "SendMeFiles_Server.py"

        system = platform.system()

        try:
            if system == "Windows":
                subprocess.run(f'wmic process where "CommandLine like \'%{script_name}%\'" call terminate', shell=True, check=True)

            elif system in ["Linux", "Darwin"]:
                subprocess.run(f"pkill -f {script_name}", shell=True, check=True)

            else:
                print("[ERROR] -- System not supported")

        except subprocess.CalledProcessError:
            print(f"[ERROR] -- Failed to close {script_name}")

        self.label_ip.hide()
        self.button_stop.hide()
        self.button_copy.hide()
        self.button_start.show()

#-----------------------------------------------------------------Main code -> Show The Window
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())