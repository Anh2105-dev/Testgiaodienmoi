from flask import Flask, request, Response #Tạo web server - Nhận dữ liệu lệnh điều khiển gửi từ client - Trả dữ liệu video dạng stream
import cv2 #OpenCV để xử lý và lấy hình ảnh từ camera
import RPi.GPIO as GPIO #Điều khiển GPIO trên Raspberry Pi
import time
import board
import busio
from adafruit_pca9685 import PCA9685   

app = Flask(__name__)

i2c = busio.I2C(board.SCL, board.SDA)

pca = PCA9685(i2c) #Tạo đối tượng PCA9685
pca.frequency = 1000 #Tần số cho động cơ 

# Gán các kênh băm xung cho động cơ trên mạch PCA9685
LPWM1 = pca.channels[0]
RPWM1 = pca.channels[1]
LPWM2 = pca.channels[2]
RPWM2 = pca.channels[3]
LPWM3 = pca.channels[4]
RPWM3 = pca.channels[5]
LPWM4 = pca.channels[6]
RPWM4 = pca.channels[7]
#Gắn các kênh cho động cơ bơm lấy mẫu nước
in1 = pca.channels[8]
in2 = pca.channels[9]
in3 = pca.channels[10]
in4 = pca.channels[11]

# Thiết lập GPIO điều khiển động cơ
#GPIO 04 = in1_L298_1
#GPIO 18 = in2_L298_1
#GPIO 27 = in3_L298_1
#GPIO 22 = in4_L298_1

#GPIO 23 = in1_L298_2
#GPIO 24 = in2_L298_2
#GPIO 25 = in3_L298_2
#GPIO 05 = in4_L298_2

#GPIO 06 = in1_L298_3
#GPIO 12 = in2_L298_3
#GPIO 13 = in3_L298_3
#GPIO 19 = in4_L298_3

#GPIO 16 = in1_L298_4
#GPIO 26 = in2_L298_4
#GPIO 20 = in3_L298_4
#GPIO 21 = in4_L298_4

#GPIO 17 = light_on
# Thiết lập các chân GPIO làm OUTPUT
GPIO.setmode(GPIO.BCM) #Để dùng đúng cách đánh số chân.
GPIO.setwarnings(False) #Tắt cảnh báo khi sử dụng lại các chân GPIO
gpio_pins = [4, 18, 27, 22, 23, 24, 25, 5, 6, 12, 13, 19, 16, 26, 20, 21, 17]
for pin in gpio_pins:
    GPIO.setup(pin, GPIO.OUT)

@app.route('/control', methods=['POST']) #Nhận lệnh từ web gửi xuống Ras
def control():
    cmd = request.form['cmd'] 
    print("Lệnh nhận:", cmd) #In ra terminal để kiểm tra lệnh

    if cmd == "Tien":
        GPIO.output(4, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)        
        #duty = int(speed * 0xFFFF)
        LPWM1.duty_cycle = 0
        RPWM1.duty_cycle = 0
        LPWM2.duty_cycle = 0xFFFF #duty
        RPWM2.duty_cycle = 0xFFFF 
    elif cmd == "Tientrai":
        GPIO.output(4, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22, GPIO.HIGH) 

        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)  
        #duty = int(speed * 0xFFFF)
        LPWM1.duty_cycle = 0
        RPWM1.duty_cycle = 0xFFFF 
        LPWM2.duty_cycle = 0xFFFF 
        RPWM2.duty_cycle = 0xFFFF
    elif cmd == "Tienphai":
        GPIO.output(4, GPIO.LOW)
        GPIO.output(18, GPIO.HIGH)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)  
        #duty = int(speed * 0xFFFF)
        LPWM1.duty_cycle = 0xFFFF #duty
        RPWM1.duty_cycle = 0 
        LPWM2.duty_cycle = 0xFFFF 
        RPWM2.duty_cycle = 0xFFFF
    elif cmd == "Lui":
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(5, GPIO.LOW)  
        #duty = int(speed * 0xFFFF)
        LPWM1.duty_cycle = 0xFFFF #duty
        RPWM1.duty_cycle = 0xFFFF 
        LPWM2.duty_cycle = 0
        RPWM2.duty_cycle = 0
    elif cmd == "Luitrai":
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(5, GPIO.HIGH)  
        #duty = int(speed * 0xFFFF)
        LPWM1.duty_cycle = 0xFFFF #duty
        RPWM1.duty_cycle = 0xFFFF 
        LPWM2.duty_cycle = 0
        RPWM2.duty_cycle = 0xFFFF
    elif cmd == "Luiphai":
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.HIGH)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(5, GPIO.LOW)  
        #duty = int(speed * 0xFFFF)
        LPWM1.duty_cycle = 0xFFFF #duty
        RPWM1.duty_cycle = 0xFFFF 
        LPWM2.duty_cycle = 0xFFFF
        RPWM2.duty_cycle = 0
    elif cmd == "Trai":
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(5, GPIO.LOW)  
        #duty = int(speed * 0xFFFF)
        LPWM1.duty_cycle = 0xFFFF #duty
        RPWM1.duty_cycle = 0
        LPWM2.duty_cycle = 0xFFFF #duty
        RPWM2.duty_cycle = 0
    elif cmd == "Phai":
        GPIO.output(4, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)      
        #duty = int(speed * 0xFFFF)
        LPWM1.duty_cycle = 0
        RPWM1.duty_cycle = 0xFFFF #duty
        LPWM2.duty_cycle = 0
        RPWM2.duty_cycle = 0xFFFF #duty
    elif cmd == "Quaytrai":
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)
        #duty = int(speed * 0xFFFF)
        LPWM1.duty_cycle = 0xFFFF #duty
        RPWM1.duty_cycle = 0
        LPWM2.duty_cycle = 0
        RPWM2.duty_cycle = 0xFFFF #duty
    elif cmd == "Quayphai":
        GPIO.output(4, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(5, GPIO.LOW)
        #duty = int(speed * 0xFFFF)
        LPWM1.duty_cycle = 0
        RPWM1.duty_cycle = 0xFFFF #duty
        LPWM2.duty_cycle = 0xFFFF #duty
        RPWM2.duty_cycle = 0 
    elif cmd == "Lan":
        GPIO.output(6, GPIO.HIGH)
        GPIO.output(12, GPIO.LOW)
        GPIO.output(13, GPIO.HIGH)
        GPIO.output(19, GPIO.LOW) 
        
        GPIO.output(16, GPIO.HIGH)
        GPIO.output(26, GPIO.LOW)
        GPIO.output(20, GPIO.HIGH)
        GPIO.output(21, GPIO.LOW) 
        #duty = int(speed * 0xFFFF)
        LPWM3.duty_cycle = 0xFFFF #duty
        RPWM3.duty_cycle = 0xFFFF
        LPWM4.duty_cycle = 0xFFFF #duty
        RPWM4.duty_cycle = 0xFFFF  
    elif cmd == "Nghientruoc_Down":
        GPIO.output(6, GPIO.HIGH)
        GPIO.output(12, GPIO.LOW)
        GPIO.output(13, GPIO.HIGH)
        GPIO.output(19, GPIO.LOW) 
        
        GPIO.output(16, GPIO.LOW)
        GPIO.output(26, GPIO.LOW)
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.LOW) 
        #duty = int(speed * 0xFFFF)
        LPWM3.duty_cycle = 0xFFFF
        RPWM3.duty_cycle = 0xFFFF #duty
        LPWM4.duty_cycle = 0
        RPWM4.duty_cycle = 0  
    elif cmd == "Nghientruoc_Up":
        GPIO.output(6, GPIO.LOW)
        GPIO.output(12, GPIO.HIGH)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(19, GPIO.HIGH) 
        
        GPIO.output(16, GPIO.LOW)
        GPIO.output(26, GPIO.LOW)
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.LOW) 
        #duty = int(speed * 0xFFFF)
        LPWM3.duty_cycle = 0xFFFF #duty
        RPWM3.duty_cycle = 0xFFFF 
        LPWM4.duty_cycle = 0
        RPWM4.duty_cycle = 0 
    elif cmd == "Nghientrai_Down":
        GPIO.output(6, GPIO.HIGH)
        GPIO.output(12, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(19, GPIO.LOW) 
        
        GPIO.output(16, GPIO.HIGH)
        GPIO.output(26, GPIO.LOW)
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.LOW) 
        #duty = int(speed * 0xFFFF)
        LPWM3.duty_cycle = 0xFFFF #duty
        RPWM3.duty_cycle = 0
        LPWM4.duty_cycle = 0xFFFF 
        RPWM4.duty_cycle = 0 
    elif cmd == "Nghientrai_Up":
        GPIO.output(6, GPIO.LOW)
        GPIO.output(12, GPIO.HIGH)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(19, GPIO.LOW) 
        
        GPIO.output(16, GPIO.LOW)
        GPIO.output(26, GPIO.HIGH)
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.LOW) 
        #duty = int(speed * 0xFFFF)
        LPWM3.duty_cycle = 0xFFFF #duty
        RPWM3.duty_cycle = 0 
        LPWM4.duty_cycle = 0xFFFF
        RPWM4.duty_cycle = 0
    elif cmd == "Nghienphai_Down":
        GPIO.output(6, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
        GPIO.output(13, GPIO.HIGH)
        GPIO.output(19, GPIO.LOW) 
        
        GPIO.output(16, GPIO.LOW)
        GPIO.output(26, GPIO.LOW)
        GPIO.output(20, GPIO.HIGH)
        GPIO.output(21, GPIO.LOW) 
        #duty = int(speed * 0xFFFF)
        LPWM3.duty_cycle = 0
        RPWM3.duty_cycle = 0xFFFF #duty
        LPWM4.duty_cycle = 0xFFFF
        RPWM4.duty_cycle = 0  
    elif cmd == "Nghienphai_Up":
        GPIO.output(6, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(19, GPIO.HIGH) 
        
        GPIO.output(16, GPIO.LOW)
        GPIO.output(26, GPIO.LOW)
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.HIGH) 
        #duty = int(speed * 0xFFFF)
        LPWM3.duty_cycle = 0
        RPWM3.duty_cycle = 0xFFFF #duty
        LPWM4.duty_cycle = 0xFFFF
        RPWM4.duty_cycle = 0       
    elif cmd == "Nghiensau_Down":
        GPIO.output(6, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(19, GPIO.LOW) 
        
        GPIO.output(16, GPIO.HIGH)
        GPIO.output(26, GPIO.LOW)
        GPIO.output(20, GPIO.HIGH)
        GPIO.output(21, GPIO.LOW) 
        #duty = int(speed * 0xFFFF)
        LPWM3.duty_cycle = 0
        RPWM3.duty_cycle = 0
        LPWM4.duty_cycle = 0xFFFF
        RPWM4.duty_cycle = 0xFFFF #duty  
    elif cmd == "Nghiensau_Up":
        GPIO.output(6, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(19, GPIO.LOW) 
        
        GPIO.output(16, GPIO.LOW)
        GPIO.output(26, GPIO.HIGH)
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.HIGH) 
        #duty = int(speed * 0xFFFF)
        LPWM3.duty_cycle = 0
        RPWM3.duty_cycle = 0
        LPWM4.duty_cycle = 0xFFFF
        RPWM4.duty_cycle = 0xFFFF #duty  
    elif cmd == "Batden":
        GPIO.output(17, GPIO.HIGH) 
    elif cmd == "Tatden":
        GPIO.output(17, GPIO.HIGH)
    elif cmd == "Laynuoc":
        in1.duty_cycle = 0xFFFF 
        in2.duty_cycle = 0
        in3.duty_cycle = 0
        in4.duty_cycle = 0
    elif cmd == "Daynuoc":
        in1.duty_cycle = 0
        in2.duty_cycle = 0
        in3.duty_cycle = 0xFFFF 
        in4.duty_cycle = 0  
    elif cmd == "Dunglaynuoc":
        in1.duty_cycle = 0
        in2.duty_cycle = 0
        in3.duty_cycle = 0
        in4.duty_cycle = 0        
    elif cmd == "Dung":
        GPIO.output(4, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(5, GPIO.LOW)  

        GPIO.output(6, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(19, GPIO.LOW) 
        
        GPIO.output(16, GPIO.LOW)
        GPIO.output(26, GPIO.LOW)
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.LOW) 

        LPWM1.duty_cycle = 0
        RPWM1.duty_cycle = 0
        LPWM2.duty_cycle = 0
        RPWM2.duty_cycle = 0
        LPWM3.duty_cycle = 0
        RPWM3.duty_cycle = 0
        LPWM4.duty_cycle = 0
        RPWM4.duty_cycle = 0

    return "OK" #Trả về "OK" để xác nhận với client

camera = cv2.VideoCapture(0) #Mở camera mặc định (index 0)
#Đặt độ phân giải khung hình video: 1280x720
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
def generate_video():
    while True:
        success, frame = camera.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame) #Đọc frame từ camera sau đó Mã hoá thành .jpg
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n') #Trả lại từng đoạn ảnh theo chuẩn MJPEG stream để client hiển thị liên tục

@app.route('/video_feed')
def video_feed(): #gọi hàm generate_video để stream từ camera
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame') #mimetype='multipart/x-mixed-replace' cho phép stream nhiều ảnh liên tục như 1 video

app.run(host='0.0.0.0', port=5000) #Khởi chạy Flask server
