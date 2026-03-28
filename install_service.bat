@echo off
:: install_service.bat
:: Installs ZIP Watcher as a Windows Service using NSSM
:: Run this as Administrator

SET SERVICE_NAME=ZipWatcher
SET PYTHON_EXE=C:\Python311\python.exe
SET SCRIPT_PATH=C:\zip-watcher\main.py
SET NSSM=C:\nssm\nssm.exe

echo Installing %SERVICE_NAME% as a Windows Service...

%NSSM% install %SERVICE_NAME% %PYTHON_EXE% %SCRIPT_PATH%
%NSSM% set %SERVICE_NAME% AppDirectory C:\zip-watcher
%NSSM% set %SERVICE_NAME% DisplayName "ZIP Watcher SD-Task Monitor"
%NSSM% set %SERVICE_NAME% Description "Monitors directory for ZIP files and sends email alerts"
%NSSM% set %SERVICE_NAME% Start SERVICE_AUTO_START
%NSSM% set %SERVICE_NAME% AppStdout C:\zip-watcher\logs\service_stdout.log
%NSSM% set %SERVICE_NAME% AppStderr C:\zip-watcher\logs\service_stderr.log

echo Starting service...
net start %SERVICE_NAME%

echo Done! Service %SERVICE_NAME% is running.
pause
