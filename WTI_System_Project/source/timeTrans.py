#초를 입력받아 시간과 분으로 반환한다.
def trans_time(second):
    #시간, 분 계산
    
    h = int(second / 3600)
    sec = int(second % 3600)
    m = int(second / 60)

    if m < 10:
        m = 0
    elif m >=10 and m<20:
        m = 10
    elif m >=20 and m<30:
        m = 20
    elif m >=30 and m<40:
        m = 30
    elif m >=40 and m<50:
        m = 40
    elif m >=50 and m<60:
        m = 50
    #저장
    return str(h), str(m)
    