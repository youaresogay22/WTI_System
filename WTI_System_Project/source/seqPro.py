import csv
import extract
import copy
import filePath


#시퀀스번호 전처리
def seq_Preprosessor():
    pro_line = []
    temp_line = []
    cycle=0

    with open(filePath.csv_probe_path,"r") as f:
        rdr = csv.reader(f)

        #임시리스트에 패킷데이터 라인 복사
        for line in rdr:
            if line[0]=="wlan.sa":
                continue
            else:
                pro_line.append(line)

        #임시 리스트에 저장
        temp_line = copy.deepcopy(pro_line)
        
        for idx in range(len(pro_line)):
            #시퀀스번호 가공
            if idx!=0 and int(pro_line[idx][2])<int(pro_line[idx-1][2]):
                cycle = cycle + 1
            temp_line[idx][2] =  int(pro_line[idx][2]) + (cycle*4096)
        
            #길이(length) 가공
            temp_line[idx][4] = int(pro_line[idx][4]) - len(pro_line[idx][3])
            
        pro_line = copy.deepcopy(temp_line)

    #수정된 패킷 데이터 라인들을 csv에 새로 작성
    with open(filePath.csv_probeRe_path,"w") as f:
        wr = csv.writer(f)
        wr.writerows(pro_line)
