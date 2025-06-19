from flask import Flask, render_template, Response, request, jsonify
import cv2

app = Flask(__name__)
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
current_mode = 'ps2'  # ps2 or web

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control', methods=['POST'])
def control():
    global current_mode
    data = request.get_json()
    if data.get("mode") == "set":
        current_mode = data.get("value", "ps2")
        return jsonify({"status": "mode updated"})
    
    if current_mode != "web":
        return jsonify({"error": "Web control disabled"}), 403

    command = data.get('command')
    print(f"[WEB CMD] Received: {command}")
    # xử lý lệnh điều khiển robot tại đây
    return jsonify({"status": "ok"})

@app.route('/data')
def data():
    return jsonify({"message": f"Chế độ hiện tại: {current_mode.upper()}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
