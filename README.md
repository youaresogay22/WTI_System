# WTI_System
무선단말식별시스템

1. 패킷 데이터 수집 준비 과정
Step 1 NIC(무선랜카드) 장착

Step 2 NIC 네트워크 인터페이스 확인
```
sudo iwconfig
```
작성자의 경우에는 wlan0 인터페이스를 확인하였습니다.
만약 wlan0이 아닌 경우에는 명령어 수정이 요구됩니다.

2. 패킷 데이터 수집 및 가공
Step 1 Desktop 화면에 git 폴더를 생성합니다.
```
user@kali:~/Desktop$ mkdir git
```

Step 2 WTI_System_Project 폴더를 git 폴더에 위치시킵니다.
```
user@kali:~/Desktop$ mv WTI_System_Project git
```

Step 3 WTI_System_Project 폴더로 이동합니다.
```
user@kali:~/Desktop/git$ cd WTI_System_Project
```

Step 4 data_collection_cmd 파일 실행
```
user@kali:~/Desktop/git/WTI_System_Project$ ./data_collection_cmd
```
