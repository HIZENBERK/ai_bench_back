superuser : admin
password : 1234

테이블 데이터 타입이 좀 문제임  intiger, char, date가 제대로 적용이 안되는 듯함, 선언에 문제가 있을 수도 있음

pip list 확인 후 djangorestframework 없으면 install

터미널에 pip freeze > requiremnets.txt
이건 효과가 제대로 있는건지 모르겠음, 안하고도 됐던거 같음

이후 migrate 진행할 것

그 뒤 runserver 하면 아마 될것