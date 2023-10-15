# DEU 23-1 임베디드소프트웨어 5조 프로젝트

## 주제 : 스마트 홈 보안 시스템

### 프로젝트 설계
![image](https://github.com/TTANGGIN/PiHomeCam/assets/58355254/cfa7e804-37aa-4d3b-8fab-f919dda093b1)
- 사진에 DHT22 추가 필요
- Flask 웹을 이용하여 상호작용

### 화면 설계
![image](https://github.com/TTANGGIN/PiHomeCam/assets/58355254/eeebc637-d4ac-4bdf-ba81-61a53349f5d9)

### 데이터베이스
#### 정보
- DBMS : MariaDB
- DB 이름 : webcam
- 스키마
  - user : 사용자 관리
  - activity_log : 사용자 활동 기록

#### ERD
![image](https://github.com/TTANGGIN/PiHomeCam/assets/58355254/137b8d45-f823-4541-b70f-aac0fe00ad6d)


#### SQL
```
CREATE DATABASE webcam;

use webcam;

CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    ip_address VARCHAR(15) NOT NULL
);

CREATE TABLE activity_log (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    date DATE NOT NULL DEFAULT CURDATE(),
    time TIME NOT NULL DEFAULT CURTIME(),
    activity VARCHAR(200),
    remark VARCHAR(100),
    filePath TEXT,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);
```

## 주의 사항
### 1. ESP32 사전작업
ESP32에 아래 링크의 코드 업로드 필수
- [ESP32 코드](https://github.com/TTANGGIN/PiHomeCam/blob/main/esp32_code.c)
- DHT22는 13번 핀에 연결되어야 함
- LED는 12번 핀에 연결되어야 함
- 피에조 부저는 15번 핀에 연결되어야 함
- 업로드 전 반드시 아래 사항을 자신의 <네트워크 이름>, <네트워크 PW>로 바꿔야함
``` 
const char* ssid = "<네트워크 이름>";
const char* password = "<네트워크 PW>";
```
- ESP32는 5G 와이파이 연결 불가. 2.4G 와이파이에 연결할 것

### 2. ESP32 연결
- esp32와 통신을 위해 ```main.py```에 아래 사항 수정 필요
```
esp32_Ip = "<ESP32 IP주소>"
esp32_port = "<ESP32 포트>"
```
- ESP32 IP는 네트워크 연결 시 아두이노 IDE의 시리얼 모니터에서 확인 가능
- 시리얼 모니터(115200보드레이트)를 켠 상태로 업로드 후 와이파이 연결 확인
- 포트는 기본적으로 http(80)포트를 사용하면 됨
```
esp32_port = "80"
```

### 3. 라이브러리 설치
- 아래의 라이브러리 또는 모듈은 별도의 설치가 필요함으로 실행 전 설치가 필요하다.
```
sudo apt-get install mariadb-server
pip install opencv-python flask-basicauth Flask-SQLAlchemy
```

### 4. MySQL(MariaDB) 권한 설정
- MariaDB 10.4 버젼 이상일 경우 비밀번호 인증을 따로 활성화 해야됨
```
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost';
ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password;
SET PASSWORD FOR 'root'@'localhost' = PASSWORD('비밀번호');
FLUSH PRIVILEGES;
```
