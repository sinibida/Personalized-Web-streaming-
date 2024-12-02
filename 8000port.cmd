@echo off
REM Windows 방화벽에서 8000번 포트를 허용
netsh advfirewall firewall add rule name="Allow Port 8000" dir=in action=allow protocol=TCP localport=8000
echo Port 8000 is now open in the firewall.
pause
