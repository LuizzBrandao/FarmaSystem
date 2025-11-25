# Script para configurar o fork do repositório FarmaSystem
# Execute este script após fazer o fork no GitHub

Write-Host "🔀 Configurando Fork do FarmaSystem" -ForegroundColor Cyan
Write-Host ""

# Solicitar informações do usuário
$seuUsuario = Read-Host "Digite seu nome de usuário do GitHub"
$repoOriginal = "LuizzBrandao/FarmaSystem"
$seuFork = "$seuUsuario/FarmaSystem"

Write-Host ""
Write-Host "📋 Configuração:" -ForegroundColor Yellow
Write-Host "  Repositório Original: $repoOriginal"
Write-Host "  Seu Fork: $seuFork"
Write-Host ""

# Verificar se Git está instalado
try {
    $gitVersion = git --version
    Write-Host "✅ Git encontrado: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git não encontrado!" -ForegroundColor Red
    Write-Host "   Por favor, instale o Git: https://git-scm.com/downloads" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Verificar se já é um repositório Git
if (Test-Path .git) {
    Write-Host "✅ Repositório Git já inicializado" -ForegroundColor Green
    
    # Verificar remotes existentes
    $remotes = git remote -v 2>&1
    if ($remotes) {
        Write-Host ""
        Write-Host "📡 Remotes atuais:" -ForegroundColor Yellow
        Write-Host $remotes
        Write-Host ""
        
        $resposta = Read-Host "Deseja reconfigurar os remotes? (s/n)"
        if ($resposta -eq "s" -or $resposta -eq "S") {
            # Remover remotes existentes
            git remote remove origin 2>$null
            git remote remove upstream 2>$null
            Write-Host "✅ Remotes removidos" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Mantendo remotes existentes" -ForegroundColor Yellow
            exit 0
        }
    }
} else {
    Write-Host "📦 Inicializando repositório Git..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Repositório inicializado" -ForegroundColor Green
}

Write-Host ""

# Adicionar remotes
Write-Host "🔗 Configurando remotes..." -ForegroundColor Yellow

# Adicionar origin (seu fork)
try {
    git remote add origin "https://github.com/$seuFork.git"
    Write-Host "✅ Origin configurado: $seuFork" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Erro ao adicionar origin (pode já existir)" -ForegroundColor Yellow
}

# Adicionar upstream (repositório original)
try {
    git remote add upstream "https://github.com/$repoOriginal.git"
    Write-Host "✅ Upstream configurado: $repoOriginal" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Erro ao adicionar upstream (pode já existir)" -ForegroundColor Yellow
}

Write-Host ""

# Verificar remotes configurados
Write-Host "📡 Remotes configurados:" -ForegroundColor Cyan
git remote -v

Write-Host ""
Write-Host "✅ Configuração concluída!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Próximos passos:" -ForegroundColor Yellow
Write-Host "  1. Certifique-se de que fez o fork no GitHub"
Write-Host "  2. Adicione seus arquivos: git add ."
Write-Host "  3. Faça o commit: git commit -m 'Initial commit'"
Write-Host "  4. Envie para seu fork: git push -u origin main"
Write-Host ""
Write-Host "💡 Para sincronizar com o upstream:" -ForegroundColor Cyan
Write-Host "  git fetch upstream"
Write-Host "  git merge upstream/main"
Write-Host "  git push origin main"
Write-Host ""

