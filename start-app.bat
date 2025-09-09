@echo off
echo ========================================
echo    INICIANDO FITNESS APP COMPLETO
echo ========================================
echo.

echo [1/3] Verificando dependencias do backend...
cd /d "%~dp0"
if not exist "venv\" (
    echo Criando ambiente virtual...
    python -m venv venv
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Instalando dependencias do Django...
pip install -r requirements.txt

echo.
echo [2/3] Verificando dependencias do frontend...
cd frontend
if not exist "node_modules\" (
    echo Instalando dependencias do React...
    call npm install
)

echo.
echo [3/3] Iniciando servidores...
echo.

echo Iniciando backend Django em http://localhost:8000
start cmd /k "cd /d \"%~dp0\" && call venv\Scripts\activate.bat && python manage.py runserver"

timeout /t 5 /nobreak >nul

echo Iniciando frontend React em http://localhost:3000
start cmd /k "cd /d \"%~dp0frontend\" && call npm start"

echo.
echo ========================================
echo     APLICACAO INICIADA COM SUCESSO!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/swagger/
echo.
echo Pressione qualquer tecla para fechar...
pause >nul