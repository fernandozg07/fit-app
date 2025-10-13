@echo off
echo ========================================
echo    FIT-APP - PROJETO CORRIGIDO
echo ========================================

echo.
echo [1/3] Aplicando correcoes automaticas...
python fix-project.py

echo.
echo [2/3] Instalando dependencias do frontend...
cd frontend
call npm install
cd ..

echo.
echo [3/3] Projeto pronto para uso!
echo.
echo ========================================
echo    COMO USAR:
echo ========================================
echo.
echo 1. Backend:  python manage.py runserver
echo 2. Frontend: cd frontend ^&^& npm start
echo.
echo Acesse: http://localhost:3000
echo Admin:  http://localhost:8000/admin
echo API:    http://localhost:8000/swagger
echo.
echo Login Admin: admin@fitapp.com / admin123
echo.
pause