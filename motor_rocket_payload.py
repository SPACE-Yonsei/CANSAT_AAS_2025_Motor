import time
import math

state = none # 하강이냐 아니냐
n = 0  # n 5보다 커지면 사출
ACC_THRESHOLD = 0.3 #가속도 변화 임계치

while True:
    acc = 현재 가속도 입력 
    if acc > ACC_THRESHOLD && sate != "descending": # 가속도 임계치 이상이며 하강이 아니였을 때
        state = "descending"
        start_time = time.time()  # 최고 고도 시 시각
        high_alt = 현재 고도 입력 # 최고 고도

    if state == "descending": 
        current_time = time.time()
        current_alt = 현재 고도 입력
        current_angle = 현재 z축 기준 각도

        if n > 5:
            print("조건 충족")
        if current_time - start_time >= 3000:
            print("조건 충족")
        if high_alt - current_alt >= 20: #m 기준
            print("조건 충족")
        if current_angle >= 135:  #(도)
            print("조건 충족")

        if 80 <= current_angle <= 100 && high_alt - current_alt < 0.2:
                n += 1
        if 60 <= current_angle <= 120 && high_alt - current_alt < 0.3:
                n += 1
        if 45 <= current_angle <= 135 && high_alt - current_alt < 0.5:
                n += 1
        elif: # 로켓 안정성 위해 사출 조건 벗어나면 n 차감. 예) 1 1 1 1 1 -> 사출 1 1 1 -1 1 -> 논 사출 1 1 1 -1 1 1 -1 1 1-> 사출
            if n >0:
                n -= 1
    time.sleep(0.1)
