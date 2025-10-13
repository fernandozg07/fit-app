#!/usr/bin/env python
"""
Script para corrigir problemas do projeto FIT-APP
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_app.settings')
django.setup()

def fix_database():
    """Corrige problemas do banco de dados"""
    from django.core.management import execute_from_command_line
    
    print("🔧 Aplicando migrações...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("✅ Banco de dados corrigido!")

def create_superuser():
    """Cria superusuário se não existir"""
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    if not User.objects.filter(email='admin@fitapp.com').exists():
        User.objects.create_superuser(
            email='admin@fitapp.com',
            password='admin123',
            first_name='Admin',
            last_name='FitApp'
        )
        print("✅ Superusuário criado: admin@fitapp.com / admin123")
    else:
        print("ℹ️ Superusuário já existe")

def collect_static():
    """Coleta arquivos estáticos"""
    from django.core.management import execute_from_command_line
    
    print("📁 Coletando arquivos estáticos...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    print("✅ Arquivos estáticos coletados!")

def main():
    """Executa todas as correções"""
    print("🚀 Iniciando correções do FIT-APP...")
    
    try:
        fix_database()
        create_superuser()
        collect_static()
        
        print("\n🎉 Todas as correções aplicadas com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Backend: python manage.py runserver")
        print("2. Frontend: cd frontend && npm start")
        print("3. Acesse: http://localhost:3000")
        
    except Exception as e:
        print(f"❌ Erro durante as correções: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()