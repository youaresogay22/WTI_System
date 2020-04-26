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

프로그램 실행방법
step 1 source 디렉토리로 이동
step 2 명령어 입력
```
sudo python3 main.py
```

TensorFlow 설치 및 버전 확인
```
$ sudo -H pip3 install --upgrade tensorflow
$ python3
>>> import tensorflow as tf
>>> tf.__version__
'1.0.0'
>>>
```
출처 : https://www.youtube.com/watch?v=-57Ne86Ia8w&list=PLlMkM4tgfjnLSOjrEJN31gZATbcj_MpUm&index=3ㅅ
