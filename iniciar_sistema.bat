@echo off
echo ========================================
echo    SISTEMA FARMASYSTEM - INICIANDO
echo ========================================
echo.

cd /d "%~dp0"

echo Configurando PowerShell...
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"

echo.
echo Ativando ambiente virtual...
powershell -Command "& .\venv\Scripts\Activate.ps1; python -c 'import django; print(\"Django\", django.get_version(), \"OK\")'"

echo.
echo ========================================
echo    SISTEMA DISPONIVEL EM:
echo    http://localhost:8000
echo.
echo    LOGIN: admin
echo    SENHA: admin123
echo ========================================
echo.
echo Iniciando servidor Django...
echo Pressione Ctrl+C para parar o servidor
echo.

powershell -Command "& .\venv\Scripts\Activate.ps1; python manage.py runserver"
