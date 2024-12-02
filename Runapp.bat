@echo off
REM 서버 파이썬 코드 실행 (app(comment_kr).py)

echo ==== 서버(app(comment_kr).py) 실행 시작 ====
python "app(comment_kr).py"

REM 서버 실행 완료 후 자동으로 종료되지 않도록 대기
echo 서버가 종료되었거나 중단되었습니다. Enter 키를 눌러 닫으세요.
pause
