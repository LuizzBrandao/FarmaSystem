#!/usr/bin/env powershell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    SISTEMA FARMASYSTEM - INICIANDO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navegar para o diretório do script
Set-Location $PSScriptRoot

Write-Host "Configurando ambiente..." -ForegroundColor Yellow
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

Write-Host "Verificando Django..." -ForegroundColor Yellow
python -c "import django; print('Django', django.get_version(), 'OK')"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "    SISTEMA DISPONIVEL EM:" -ForegroundColor Green
Write-Host "    http://localhost:8000" -ForegroundColor White
Write-Host "" 
Write-Host "    LOGIN: admin" -ForegroundColor White
Write-Host "    SENHA: admin123" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Iniciando servidor Django..." -ForegroundColor Yellow
Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Red
Write-Host ""

# Iniciar servidor Django
python manage.py runserver
