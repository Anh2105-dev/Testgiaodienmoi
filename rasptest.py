from flask import Flask, request, Response
import cv2
import RPi.GPIO as GPIO

app = Flask(__name__)

# Thiết lập GPIO điều khiển động cơ
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
pwm = GPIO.PWM(17, 100)
pwm.start(0)

@app.route('/control', methods=['POST'])
def control():
    cmd = request.form['cmd']
    print("Lệnh nhận:", cmd)

    # Ví dụ điều khiển bằng PWM đơn giản
    if cmd == "forward":
        pwm.ChangeDutyCycle(70)
    elif cmd == "backward":
        pwm.ChangeDutyCycle(30)
    elif cmd == "dive":
    # Bật động cơ lặn
        GPIO.output(22, GPIO.HIGH)  # ví dụ chân 22
    elif cmd == "surface":
        # Bật động cơ nổi
        GPIO.output(22, GPIO.LOW)  # hoặc ngược lại
    else:
        pwm.ChangeDutyCycle(0)

    return "OK"

# Stream video
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
def generate_video():
    while True:
        success, frame = camera.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

app.run(host='0.0.0.0', port=5000)
