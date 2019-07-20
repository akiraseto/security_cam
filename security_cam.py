import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
import requests, cv2, config

# LINE Notifyトークン
TOKEN = config.TOKEN
API = 'https://notify-api.line.me/api/notify'

# GPIOポートの設定
SENSOR_PORT = 23
LED_PORT = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PORT, GPIO.IN)
GPIO.setup(LED_PORT, GPIO.OUT)

# CV2準備
camera = cv2.VideoCapture(0)
IMG_SIZE = (600,400)

# 写真の撮影コマンドを実行(ファイル名を日時に)
last_post = datetime(2000, 1, 1) # 適当に初期化
def take_photo():
    global last_post
    # 写真を撮影
    now = datetime.now()
    fname = "img/" + now.strftime('%Y-%m-%d_%H-%M-%S') + ".jpg"

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
