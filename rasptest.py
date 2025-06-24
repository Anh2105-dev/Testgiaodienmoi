from flask import Flask, request, Response #Tạo web server - Nhận dữ liệu lệnh điều khiển gửi từ client - Trả dữ liệu video dạng stream
import cv2 #OpenCV để xử lý và lấy hình ảnh từ camera
import RPi.GPIO as GPIO #Điều khiển GPIO trên Raspberry Pi
from flask import Response, stream_with_context
import json
import time
import board
import busio
import adafruit_bmp280
from adafruit_pca9685 import PCA9685
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250

app = Flask(__name__)

i2c = busio.I2C(board.SCL, board.SDA)

# MPU9250 (IMU)
mpu = MPU9250(
    address_ak=AK8963_ADDRESS,
    address_mpu_master=MPU9050_ADDRESS_68,
    bus=1,
    gfs=GFS_250,  # Gyroscope full scale
    afs=AFS_2G,   # Accelerometer full scale
    mfs=AK8963_BIT_16,  # Magnetometer resolution
    mode=AK8963_MODE_C100HZ
)
try:
    mpu.configure()  # Apply settings
except Exception as e:
    print("Không thể cấu hình từ kế, bỏ qua magnetometer:", e)

# BMP280 (áp suất & nhiệt độ)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
bmp280.sea_level_pressure = 1013.25  # Điều chỉnh theo vị trí thực

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

mode = "web"  # hoặc "ps2"

@app.route('/set_mode', methods=['POST'])
def set_mode():
    global mode
    mode = request.form.get('mode', 'web')
    print("Đã chuyển chế độ sang:", mode)
    return "OK"

@app.route('/control', methods=['POST'])
def control():
    cmd = request.form.get('cmd', '')

    def parse_pwm(value):
        try:
            return int(float(value))
        except:
            return 0

    pwmLeftPS2 = parse_pwm(request.form.get('pwmLeftPS2', 0))
    pwmRightPS2 = parse_pwm(request.form.get('pwmRightPS2', 0))

    if mode == "web" and cmd.endswith("PS2"):
        print("Chế độ Web đang hoạt động. Bỏ qua lệnh PS2:", cmd)
        return "IGNORED"
    elif mode == "ps2" and not cmd.endswith("PS2"):
        print("Chế độ PS2 đang hoạt động. Bỏ qua lệnh Web:", cmd)
        return "IGNORED"

    print(f"Đang xử lý lệnh: {cmd} (PWM: Left={pwmLeftPS2}, Right={pwmRightPS2})")
    # TODO: Gửi lệnh điều khiển động cơ tại đây
    
    if cmd == "Tien":
        GPIO.output(4, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)        
        LPWM1.duty_cycle = 0
        RPWM1.duty_cycle = 0
        LPWM2.duty_cycle = 0xFFFF
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
        LPWM1.duty_cycle = 0xFFFF 
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
        LPWM1.duty_cycle = 0xFFFF 
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
        LPWM1.duty_cycle = 0xFFFF 
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
        LPWM1.duty_cycle = 0xFFFF 
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
        LPWM1.duty_cycle = 0xFFFF 
        RPWM1.duty_cycle = 0
        LPWM2.duty_cycle = 0xFFFF 
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
        LPWM1.duty_cycle = 0
        RPWM1.duty_cycle = 0xFFFF 
        LPWM2.duty_cycle = 0
        RPWM2.duty_cycle = 0xFFFF
    elif cmd == "Quaytrai":
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)
        LPWM1.duty_cycle = 0xFFFF
        RPWM1.duty_cycle = 0
        LPWM2.duty_cycle = 0
        RPWM2.duty_cycle = 0xFFFF 
    elif cmd == "Quayphai":
        GPIO.output(4, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(5, GPIO.LOW)
        LPWM1.duty_cycle = 0
        RPWM1.duty_cycle = 0xFFFF 
        LPWM2.duty_cycle = 0xFFFF 
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
        LPWM3.duty_cycle = 0xFFFF
        RPWM3.duty_cycle = 0xFFFF
        LPWM4.duty_cycle = 0xFFFF 
        RPWM4.duty_cycle = 0xFFFF
    elif cmd == "Noi":
        GPIO.output(6, GPIO.LOW)
        GPIO.output(12, GPIO.HIGH)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(19, GPIO.HIGH) 
        
        GPIO.output(16, GPIO.LOW)
        GPIO.output(26, GPIO.HIGH)
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.HIGH) 
        LPWM3.duty_cycle = 0xFFFF 
        RPWM3.duty_cycle = 0xFFFF
        LPWM4.duty_cycle = 0xFFFF 
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
        LPWM3.duty_cycle = 0xFFFF
        RPWM3.duty_cycle = 0xFFFF 
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
        LPWM3.duty_cycle = 0xFFFF
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
        LPWM3.duty_cycle = 0xFFFF 
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
        LPWM3.duty_cycle = 0xFFFF 
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
        LPWM3.duty_cycle = 0
        RPWM3.duty_cycle = 0xFFFF 
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
        LPWM3.duty_cycle = 0
        RPWM3.duty_cycle = 0xFFFF 
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
        LPWM3.duty_cycle = 0
        RPWM3.duty_cycle = 0
        LPWM4.duty_cycle = 0xFFFF
        RPWM4.duty_cycle = 0xFFFF
    elif cmd == "Nghiensau_Up":
        GPIO.output(6, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(19, GPIO.LOW) 
        
        GPIO.output(16, GPIO.LOW)
        GPIO.output(26, GPIO.HIGH)
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.HIGH) 
        LPWM3.duty_cycle = 0
        RPWM3.duty_cycle = 0
        LPWM4.duty_cycle = 0xFFFF
        RPWM4.duty_cycle = 0xFFFF 
    elif cmd == "Batden":
        GPIO.output(17, GPIO.HIGH) 
    elif cmd == "Tatden":
        GPIO.output(17, GPIO.LOW)
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
    if cmd == "TienPS2":
        GPIO.output(4, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)        
        LPWM1.duty_cycle = 0
        RPWM1.duty_cycle = 0
        LPWM2.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
        RPWM2.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
    elif cmd == "TientraiPS2":
        GPIO.output(4, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22, GPIO.HIGH) 

        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)  
        LPWM1.duty_cycle = 0
        RPWM1.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
        LPWM2.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
        RPWM2.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
    elif cmd == "TienphaiPS2":
        GPIO.output(4, GPIO.LOW)
        GPIO.output(18, GPIO.HIGH)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)  
        LPWM1.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
        RPWM1.duty_cycle = 0 
        LPWM2.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
        RPWM2.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
    elif cmd == "LuiPS2":
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(5, GPIO.LOW)  
        LPWM1.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
        RPWM1.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
        LPWM2.duty_cycle = 0
        RPWM2.duty_cycle = 0
    elif cmd == "LuitraiPS2":
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(5, GPIO.HIGH)  
        LPWM1.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
        RPWM1.duty_cycle = int(pwmLeftPS2 * 65535 / 255) 
        LPWM2.duty_cycle = 0
        RPWM2.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
    elif cmd == "LuiphaiPS2":
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.HIGH)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(5, GPIO.LOW)  
        LPWM1.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
        RPWM1.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
        LPWM2.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
        RPWM2.duty_cycle = 0
    elif cmd == "TraiPS2":
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(5, GPIO.LOW)  
        LPWM1.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
        RPWM1.duty_cycle = 0
        LPWM2.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
        RPWM2.duty_cycle = 0
    elif cmd == "PhaiPS2":
        GPIO.output(4, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)      
        LPWM1.duty_cycle = 0
        RPWM1.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
        LPWM2.duty_cycle = 0
        RPWM2.duty_cycle = int(pwmLeftPS2 * 65535 / 255)
    elif cmd == "QuaytraiPS2":
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)
        LPWM1.duty_cycle = 0xFFFF
        RPWM1.duty_cycle = 0
        LPWM2.duty_cycle = 0
        RPWM2.duty_cycle = 0xFFFF
    elif cmd == "QuayphaiPS2":
        GPIO.output(4, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(22, GPIO.LOW) 

        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(5, GPIO.LOW)
        LPWM1.duty_cycle = 0
        RPWM1.duty_cycle = 0xFFFF 
        LPWM2.duty_cycle = 0xFFFF 
        RPWM2.duty_cycle = 0 
    elif cmd == "LanPS2":
        GPIO.output(6, GPIO.HIGH)
        GPIO.output(12, GPIO.LOW)
        GPIO.output(13, GPIO.HIGH)
        GPIO.output(19, GPIO.LOW) 
        
        GPIO.output(16, GPIO.HIGH)
        GPIO.output(26, GPIO.LOW)
        GPIO.output(20, GPIO.HIGH)
        GPIO.output(21, GPIO.LOW) 
        LPWM3.duty_cycle = int(pwmRightPS2 * 65535 / 255) 
        RPWM3.duty_cycle = int(pwmRightPS2 * 65535 / 255) 
        LPWM4.duty_cycle = int(pwmRightPS2 * 65535 / 255) 
        RPWM4.duty_cycle = int(pwmRightPS2 * 65535 / 255) 
    elif cmd == "NoiPS2":
        GPIO.output(6, GPIO.LOW)
        GPIO.output(12, GPIO.HIGH)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(19, GPIO.HIGH) 
        
        GPIO.output(16, GPIO.LOW)
        GPIO.output(26, GPIO.HIGH)
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.HIGH) 
        LPWM3.duty_cycle = int(pwmRightPS2 * 65535 / 255) 
        RPWM3.duty_cycle = int(pwmRightPS2 * 65535 / 255) 
        LPWM4.duty_cycle = int(pwmRightPS2 * 65535 / 255) 
        RPWM4.duty_cycle = int(pwmRightPS2 * 65535 / 255)     
    elif cmd == "BatdenPS2":
        GPIO.output(17, GPIO.HIGH) 
    elif cmd == "TatdenPS2":
        GPIO.output(17, GPIO.LOW)
    elif cmd == "LaynuocPS2":
        in1.duty_cycle = 0xFFFF 
        in2.duty_cycle = 0
        in3.duty_cycle = 0
        in4.duty_cycle = 0
    elif cmd == "DaynuocPS2":
        in1.duty_cycle = 0
        in2.duty_cycle = 0
        in3.duty_cycle = 0xFFFF 
        in4.duty_cycle = 0  
    elif cmd == "DunglaynuocPS2":
        in1.duty_cycle = 0
        in2.duty_cycle = 0
        in3.duty_cycle = 0
        in4.duty_cycle = 0          
    elif cmd in ["Dung", "DungPS2"]:
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
if not camera.isOpened():
    raise RuntimeError("Không mở được camera")
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
@app.route('/sensor_stream')
def sensor_stream():
    def generate_sensor_data():
        while True:
            # Đọc dữ liệu cảm biến
            ax, ay, az = mpu.readAccelerometerMaster()
            gx, gy, gz = mpu.readGyroscopeMaster()
            temp = bmp280.temperature
            pressure = bmp280.pressure

            # Tạo dữ liệu JSON
            data = {
                "acc": {"x": round(ax, 2), "y": round(ay, 2), "z": round(az, 2)},
                "gyro": {"x": round(gx, 2), "y": round(gy, 2), "z": round(gz, 2)},
                "temp": round(temp, 2),
                "pressure": round(pressure, 2)
            }

            # Stream dưới dạng text/plain
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.2)
       
    return Response(stream_with_context(generate_sensor_data()), mimetype='text/event-stream')
app.run(host='0.0.0.0', port=5000) #Khởi chạy Flask server
