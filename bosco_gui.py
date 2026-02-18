"""
Bosco Core - GUI Server with Robot Avatar
"""

from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO
import threading
import time
import subprocess
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bosco-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

assistant_state = {"status": "idle", "message": "", "last_command": "", "response": ""}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Bosco Assistant</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: "Segoe UI", sans-serif; background: transparent; overflow: hidden; }
.widget-container { position: fixed; bottom: 20px; right: 20px; z-index: 10000; }
.robot-face {
    width: 120px; height: 120px;
    background: linear-gradient(145deg, #1a1a2e, #16213e);
    border-radius: 50%; position: relative;
    cursor: pointer;
    box-shadow: 0 0 30px rgba(0, 255, 255, 0.3);
    border: 3px solid #00d4ff;
    transition: transform 0.3s ease;
}
.robot-face:hover { transform: scale(1.05); }
.robot-face.listening { animation: pulse-green 1s infinite; border-color: #00ff88; }
.robot-face.processing { animation: pulse-yellow 0.5s infinite; border-color: #ffd700; }
.robot-face.speaking { animation: pulse-cyan 0.3s infinite; }
@keyframes pulse-green { 0%,100% { box-shadow: 0 0 30px rgba(0,255,136,0.3); } 50% { box-shadow: 0 0 50px rgba(0,255,136,0.6); } }
@keyframes pulse-yellow { 0%,100% { box-shadow: 0 0 30px rgba(255,215,0,0.3); } 50% { box-shadow: 0 0 50px rgba(255,215,0,0.6); } }
@keyframes pulse-cyan { 0%,100% { box-shadow: 0 0 30px rgba(0,255,255,0.4); } 50% { box-shadow: 0 0 60px rgba(0,255,255,0.8); } }
.eyes { position: absolute; top: 35%; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; }
.eye { width: 22px; height: 22px; background: #00d4ff; border-radius: 50%; box-shadow: 0 0 15px #00d4ff; }
.listening .eye { background: #00ff88; box-shadow: 0 0 20px #00ff88; height: 18px; border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%; }
.mouth { position: absolute; bottom: 25%; left: 50%; transform: translateX(-50%); width: 30px; height: 8px; background: #00d4ff; border-radius: 10px; box-shadow: 0 0 10px #00d4ff; }
.speaking .mouth { height: 15px; border-radius: 50%; animation: talk 0.2s infinite alternate; }
@keyframes talk { 0% { width: 25px; height: 10px; } 100% { width: 35px; height: 18px; } }
.status-dot { position: absolute; top: 5px; right: 5px; width: 12px; height: 12px; background: #00ff88; border-radius: 50%; animation: status-pulse 2s infinite; }
@keyframes status-pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
.chat-panel { position: fixed; bottom: 160px; right: 20px; width: 350px; max-height: 400px; background: rgba(26,26,46,0.95); border-radius: 15px; border: 2px solid #00d4ff; display: none; flex-direction: column; }
.chat-panel.active { display: flex; }
.chat-header { background: linear-gradient(90deg, #00d4ff, #0099cc); padding: 12px 15px; color: white; font-weight: bold; }
.chat-messages { flex: 1; overflow-y: auto; padding: 15px; max-height: 280px; }
.message { margin-bottom: 10px; padding: 8px 12px; border-radius: 10px; font-size: 13px; }
.message.user { background: rgba(0,212,255,0.2); color: #00d4ff; margin-left: 20px; }
.message.bosco { background: rgba(0,255,136,0.15); color: #00ff88; margin-right: 20px; }
.chat-input { padding: 10px; border-top: 1px solid rgba(0,212,255,0.3); display: flex; }
.chat-input input { flex: 1; padding: 8px 12px; border: 1px solid #00d4ff; border-radius: 20px; background: rgba(0,0,0,0.3); color: white; outline: none; }
.chat-input button { margin-left: 8px; padding: 8px 15px; background: #00d4ff; border: none; border-radius: 20px; color: #1a1a2e; font-weight: bold; cursor: pointer; }
.quick-actions { position: fixed; bottom: 150px; right: 160px; display: flex; flex-direction: column; gap: 8px; opacity: 0; transition: opacity 0.3s; }
.robot-face:hover + .quick-actions, .quick-actions:hover { opacity: 1; }
.action-btn { width: 40px; height: 40px; background: rgba(26,26,46,0.9); border: 2px solid #00d4ff; border-radius: 10px; color: #00d4ff; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.control-panel { position: fixed; top: 20px; right: 20px; background: rgba(26,26,46,0.95); border: 2px solid #00d4ff; border-radius: 15px; padding: 15px; width: 300px; display: none; }
.control-panel.active { display: block; }
.control-panel h3 { color: #00d4ff; margin-bottom: 15px; }
.control-group { margin-bottom: 15px; }
.control-group label { display: block; color: #aaa; font-size: 12px; margin-bottom: 5px; }
.control-group input { width: 100%; padding: 8px; background: rgba(0,0,0,0.3); border: 1px solid #00d4ff; border-radius: 5px; color: white; margin-bottom: 5px; }
.control-row { display: flex; gap: 10px; }
.control-row button { flex: 1; padding: 8px; background: rgba(0,212,255,0.2); border: 1px solid #00d4ff; border-radius: 5px; color: #00d4ff; cursor: pointer; }
</style>
</head>
<body>
<div class="widget-container">
    <div class="robot-face" id="robotFace" onclick="toggleChat()">
        <div class="status-dot"></div>
        <div class="eyes"><div class="eye"></div><div class="eye"></div></div>
        <div class="mouth"></div>
    </div>
    <div class="quick-actions">
        <button class="action-btn" onclick="showControlPanel()" title="PC Control">🎮</button>
    </div>
</div>
<div class="chat-panel" id="chatPanel">
    <div class="chat-header">🤖 Bosco Assistant</div>
    <div class="chat-messages" id="chatMessages"><div class="message bosco">Hello! I'm Bosco. How can I help?</div></div>
    <div class="chat-input">
        <input type="text" id="userInput" placeholder="Type a command..." onkeypress="if(event.key==='Enter')sendMessage()">
        <button onclick="sendMessage()">Send</button>
    </div>
</div>
<div class="control-panel" id="controlPanel">
    <h3>🎮 PC Control</h3>
    <div class="control-group">
        <label>Open App / Type Command</label>
        <input type="text" id="appName" placeholder="e.g., notepad, type hello">
        <div class="control-row">
            <button onclick="openApp()">Open</button>
            <button onclick="typeText()">Type</button>
        </div>
    </div>
    <div class="control-group">
        <label>Run Terminal</label>
        <input type="text" id="terminalCmd" placeholder="e.g., ls -la">
        <button onclick="runCommand()">Run</button>
    </div>
    <div class="control-group">
        <div class="control-row">
            <button onclick="screenshot()">📸 Screenshot</button>
            <button onclick="showDesktop()">🖥️</button>
        </div>
    </div>
    <button onclick="closeControlPanel()">Close</button>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
<script>
const socket = io();
socket.on("status_update", d => document.getElementById("robotFace").className = "robot-face " + d.status);
function toggleChat() { document.getElementById("chatPanel").classList.toggle("active"); }
function showControlPanel() { document.getElementById("controlPanel").classList.toggle("active"); }
function closeControlPanel() { document.getElementById("controlPanel").classList.remove("active"); }
function sendMessage() {
    const m = document.getElementById("userInput").value.trim();
    if (!m) return;
    addMessage(m, "user");
    document.getElementById("userInput").value = "";
    socket.emit("user_message", {message: m});
    socket.emit("set_status", {status: "processing"});
}
function addMessage(t, s) {
    const d = document.createElement("div");
    d.className = "message " + s;
    d.textContent = t;
    document.getElementById("chatMessages").appendChild(d);
    document.getElementById("chatMessages").scrollTop = 9999;
}
socket.on("bosco_response", d => { addMessage(d.response, "bosco"); socket.emit("set_status", {status: "idle"}); });
function openApp() {
    const v = document.getElementById("appName").value;
    if (v) { socket.emit("pc_control", {action: "open_app", value: v}); document.getElementById("appName").value = ""; }
}
function typeText() {
    const v = document.getElementById("appName").value;
    if (v) { socket.emit("pc_control", {action: "enhanced_type", value: v}); document.getElementById("appName").value = ""; }
}
function runCommand() {
    const v = document.getElementById("terminalCmd").value;
    if (v) { socket.emit("pc_control", {action: "run_command", value: v}); document.getElementById("terminalCmd").value = ""; }
}
function screenshot() { socket.emit("pc_control", {action: "screenshot", value: ""}); }
function showDesktop() { socket.emit("pc_control", {action: "show_desktop", value: ""}); }
</script>
</body>
</html>
'''

try:
    import sys
    sys.path.insert(0, '/home/tradler/Desktop/bosco-core')
    from bosco_os.brain.llm_client import get_llm
    from bosco_os.capabilities.system.pc_control import PCControl
    from bosco_os.capabilities.system.enhanced_automation import EnhancedAutomation
    pc_control = PCControl()
    automation = EnhancedAutomation()
except Exception as e:
    print(f"Warning: {e}")
    pc_control = None
    automation = None
    get_llm = None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def get_status():
    return jsonify(assistant_state)

@app.route('/api/set_status', methods=['POST'])
def set_status():
    assistant_state['status'] = request.json.get('status', 'idle')
    socketio.emit('status_update', {'status': assistant_state['status']})
    return jsonify({'success': True})

@app.route('/api/pc_control', methods=['POST'])
def pc_control_api():
    action = request.json.get('action', '')
    value = request.json.get('value', '')
    result = {'success': False, 'message': ''}
    try:
        if action == 'open_app' and pc_control:
            result['message'] = pc_control.open_app(value)
            result['success'] = True
        elif action == 'enhanced_type' and automation:
            result['message'] = automation.process_command(value)
            result['success'] = True
        elif action == 'run_command':
            proc = subprocess.Popen(value, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, _ = proc.communicate()
            result['message'] = out.decode('utf-8', errors='ignore')[:500]
            result['success'] = True
        elif action == 'screenshot' and pc_control:
            result['message'] = pc_control.screenshot()
            result['success'] = True
        elif action == 'show_desktop' and pc_control:
            pc_control.press_key('super+d')
            result['message'] = 'Desktop shown'
            result['success'] = True
    except Exception as e:
        result['message'] = str(e)
    return jsonify(result)

@app.route('/api/chat', methods=['POST'])
def chat():
    message = request.json.get('message', '')
    if not message:
        return jsonify({'response': 'No message'})
    assistant_state['status'] = 'processing'
    socketio.emit('status_update', {'status': 'processing'})
    try:
        keywords = ['open', 'write', 'type', 'run', 'screenshot']
        if any(k in message.lower() for k in keywords) and automation:
            r = automation.process_command(message)
            response = '\n'.join(r) if isinstance(r, list) else r
        elif get_llm:
            response = get_llm().chat(message, "You are Bosco, a helpful AI assistant.")
        else:
            response = f"Got: {message}"
        socketio.emit('bosco_response', {'response': response})
        def reset(): 
            time.sleep(2)
            socketio.emit('status_update', {'status': 'idle'})
        threading.Thread(target=reset, daemon=True).start()
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f'Error: {e}'})

@socketio.on('user_message')
def handle_msg(data):
    chat()

@socketio.on('set_status')
def handle_status(data):
    assistant_state['status'] = data.get('status', 'idle')

def run_gui_server():
    print("\n🤖 BOSCO CORE GUI")
    print("Open http://localhost:5000 in your browser!")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    run_gui_server()
