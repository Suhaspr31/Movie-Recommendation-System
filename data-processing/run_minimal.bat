@echo off
REM Ultra-Minimal Spark ALS Training Launcher for Low-Memory Systems
REM Save this as run_minimal.bat in your data-processing folder

echo ================================================
echo Ultra-Minimal Spark ALS Training
echo For Low-Memory Windows Systems
echo ================================================
echo.

REM Set minimal Java heap size
set JAVA_OPTS=-Xmx512m -Xms256m -Xss2m -XX:+UseSerialGC
set _JAVA_OPTIONS=-Xmx512m -Xms256m -Xss2m

REM Set Spark memory
set SPARK_DRIVER_MEMORY=512m
set SPARK_EXECUTOR_MEMORY=512m

REM Set Python unbuffered for immediate output
set PYTHONUNBUFFERED=1

echo Java Options: %JAVA_OPTS%
echo Spark Driver Memory: %SPARK_DRIVER_MEMORY%
echo.

echo Starting training...
echo This will take several minutes. Please be patient.
echo.

REM Run the Python script with the virtual environment
if exist "venv\Scripts\python.exe" (
    echo Using virtual environment...
    venv\Scripts\python.exe main.py
) else (
    echo Using system Python...
    python main.py
)

if errorlevel 1 (
    echo.
    echo ================================================
    echo TRAINING FAILED!
    echo ================================================
    echo.
    echo If you see "Could not reserve enough space" error:
    echo   1. Close ALL other applications
    echo   2. Restart your computer
    echo   3. Run ONLY this script
    echo.
    echo If you see Stack Overflow error:
    echo   - Your dataset may still be too large
    echo   - Try reducing sample_rate in main.py to 0.0005
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo TRAINING COMPLETED SUCCESSFULLY!
echo ================================================
echo.
echo Model saved to: models\als_model
echo.
pause