#! /user/bin/env python3

# module

import time
import serial
from datetime import datetime, timedelta

# module of firebase

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

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

doc_ref_W_I1 = doc_ref.collection(u'featureAnalysis').document(u'weight_increment1')  # 빨래를 할때 얼마나 빨래하고 언제 하는지

doc_ref_W_I2 = doc_ref.collection(u'featureAnalysis').document(u'weight_increment2')  # 빨래를 할때 얼마나 빨래하고 언제 하는지


# 초기값 선언
weight1 = 0
weight2 = 0
    
try:
    dictionary1 = doc_ref.get().to_dict()  # user의 data 가져오기
    
    pre_weight1 = dictionary1['pre_weight1']
    pre_weight2 = dictionary1['pre_weight2']

    '''
    while True:
        if dictionary1['on_off1'] == 1 or dictionary1['on_off2'] == 1:
            time.sleep(5000)
            continue
        else:
            break
    
    doc_ref.update({
        u'on_off1' : 1 ,
        u'on_off2' : 1           
    })
    '''
    # weight1 값 가져오기

    if __name__ == '__main__':

        ser_Weight1 = serial.Serial('/dev/ttyUSB1', 57600, timeout=1)
        ser_Weight1.flush()

        while True:
            if ser_Weight1.in_waiting > 0:
                weight1 = ser_Weight1.readline().decode('uft-8').rstrip()

                if int(weight1) == -1000:
                    continue
                else:
                    break

    # weight2 값 가져오기

    if __name__ == '__main__':

        ser_Weight2 = serial.Serial('/dev/ttyUSB0', 57600, timeout=1)
        ser_Weight2.flush()

        while True:
            if ser_Weight2.in_waiting > 0:
                weight2 = ser_Weight2.readline().decode('uft-8').rstrip()

                if int(weight2) == -1000:
                    continue
                else:
                    break    
    ''' 
    doc_ref.update({
        u'on_off1' : 0 ,
        u'on_off2' : 0           
    })
    '''

    # weight값 float으로 변경
    weight1 = float(weight1)
    weight2 = float(weight2)

    # 증가량 계산

    weight1_inc = weight1 - pre_weight1
    weight2_inc = weight2 - pre_weight2


    # 오늘 날짜 가져오기 슬라이싱

    date = datetime.today()

    date_slicing = date.strftime('%Y%m%d')

    # 업데이트

    if weight1 > pre_weight1:  # 증가량 > 0 일때
        doc_ref_W_I1.update({
            date_slicing: weight1_inc
        })

    else:
        doc_ref_W_I1.update({  # 빨래한 날
            date_slicing: 0
        })

    if weight2 > pre_weight2: # 증가량 > 0 일때

        doc_ref_W_I2.update({
            date_slicing: weight2_inc
        })

    else:
        doc_ref_W_I2.update({  # 빨래한 날
            date_slicing: 0
        })
    # 14일 이전 데이터 삭제

    if len(doc_ref_W_I1) > 14:
        date_14 = date - timedelta(14)
        date_14 = date_14.strftime('%Y%m%d')
        doc_ref_W_I1.update({
            date_14: firestore.DELETE_FIELD
        })
        doc_ref_W_I2.update({
            date_14: firestore.DELETE_FIELD
        })

    # 평균을 계산하기 위한 초기값 지정
    count1 = 0
    count2 = 0
    sum1 = 0
    sum2 = 0

    length = len(doc_ref_W_I1)

    # 값을 가지고 오기
    for i in range(length): # 14일은 회의 조정 필요
        date_d = date - timedelta(i)
        date_d_s = date_d.strftime('%Y%m%d')
        weight_inc1, weight_inc2 = doc_ref_W_I1[date_d_s], doc_ref_W_I1[date_d_s]

        sum2 += weight_inc1
        sum2 += weight_inc2
        '''
        if weight_inc1:
            sum1 += weight_inc1
            count1 += 1
        if weight_inc2:
            sum2 += weight_inc2
            count2 += 1
        '''

    # 평균 증가량 계산 후 파이어베이스에 업로드
    
    mean1 = sum1 / length
    mean2 = sum2 / length

    doc_ref.update({
            u'mean_inc1' : mean1,
            u'mean_inc2' : mean2,
            u'pre_weight1' : weight1,
            u'pre_weight2' : weight2
        })
        

except:
    print('error')




