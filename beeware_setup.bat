@echo off
REM Ensure pip is up to date
python -m pip install --upgrade pip

REM Install BeeWare Briefcase
pip install briefcase

REM Create a new BeeWare project (user will be prompted for details)
briefcase new

echo.
echo ==========================================
echo BeeWare project created!
echo.
echo To run your app on Windows desktop:
echo   cd <your-app-directory>
echo   briefcase dev
echo.
echo To build for Android, copy your project to WSL or a Linux VM and run:
echo   pip install briefcase
echo   briefcase create android
echo   briefcase build android
echo   briefcase run android
echo.
echo For more info, see: https://docs.beeware.org/en/latest/tutorial/tutorial-0.html
echo ==========================================
pause 