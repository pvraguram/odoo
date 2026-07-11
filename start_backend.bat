@echo off
echo Cleaning old generated files...
if exist outputs (
    del /q outputs\*.png
)

echo Starting FastAPI Backend Server on port 8000...
echo Frontend will connect to: http://localhost:8000
echo.

start http://localhost:8000/improved.html
cd backend\app
uvicorn main:app --reload --host 0.0.0.0 --port 8000