#! /user/bin/env python3

# 모듈

import serial
import RPi.GPIO as GPIO
import time
from datetime import datetime

# firebase module

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# 오늘 날짜 불러오기

date = datetime.today()

# firebase document name 불러오기
while True:
    try :
        f = open("/home/pi/Desktop/id", 'r')
        id_data = f.readline()
        break

    except FileNotFoundError:  # 파일이 생성되어 있지 않은 경우
        print("블루투스 연결이 필요합니다.")
        time.sleep(3600)

# firestore 접근하기

cred = credentials.Certificate("/home/pi/Desktop/learndry-bin-firebase-adminsdk-dqbsn-4dc8a30be2.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 받아온 id값에 해당하는 문서 열기

doc_ref = db.collection(u'datas').document(id_data)

doc_ref_Period = doc_ref.collection(u'period')  # 빨래를 할때 얼마나 빨래하고 언제 하는지


# 라즈베리파이 초음파센서 작동시키기

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

trig = 6
echo = 13

GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

try:
    while True :
        GPIO.output(trig, False)
        time.sleep(0.1)    # need test!
        GPIO.output(trig, True)
        time.sleep(0.0001)
        
        GPIO.output(trig, False)
        
        while GPIO.input(echo) == 0 :
            pulse_start = time.time()
            
        while GPIO.input(echo) == 1 :
            pulse_end = time.time()

        # 거리 계산 기준치(40cm) 미만이면 loadcell 센서 작동

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17000
        distance = round(distance, 2)

        if distance < 40:

            # loadcell 센서 동작 serial 통신

            while True:

                # 다른 python 파일에서 data값을 올리고 있는 경우 동작x

                if doc_ref.get()['on_off1'] == 1:
                    time.sleep(5000)
                    continue
                else:
                    break
                
            # 실제 serial 통신 동작 부분

            if __name__ == '__main__':
                ser = serial.Serial('/dev/ttyUSB1', 57600, timeout = 1)
                ser.flush()
                while True:
                    if ser.in_waiting > 0:
                        line = ser.readline().decode('utf-8').rstrip()
                        # print(line)
                        
                        if float(line) == -1000:
                            continue
                        
                            
                        data = float(line)    
                        break

                # data < 0 인 순간 => 빨래하는 날이므로 빨래를 언제, 얼마나 하는지 데이터 저장

                if data <= 0 :


                    # doc_ref_Period에 document에 '오늘 날짜' 가 있는지 확인 없으면 set()

                    if date.strftime("%Y%m%d") not in doc_ref_Period.get():

                        doc_ref_Period.document(date.strftime("%Y%m%d")).set()

                    # 업데이트 되기전 빨래통의 무게를 빨래양으로 db에 업데이트

                    pre_weight = doc_ref.get()['weight1']
                    doc_ref_Period.document(date.strftime("%Y%m%d")).update({'laun_weight1' : pre_weight})

                    # 빨래양과 주기 가져오기

                    dic_ideal = doc_ref_Period.get()
                    
                    count = 0  # 빨래 한 날의 수
                    sum_d = 0  # 날짜의 차이를 더함
                    sum_w = 0.0  # weight를 더함

                    # for문 :  collection(= Period)에 저장된 document(날짜) 반복

                    for i in dic_ideal:

                        if i['laun_weight1']:  # laun_weight1이 있는 경우 실행

                            if count == 0:     # 처음 동작시 이전 빨래한날 초기화
                                pre_day = i

                            else:
                                day1 = datetime.strptime(i, "%Y%m%d")  # string -> datetime
                                day2 = datetime.strptime(pre_day, "%Y%m%d")  # string -> datetime

                                delta_day = (day1 - day2).days   # 주기 계산
                                pre_day = i    # 이전 빨래한날 초기화

                                sum_d += delta_day  # 주기 더해주기

                            sum_w += float(i['laun_weight1'])  # 빨래 무게 더해주기
                            count += 1
                    
                    mean_w = sum_w / count  # 사용자의 평균 빨래양

                    if count > 1:
                        mean_d = sum_d / (count - 1)
                    else:
                        mean_d = 0 # 주기 초기값?

                    # 평균빨래양, 평균 주기 업데이트 

                    doc_ref.update({ 
                        u'ideal_w1' : mean_w ,
                        u'period_w1' : mean_d
                        })

                # weight1값 업데이트, on_off 업데이트

                doc_ref.update({
                    u'weight1' : data,
                    u'on_off1' : 0
                    })

except :
    GPIO.cleanup()