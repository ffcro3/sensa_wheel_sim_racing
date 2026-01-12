import socket
import json
import pyvjoy
from pynput import mouse
from flask import Flask, render_template_string
import threading
import logging
import os
import sys
import tkinter as tk
from PIL import Image
import pystray
import subprocess

try:
    j = pyvjoy.VJoyDevice(1)
except:
    os._exit(1)

CURSO_FISICO_CELULAR = 45.0 
FATOR_EXPONENCIAL = 1.7
PESO_SUAVIDADE = 0.5
eixo_x_atual = 16384
rodando = False
app_rodando = True
active_button = mouse.Button.x1 

app = Flask(__name__)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def send_windows_notification(title, msg):
    vbs_path = os.path.join(os.environ["TEMP"], "sensa_notify.vbs")
    with open(vbs_path, "w") as f:
        f.write(f'Set objShell = CreateObject("WScript.Shell")\n')
        f.write(f'objShell.Popup "{msg}", 2, "{title}", 4096 + 64')
    subprocess.Popen(["wscript.exe", vbs_path], creationflags=subprocess.CREATE_NO_WINDOW)

def open_assign_window():
    def run_tk():
        root = tk.Tk()
        root.title("Hotkey Settings")
        root.geometry("340x180")
        root.configure(bg='#121212')
        root.attributes("-topmost", True)
        root.eval('tk::PlaceWindow . center')
        try:
            root.iconbitmap(resource_path("icon.ico"))
        except:
            pass

        def start_capture():
            btn_cap.config(text="LISTENING...", fg="#ffcc00")
            root.update()
            def on_click_once(x, y, button, pressed):
                global active_button
                if pressed:
                    active_button = button
                    root.after(0, lambda: finish_capture(button.name.upper(), lbl_status, btn_cap, root))
                    return False
            mouse.Listener(on_click=on_click_once).start()

        def finish_capture(btn_name, lbl, btn, rt):
            lbl.config(text=f"HOTKEY: {btn_name}", fg="#2ecc71")
            btn.config(text="CAPTURE NEW", fg="white")
            send_windows_notification("SensaWheel Pro", f"Hotkey updated: {btn_name}")
            rt.after(1000, rt.destroy)

        tk.Label(root, text="SENSAWHEEL CONFIG", bg='#121212', fg='white', font=("Arial", 10, "bold")).pack(pady=10)
        lbl_status = tk.Label(root, text=f"HOTKEY: {active_button.name.upper()}", bg='#121212', fg='#2ecc71', font=("Arial", 12))
        lbl_status.pack(pady=5)
        btn_cap = tk.Button(root, text="CAPTURE NEW", command=start_capture, bg="#333", fg="white", relief="flat", padx=20, pady=10)
        btn_cap.pack(pady=15)
        root.mainloop()
    
    threading.Thread(target=run_tk, daemon=True).start()

html_interface = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        * { box-sizing: border-box; touch-action: none; user-select: none; }
        body { margin: 0; background: #000; font-family: sans-serif; height: 100vh; display: flex; padding: 15px; gap: 15px; overflow: hidden; }
        .column { display: flex; flex-direction: column; flex: 1; gap: 15px; }
        button { flex: 1; border: none; border-radius: 25px; color: white; font-size: 2rem; font-weight: 900; box-shadow: inset 0 0 20px rgba(0,0,0,0.3); transition: transform 0.05s; display: flex; align-items: center; justify-content: center; }
        #btn-w { background: #27ae60; border-bottom: 6px solid #1e8449; }
        #btn-s { background: #c0392b; border-bottom: 6px solid #922b21; }
        #btn-e { background: #2980b9; border-bottom: 6px solid #21618c; }
        #btn-q { background: #8e44ad; border-bottom: 6px solid #6c3483; }
        button:active { transform: scale(0.95); filter: brightness(1.2); border-bottom: 2px solid transparent; }
    </style>
</head>
<body>
    <div class="column"><button id="btn-w">GAS</button><button id="btn-s">BRAKE</button></div>
    <div class="column"><button id="btn-e">UP</button><button id="btn-q">DOWN</button></div>
    <script>
        function setup(id, p, r) {
            const b = document.getElementById(id);
            b.addEventListener('touchstart', (e) => { e.preventDefault(); fetch(p); });
            b.addEventListener('touchend', (e) => { e.preventDefault(); fetch(r); });
        }
        setup('btn-w', '/p_w', '/r_w'); setup('btn-s', '/p_s', '/r_s');
        setup('btn-q', '/p_q', '/r_q'); setup('btn-e', '/p_e', '/r_e');
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(html_interface)
@app.route('/p_w')
def p_w(): j.set_axis(pyvjoy.HID_USAGE_Y, 32767); return "ok"
@app.route('/r_w')
def r_w(): j.set_axis(pyvjoy.HID_USAGE_Y, 0); return "ok"
@app.route('/p_s')
def p_s(): j.set_axis(pyvjoy.HID_USAGE_Z, 32767); return "ok"
@app.route('/r_s')
def r_s(): j.set_axis(pyvjoy.HID_USAGE_Z, 0); return "ok"
@app.route('/p_q')
def p_q(): j.set_button(3, 1); return "ok"
@app.route('/r_q')
def r_q(): j.set_button(3, 0); return "ok"
@app.route('/p_e')
def p_e(): j.set_button(4, 1); return "ok"
@app.route('/r_e')
def r_e(): j.set_button(4, 0); return "ok"

def volante_loop():
    global eixo_x_atual, rodando
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 8080))
    sock.settimeout(0.01)
    while app_rodando:
        try:
            data, _ = sock.recvfrom(1024)
            if rodando:
                payload = json.loads(data.decode('utf-8'))
                val = payload['values'][1]
                norm = max(-1, min(1, val / CURSO_FISICO_CELULAR))
                curva = (1 if norm >= 0 else -1) * (abs(norm) ** FATOR_EXPONENCIAL)
                target = int(16384 + (curva * 16384))
                eixo_x_atual += (target - eixo_x_atual) * PESO_SUAVIDADE
                j.set_axis(pyvjoy.HID_USAGE_X, int(eixo_x_atual))
        except: continue

def on_mouse_click(x, y, button, pressed):
    global rodando
    if pressed and button == active_button:
        rodando = not rodando
        send_windows_notification("SensaWheel Pro", "ACTIVE" if rodando else "DISABLED")

if __name__ == "__main__":
    send_windows_notification("SensaWheel Pro", "SensaWheel Started!")
    threading.Thread(target=volante_loop, daemon=True).start()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False), daemon=True).start()
    mouse.Listener(on_click=on_mouse_click).start()

    img = Image.open(resource_path("icon.png"))
    menu = pystray.Menu(
        pystray.MenuItem("Assign Hotkey", open_assign_window),
        pystray.MenuItem("Exit", lambda icon: os._exit(0))
    )
    icon = pystray.Icon("SensaWheel", img, "SensaWheel Pro", menu)
    icon.run()