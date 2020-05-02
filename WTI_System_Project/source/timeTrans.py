#초를 입력받아 시간과 분으로 반환한다.
def trans_time(second,interval):
    #시간, 분 계산
    sec = second

    h = int(sec // 3600)
    sec = int(sec%3600)

    m = int(sec//60)
    m = (m//interval)*interval
    
    return str(h), str(m)
    