@echo off
echo ===========================================
echo Setting up the Machine Learning Environment
echo ===========================================

echo.
echo Installing Python backend dependencies...
pip install -r requirements.txt

echo.
echo Installing Node.js frontend dependencies...
cd frontend
call npm install

echo.
echo Starting FastAPI backend and Vite frontend...
npm run dev:all
