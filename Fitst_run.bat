@echo off
REM 실행 순서: install.py -> reader.py -> 8000port.cmd -> app(comment_kr).py

echo ==== Python 환경 확인 및 패키지 설치 ====
python install.py
if %errorlevel% neq 0 (
    echo install.py 실행 실패. 배치파일을 종료합니다.
    pause
    exit /b
)

echo ==== reader.py 실행 ====
python reader.py
if %errorlevel% neq 0 (
    echo reader.py 실행 실패. 배치파일을 종료합니다.
    pause
    exit /b
)

echo ==== 8000port.cmd 실행 ====
call 8000port.cmd
if %errorlevel% neq 0 (
    echo 8000port.cmd 실행 실패. 배치파일을 종료합니다.
    pause
    exit /b
)

echo ==== app(comment_kr).py 실행 ====
python "app(comment_kr).py"
if %errorlevel% neq 0 (
    echo app(comment_kr).py 실행 실패. 배치파일을 종료합니다.
    pause
    exit /b
)

echo ==== 모든 작업이 완료되었습니다 ====
pause
exit
