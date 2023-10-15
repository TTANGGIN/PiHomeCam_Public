import cv2
import os
import sys
from flask import Flask, render_template, Response, jsonify, request, send_from_directory
from webcamvideostream import WebcamVideoStream
from databasemanager import DatabaseManager
from flask_basicauth import BasicAuth
import time
import threading
from datetime import datetime
from urllib.request import urlopen  # python 3
from urllib.error import HTTPError, URLError

app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'pi'
app.config['BASIC_AUTH_PASSWORD'] = 'pi'
app.config['BASIC_AUTH_FORCE'] = True

# 데이터베이스 URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/webcam'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Flask-SQLAlchemy에서 변경 사항을 추적하지 않도록 설정

basic_auth = BasicAuth(app)
last_epoch = 0

esp32_Ip = "192.168.0.105"
esp32_port = "80"
esp32_url = "http://" + esp32_Ip + ":" + esp32_port
temp_url = esp32_url + "/temp"
led_on_url = esp32_url + "/led_on"
led_off_url = esp32_url + "/led_off"
led_status_url = esp32_url + "/led_status"
alart_on_url = esp32_url + "/alart_on"
alart_off_url = esp32_url + "/alart_off"
alart_status_url = esp32_url + "/alart_status"

DatabaseManager.init_app(app)
camera = WebcamVideoStream(db_manager=DatabaseManager, app=app).start()

@app.route('/')
@basic_auth.required
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        if camera.stopped:
            break
        frame = camera.read()
        ret, jpeg = cv2.imencode('.jpg', frame)
        if jpeg is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        else:
            print("frame is none")

@app.route('/video_feed')
def video_feed():
    # 비디오 피드 생성
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    
@app.route('/temp')
def get_temp():
    u = urlopen(temp_url)
    data = ""
    try:
        data = u.read()
    except HTTPError as e:
        print("HTTP error: % d" % e.code)
    except URLError as e:
        print("Network error: %s" % e.reason.args[1])

    return data

@app.route('/dhtchart')
def dht_chart():
    return render_template('dhtchart.html')

@app.route('/led_on')
def led_on():
    try:
        urlopen(led_on_url)
        log_activity('LED 켜짐')
    except (HTTPError, URLError) as e:
        print("Error: %s" % e)
    return "LED is now on"

@app.route('/led_off')
def led_off():
    try:
        urlopen(led_off_url)
        log_activity('LED 꺼짐')
    except (HTTPError, URLError) as e:
        print("Error: %s" % e)
    return "LED is now off"

@app.route('/led_status')
def led_status():
    try:
        response = urlopen(led_status_url)
        data = response.read().decode()
    except (HTTPError, URLError) as e:
        print("Error: %s" % e)
        data = "{\"status\": \"unknown\"}"

    return data

@app.route('/alart_on')
def alart_on():
    try:
        urlopen(alart_on_url)
        log_activity('경보 켜짐')
    except (HTTPError, URLError) as e:
        print("Error: %s" % e)
    return "alart is now on"

@app.route('/alart_off')
def alart_off():
    try:
        urlopen(alart_off_url)
        log_activity('경보 꺼짐')
    except (HTTPError, URLError) as e:
        print("Error: %s" % e)
    return "alart is now off"

@app.route('/alart_status')
def alart_status():
    try:
        response = urlopen(alart_status_url)
        data = response.read().decode()
    except (HTTPError, URLError) as e:
        print("Error: %s" % e)
        data = "{\"status\": \"unknown\"}"

    return data

@basic_auth.required
def log_activity(activity):
    if DatabaseManager and app:
        with app.app_context():
            username = app.config['BASIC_AUTH_USERNAME']
            user = DatabaseManager.get_user_by_username(username)
            if user:
                DatabaseManager.add_activity(user.user_id, activity)
                log_message = f"{username} - - [{datetime.now()}] Activity record - {activity}"
                print(log_message)

class VideoInfo:
    def __init__(self, filename, date, size):
        self.filename = filename
        self.date = date
        # Convert size to KB and append 'KB'
        self.size = f"{size // 1024} KB"

@app.route('/check_video')
@basic_auth.required
def video_list():
    video_dir = 'Videos'
    videos = []
    for filename in os.listdir(video_dir):
        if filename.endswith('.mp4'):
            filepath = os.path.join(video_dir, filename)
            file_stat = os.stat(filepath)
            size = file_stat.st_size
            date = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y년%m월%d일 %H:%M:%S')
            videos.append(VideoInfo(filename, date, size))
            
    videos = sorted(videos, key=lambda x: x.date, reverse=True)
    return render_template('video_list.html', videos=videos)

@app.route('/check_video/<filename>')
@basic_auth.required
def video_player(filename):
    return render_template('video_player.html', filename=filename)

@app.route('/file/<filename>')
@basic_auth.required
def file(filename):
    return send_from_directory('Videos', filename)

@app.route('/events')
def events():
    return render_template('events.html')

@app.route('/get_activities', methods=['GET'])
@basic_auth.required
def get_activities():
    # DB에서 활동기록을 가져옴
    username = app.config['BASIC_AUTH_USERNAME']
    activities = DatabaseManager.get_activities_by_username(username)
    
    # 각 활동 로그 객체를 dictionary로 변환
    activities_dicts = [activity.as_dict() for activity in activities]

    # dictionary 목록을 JSON으로 직렬화하여 반환
    return jsonify(activities_dicts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, threaded=True)