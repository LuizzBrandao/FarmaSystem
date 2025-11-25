# 🔀 Guia para Fazer Fork do Repositório

Este guia explica como fazer fork do repositório `LuizzBrandao/FarmaSystem:main` e configurar seu repositório local.

## 📋 Pré-requisitos

1. **Conta no GitHub** - Você precisa estar logado
2. **Git instalado** - Baixe em: https://git-scm.com/downloads
3. **Acesso ao repositório** - O repositório `LuizzBrandao/FarmaSystem` deve estar acessível

## 🚀 Passo a Passo

### 1. Fazer Fork no GitHub (Interface Web)

1. Acesse o repositório original:
   ```
   https://github.com/LuizzBrandao/FarmaSystem
   ```

2. Clique no botão **"Fork"** no canto superior direito da página

3. Escolha sua conta/organização onde deseja fazer o fork

4. Aguarde o GitHub criar o fork (geralmente leva alguns segundos)

5. Após o fork, você terá uma cópia em:
   ```
   https://github.com/SEU_USUARIO/FarmaSystem
   ```

### 2. Configurar o Repositório Local

#### Opção A: Clonar o Fork (Recomendado se você ainda não tem o código local)

```bash
# Clone seu fork
git clone https://github.com/SEU_USUARIO/FarmaSystem.git

# Entre no diretório
cd FarmaSystem

# Adicione o repositório original como upstream
git remote add upstream https://github.com/LuizzBrandao/FarmaSystem.git

# Verifique os remotes
git remote -v
```

#### Opção B: Configurar o Repositório Existente (Se você já tem o código)

Se você já tem o código localmente e quer conectar ao fork:

```bash
# Inicialize o repositório Git (se ainda não foi feito)
git init

# Adicione todos os arquivos
git add .

# Faça o commit inicial
git commit -m "Initial commit from fork"

# Adicione seu fork como origin
git remote add origin https://github.com/SEU_USUARIO/FarmaSystem.git

# Adicione o repositório original como upstream
git remote add upstream https://github.com/LuizzBrandao/FarmaSystem.git

# Verifique os remotes
git remote -v

# Faça push para seu fork
git branch -M main
git push -u origin main
```

### 3. Sincronizar com o Repositório Original (Upstream)

Para manter seu fork atualizado com as mudanças do repositório original:

```bash
# Busque as mudanças do upstream
git fetch upstream

# Mude para a branch main
git checkout main

# Mescle as mudanças do upstream
git merge upstream/main

# Envie as atualizações para seu fork
git push origin main
```

### 4. Trabalhar com Branches

Para fazer mudanças sem afetar a branch main:

```bash
# Crie uma nova branch
git checkout -b feature/minha-feature

# Faça suas alterações e commits
git add .
git commit -m "Descrição das mudanças"

# Envie para seu fork
git push origin feature/minha-feature
```

### 5. Criar Pull Request

1. Vá para seu fork no GitHub: `https://github.com/SEU_USUARIO/FarmaSystem`
2. Clique em **"Compare & pull request"**
3. Selecione sua branch e descreva suas mudanças
4. Clique em **"Create pull request"**

## 🔧 Comandos Úteis

### Verificar status
```bash
git status
```

### Ver remotes configurados
```bash
git remote -v
```

### Atualizar fork com upstream
```bash
git fetch upstream
git merge upstream/main
git push origin main
```

### Ver diferenças entre seu fork e upstream
```bash
git fetch upstream
git diff main upstream/main
```

### Listar branches
```bash
git branch -a
```

## ⚠️ Observações Importantes

1. **Não faça push direto para o repositório original** - Use Pull Requests
2. **Mantenha seu fork atualizado** - Sincronize regularmente com upstream
3. **Use branches para features** - Não trabalhe diretamente na main
4. **Commits descritivos** - Use mensagens claras sobre o que foi alterado

## 🆘 Problemas Comuns

### Erro: "remote origin already exists"
```bash
# Remova o remote existente
git remote remove origin

# Adicione novamente
git remote add origin https://github.com/SEU_USUARIO/FarmaSystem.git
```

### Erro: "fatal: not a git repository"
```bash
# Inicialize o repositório
git init
```

### Erro: "Permission denied"
- Verifique se você está autenticado no GitHub
- Use SSH keys ou Personal Access Token

## 📚 Recursos Adicionais

- [Documentação do GitHub sobre Forks](https://docs.github.com/en/get-started/quickstart/fork-a-repo)
- [Guia de Git](https://git-scm.com/doc)
- [GitHub CLI](https://cli.github.com/) - Alternativa à interface web

---

**Nota:** Substitua `SEU_USUARIO` pelo seu nome de usuário do GitHub em todos os comandos.

