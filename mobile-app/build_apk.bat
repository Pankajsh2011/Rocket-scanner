@echo off
setlocal enabledelayedexpansion
title RocketScan - Mobile App Build Tool
color 0A

echo ======================================================================
echo    ROCKETSCAN - MOBILE APP (ANDROID & iOS) BUILDER
echo    NSE & BSE 4,200+ Stocks · 20%+ Circuit Rockets · Google AdMob
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Node.js environment...
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not found in PATH! Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)
node -v
npm -v

echo.
echo [2/4] Installing / Updating Capacitor & AdMob Dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] npm install had warnings, continuing...
)

echo.
echo [3/4] Syncing Web Assets with Android & iOS Native Projects...
call npx cap sync
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Running initial cap add if needed...
    call npx cap add android
    call npx cap add ios
    call npx cap sync
)

echo.
echo [4/4] Build Options:
echo   [1] Open in Android Studio (Recommended for debug & testing)
echo   [2] Build Release APK (gradlew assembleRelease)
echo   [3] Build Google Play Store AAB Bundle (gradlew bundleRelease)
echo   [4] Open in Xcode (macOS only for iOS App Store)
echo   [5] Exit
echo.

set /p choice="Select an option (1-5): "

if "%choice%"=="1" (
    echo Opening Android Studio...
    call npx cap open android
    goto done
)

if "%choice%"=="2" (
    echo Building Release APK...
    cd android
    if exist "gradlew.bat" (
        call gradlew.bat assembleRelease
        echo.
        echo APK Build Finished! Locate output at:
        echo   android\app\build\outputs\apk\release\app-release-unsigned.apk
    ) else (
        echo [INFO] Please open Android Studio with Option 1 to compile.
    )
    cd ..
    goto done
)

if "%choice%"=="3" (
    echo Building Google Play Store AAB Bundle...
    cd android
    if exist "gradlew.bat" (
        call gradlew.bat bundleRelease
        echo.
        echo AAB Bundle Finished! Locate output at:
        echo   android\app\build\outputs\bundle\release\app-release.aab
    ) else (
        echo [INFO] Please open Android Studio with Option 1 to compile.
    )
    cd ..
    goto done
)

if "%choice%"=="4" (
    echo Opening Xcode...
    call npx cap open ios
    goto done
)

:done
echo.
echo ======================================================================
echo [SUCCESS] Operation completed. Press any key to exit.
echo ======================================================================
pause
