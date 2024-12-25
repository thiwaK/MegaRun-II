@echo off
cd /d "%~dp0"
rem Add a new TAP virtual ethernet adapter
"%~dp0tapinstall.exe" install "%~dp0driver\OemVista.inf" tap0901mr2a
pause
