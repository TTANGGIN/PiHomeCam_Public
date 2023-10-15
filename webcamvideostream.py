import cv2
from threading import Thread
import time
import numpy as np
import os
import logging
from datetime import datetime, timedelta

class WebcamVideoStream:
    camera_instance = None
    
    def __init__(self, src = 0, db_manager=None, app=None):
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        logging.info("init camera")
        
        self.db_manager = db_manager
        self.app = app
        
        if WebcamVideoStream.camera_instance is not None:
            WebcamVideoStream.camera_instance.stop()
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        # Initialize for object detection
        self.i0 = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
        (self.grabbed, self.frame) = self.stream.read()
        self.i1 = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
        (self.grabbed, self.frame) = self.stream.read()
        self.i2 = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
        self.thresh = 32
        
        self.stopped = False
        time.sleep(2.0)
        
        WebcamVideoStream.camera_instance = self
        
        self.is_recording = False
        self.out = None
        self.start_time = None
        self.MIN_RECORDING_DURATION = timedelta(seconds=1)  # 상수로 1초 설정

    def start(self):
        print("start thread")
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self
    
    def diffImage(self, i0, i1, i2):
        diff0 = cv2.absdiff(i0, i1)
        diff1 = cv2.absdiff(i1, i2)
        return cv2.bitwise_and(diff0, diff1)

    def update(self):
        print("read")
        while True:
            if self.stopped:
                if self.is_recording:
                    self.out.release()
                return

            (self.grabbed, self.frame) = self.stream.read()

            # 객체 감지 코드
            diff = self.diffImage(self.i0, self.i1, self.i2)
            ret, thrimg = cv2.threshold(diff, self.thresh, 1, cv2.THRESH_BINARY)
            count = cv2.countNonZero(thrimg)
            if count > 1:
                if not self.is_recording:
                    self.start_recording()
            else:
                if self.is_recording:
                    self.stop_recording()
                
            # 다음 이미지 처리
            self.i0 = self.i1
            self.i1 = self.i2
            self.i2 = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)

            # 녹화 중이면 프레임 저장
            if self.is_recording:
                self.out.write(self.frame)

    def start_recording(self):
        # 영상 저장 폴더 확인
        if not os.path.exists('Videos'):
            os.makedirs('Videos')
        timestamp = datetime.now().strftime("motionevent_%y%m%d_%H%M%S")
        self.video_path = os.path.join('Videos', f'{timestamp}.mp4')  # video_path를 인스턴스 변수로 저장
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        self.out = cv2.VideoWriter(self.video_path, fourcc, 20.0, (640,480))
        self.is_recording = True
        self.start_time = datetime.now()


    def stop_recording(self):
        elapsed_time = datetime.now() - self.start_time
        if elapsed_time >= self.MIN_RECORDING_DURATION:
            # 일정 시간 이상 녹화되었다면 파일 저장
            self.out.release()
            # DB에 로그 남기기
            if self.db_manager and self.app:
                with self.app.app_context():
                    username = self.app.config.get('BASIC_AUTH_USERNAME')
                    user = self.db_manager.get_user_by_username(username)
                    if user:
                        self.db_manager.add_activity(user.user_id, activity='움직임 감지', remark=None, filePath=self.video_path)
                        log_message = f"{username} - - [{datetime.now()}] Activity record - Video: {self.video_path}"
                        logging.info(log_message)
        else:
            # 녹화 시간이 짧으면 파일 삭제
            os.remove(self.video_path)  # video_path 변수 사용
        self.is_recording = False
        self.start_time = None


    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.stream.release()

