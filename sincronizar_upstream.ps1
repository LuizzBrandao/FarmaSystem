# Script para sincronizar seu fork com o repositório original (upstream)

Write-Host "🔄 Sincronizando com o repositório original..." -ForegroundColor Cyan
Write-Host ""

# Verificar se está em um repositório Git
if (-not (Test-Path .git)) {
    Write-Host "❌ Este diretório não é um repositório Git!" -ForegroundColor Red
    exit 1
}

# Verificar se upstream está configurado
$upstream = git remote get-url upstream 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Remote 'upstream' não configurado!" -ForegroundColor Red
    Write-Host "   Execute primeiro: configurar_fork.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "📡 Buscando atualizações do upstream..." -ForegroundColor Yellow
git fetch upstream

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao buscar do upstream!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Atualizações buscadas" -ForegroundColor Green
Write-Host ""

# Verificar branch atual
$branchAtual = git branch --show-current
Write-Host "📍 Branch atual: $branchAtual" -ForegroundColor Cyan

# Perguntar se deseja mesclar
$resposta = Read-Host "Deseja mesclar as mudanças do upstream/main para $branchAtual? (s/n)"
if ($resposta -ne "s" -and $resposta -ne "S") {
    Write-Host "⚠️  Operação cancelada" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🔀 Mesclando mudanças..." -ForegroundColor Yellow
git merge upstream/main

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao mesclar! Pode haver conflitos." -ForegroundColor Red
    Write-Host "   Resolva os conflitos manualmente e depois faça commit." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Mudanças mescladas com sucesso!" -ForegroundColor Green
Write-Host ""

# Perguntar se deseja fazer push
$resposta = Read-Host "Deseja enviar as mudanças para seu fork? (s/n)"
if ($resposta -eq "s" -or $resposta -eq "S") {
    Write-Host ""
    Write-Host "📤 Enviando para seu fork..." -ForegroundColor Yellow
    git push origin $branchAtual
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Sincronização concluída!" -ForegroundColor Green
    } else {
        Write-Host "❌ Erro ao enviar para seu fork!" -ForegroundColor Red
    }
} else {
    Write-Host "⚠️  Mudanças locais não foram enviadas" -ForegroundColor Yellow
}

Write-Host ""

