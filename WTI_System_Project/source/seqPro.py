import csv
import extract

#시퀀스 번호 전처리
def seq_pretreat(seq):
    cycle=0
    seq_no_re = []
    
    for idx in range(len(seq)):
        #현재 시퀀스 번호가 이전 시퀀스 번호보다 작으면
        #사이클이 바꼈다는 의미로 사이클 번호를 1 증가시킵니다.
        if idx!=0 and int(seq[idx])<int(seq[idx-1]):
            cycle = cycle + 1
        seq_no_re.append(int(seq[idx]) + (cycle*4096))
    return seq_no_re

#시퀀스번호 전처리
def seq_Preprosessor():
    seq_list = []             #시퀀스 번호 추출 리스트
    seq_lines = []          #가공된 시퀀스번호 패킷데이터 라인

    #시퀀스 넘버 추출
    with open("/home/user/Desktop/WTI_System_Project/csv/probe.csv","r") as f:
        rdr  = csv.reader(f)
        seq_list = extract.extract_data_header(rdr,"wlan.seq")
        seq_list = seq_pretreat(seq_list)

    #시퀀스 번호 수정
    with open("/home/user/Desktop/WTI_System_Project/csv/probe.csv","r") as f:
        rdr = csv.reader(f)
        i = 0
        for line in rdr:
            if line[2] =="wlan.seq":
                seq_lines.append(line)
            else:
                line[2] = seq_list[i]
                i = i+1
                seq_lines.append(line)

    #수정된 시퀀스 번호를 csv에 새로 작성
    with open("/home/user/Desktop/WTI_System_Project/csv/probe_re.csv","w") as f:
        wr = csv.writer(f)
        wr.writerows(seq_lines)