@echo off
echo ========================================
echo    FIT-APP - Iniciando Desenvolvimento
echo ========================================

echo.
echo [1/4] Instalando dependencias do backend...
pip install -r requirements.txt

echo.
echo [2/4] Aplicando migracoes do banco de dados...
python manage.py makemigrations
python manage.py migrate

echo.
echo [3/4] Criando superusuario (se necessario)...
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@fitapp.com').exists():
    User.objects.create_superuser('admin@fitapp.com', 'admin123')
    print('Superusuario criado: admin@fitapp.com / admin123')
else:
    print('Superusuario ja existe')
"

echo.
echo [4/4] Instalando dependencias do frontend...
cd frontend
npm install
cd ..

echo.
echo ========================================
echo    CONFIGURACAO CONCLUIDA!
echo ========================================
echo.
echo Para iniciar o projeto:
echo   Backend:  python manage.py runserver
echo   Frontend: cd frontend ^&^& npm start
echo.
echo Acesse: http://localhost:3000
echo Admin:  http://localhost:8000/admin
echo API:    http://localhost:8000/swagger
echo.
pause