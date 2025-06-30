#-----------------------------------------------------------------Importations
from flask import Flask, request, render_template
import os
import json
from werkzeug.utils import secure_filename
import threading
import time
import socket
from plyer import notification

#-----------------------------------------------------------------Define Variables and Files Path
upload_folder = 'uploads'
os.makedirs(upload_folder, exist_ok=True)

icon_name = "static/assets/favicon.ico"
icon_path = os.path.join(os.path.dirname(__file__), icon_name)

hostname = socket.gethostname()

infos = {
    'hostname': hostname
}

#-----------------------------------------------------------------Check Settings
def watcher():
    while True:
        global extensions_json
        global size_json

        with open("config.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        extensions_json = data["extensions"]
        size_json = data["size"]

        time.sleep(1)

#-----------------------------------------------------------------Define Sharing Interface
app = Flask(__name__)

@app.route('/')
def upload_form():
    return render_template('SendMeFiles_Index.html', infos=infos)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return 'Aucun fichier trouvé', 400
    files = request.files.getlist('files')
    for file in files:
        if file.filename == '':
            return render_template('SendMeFiles_NoFiles.html')

        filename = secure_filename(file.filename)

        extension = os.path.splitext(filename)[1].lower()

        if extension not in extensions_json:
            return render_template('SendMeFiles_Refused.html')

        file.stream.seek(0, os.SEEK_END)
        taille_bytes = file.stream.tell()
        file.stream.seek(0)

        taille_mo = taille_bytes / (1024 * 1024)

        if taille_mo > size_json:
            return render_template('SendMeFiles_Refused.html')

        file.save(os.path.join(upload_folder, file.filename))
        notification.notify(title="SenMeFiles - Information",
                            message=f"Someone send you {filename}",
                            timeout=7, app_icon=icon_path)
    return render_template('SendMeFiles_Success.html')

#-----------------------------------------------------------------Launch Sharing Interface
def launcher():
    app.run(host='0.0.0.0', port=5000, debug=True)

#-----------------------------------------------------------------Main code -> Launch Sharing Interface + Check Settings
if __name__ == '__main__':
    threading.Thread(target=watcher, daemon=True).start()
    launcher()