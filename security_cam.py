import RPi.GPIO as GPIO
from time import sleep
import datetime, requests, cv2, os, glob, config

# LINE Notifyトークン
TOKEN = config.TOKEN
API = 'https://notify-api.line.me/api/notify'

# GPIOポートの設定
SENSOR_PORT = 23
LED_PORT = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PORT, GPIO.IN)
GPIO.setup(LED_PORT, GPIO.OUT)

# CV2準備
camera = cv2.VideoCapture(0)
IMG_SIZE = (600,400)

# 写真の撮影コマンドを実行(ファイル名を日時に)
last_post = datetime.datetime(2000, 1, 1) # 適当に初期化
def take_photo():
    global last_post
    # 写真を撮影
    now = datetime.datetime.now()
    fname = "/media/pi/rasUSB/security_cam/img/" + now.strftime('%Y-%m-%d_%H-%M-%S') + ".jpg"

    # 古い画像を削除
    file_list = glob.glob("/media/pi/rasUSB/security_cam/img/*jpg")
    dif_time = datetime.timedelta(days=3)
    for file in file_list:
        file_time = datetime.datetime.fromtimestamp(os.path.getatime(file))
        if (file_time < now  - dif_time):
            print("remove：{0}".format(file))
            os.remove(file)

    # 撮影
    _, frame = camera.read()
    img = cv2.resize(frame, IMG_SIZE)
    ret = cv2.imwrite(fname, img)
    if ret:
        print('撮影画像: ' + fname)
    else:
        print('Failed to write image.')

    # LINEに通知
    # ただし10分は通知しない --- (*1)
    sec = (now - last_post).seconds
    if sec < 10 * 60: return
    last_post = now
    # 通知をLINEに挿入 --- (*2)
    post_data = {'message': 'ニャンズ'}
    headers = {'Authorization': 'Bearer ' + TOKEN}
    files={'imageFile': open(fname,'rb')}
    res = requests.post(API, data=post_data,
        headers=headers,files=files)
    print(res.text)

try:
    sw = 0 # 連続撮影防止
    # 繰り返しセンサーの値を得る
    while True:
        v = GPIO.input(SENSOR_PORT)
        if v == GPIO.HIGH:
            GPIO.output(LED_PORT, GPIO.HIGH)
            take_photo()
            sw = 1
        else:
            GPIO.output(LED_PORT, GPIO.LOW)
            sw = 0
        sleep(10.0)
except KeyboardInterrupt:
        pass
GPIO.cleanup()
