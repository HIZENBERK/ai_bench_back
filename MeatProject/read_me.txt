프로젝트 폴더 만들고 그 안에 가상환경 설치
vscode의 경우 ctrl + shift + P 입력
interpreter에서 가상환경 선택

프롬픝트 cmd로 연 후
pip list
pip 리스트 확인 후 없는것들 설치

이거부터
pip install -r requirements.txt

이후 안되면 밑에거 하나씩 설치
django
djangorestframework
djangorestframework-simplejwt
django-cors-headers

설치 이후
jprivate_setting.py를 settings.py와 같은 폴더에 옮기고

실행
python manage.py makemigrations
python manage.py migrate


//이미 있을 수도 있음
superuser 생성
python manage.py createsuperuser

superuser : admin
password : 1234

테이블 데이터 타입이 좀 문제임  intiger, char, date가 제대로 적용이 안되는 듯함, 선언에 문제가 있을 수도 있음


터미널에 pip freeze > requiremnets.txt
이건 효과가 제대로 있는건지 모르겠음, 안하고도 됐던거 같음

그 뒤 runserver 하면 아마 될것


db 갈아엎을때
rm db.sqlite3 명령어로 sql파일부터 날리고 다시 마이그레이션
**db 갈아엎을 때 python manage.py flush 명령어도 가능하다 함 -> sql 파일은 안지우고 내용물만 지움

23.06.07 추가사항
보안을 위해 settings.py의 시크릿키와 데이터베이스를 외부 파일로 만든 뒤 gitignore에 추가하여서 깃에 올라가지 않음

23.06.10 추가사항
모델 수정