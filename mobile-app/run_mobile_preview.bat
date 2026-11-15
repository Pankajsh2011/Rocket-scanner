@echo off
title RocketScan Mobile App Preview
color 0B
echo ======================================================================
echo    ROCKETSCAN - MOBILE APP LOCAL PREVIEW SERVER
echo ======================================================================
echo.

cd /d "%~dp0\www"
echo Serving www folder on http://localhost:8080...
echo Open your mobile browser or desktop browser (Press F12 -> Device Mode)
echo.

python -m http.server 8080
pause
