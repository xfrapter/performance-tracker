@echo off
echo ==========================================
echo  Performance Tracker APK Builder (Docker)
echo ==========================================
echo.
echo This script builds your Android APK using Docker
echo No WSL, VM, or complex setup required!
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running
    echo.
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo Docker found! Starting APK build...
echo.

REM Create the build directory if it doesn't exist
if not exist "android_build" mkdir android_build

REM Copy main files to build directory
copy main.py android_build\
copy buildozer.spec android_build\
copy requirements.txt android_build\
if exist "data" xcopy /E /I data android_build\data

REM Change to build directory
cd android_build

echo Building APK with Docker...
echo This may take 15-30 minutes on first run (downloads Android SDK/NDK)
echo.

REM Run buildozer in Docker container
docker run --rm -v "%cd%":/home/user/hostcwd kivy/buildozer android debug

if errorlevel 0 (
    echo.
    echo ==========================================
    echo  BUILD SUCCESSFUL! 
    echo ==========================================
    echo.
    echo Your APK is ready at:
    echo %cd%\bin\
    echo.
    echo Look for: performancetracker-*-debug.apk
    echo.
    echo You can install this on your Android device!
    echo ==========================================
) else (
    echo.
    echo BUILD FAILED - Check the output above for errors
    echo.
)

echo.
pause 