@echo off


title Background disk scan



REM change active dir to current location
%~d0
cd /d "%~dp0"



if "%~1" neq "oneinstance" (

	if exist SingleInstanceCmd.exe (
		SingleInstanceCmd.exe "%~n0" "%~0" "oneinstance"
		goto :eof
	)
)



REM change screen dimensions
mode con: cols=200 lines=9999



:loop


python diskscan.py >> diskscan_log.txt 2>&1


ping -n 2 127.0.0.1 > nul
REM sleep 1 > nul


goto loop
