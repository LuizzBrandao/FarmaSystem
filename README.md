# 💊 FarmaSystem - Sistema de Gerenciamento de Farmácia

Um sistema completo e moderno para gerenciamento de estoque de medicamentos em múltiplas filiais, desenvolvido com Django 4.2 e interface responsiva. Sistema robusto com sincronização em tempo real, transferências entre filiais com transações atômicas e geração de relatórios em PDF.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/django-4.2-green.svg)
![SQLite](https://img.shields.io/badge/database-SQLite-blue.svg)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue.svg)

## 🚀 Características Principais

### 📊 Dashboard Inteligente
- Visão geral em tempo real do estoque
- Alertas automáticos para medicamentos vencidos ou com estoque baixo
- Estatísticas e métricas importantes
- Gráficos interativos de movimentação

### 💊 Gerenciamento de Medicamentos
- CRUD completo de medicamentos
- Categorização por tipos de medicamentos
- Controle de códigos de barras
- Upload de imagens dos produtos
- Informações detalhadas (princípio ativo, dosagem, forma farmacêutica)

### 📦 Controle de Estoque
- Controle de estoque por filial
- Entrada e saída de produtos
- Histórico completo de movimentações
- Alertas automáticos para estoque baixo
- Controle de medicamentos próximos ao vencimento
- Sincronização em tempo real entre frontend e backend

### 🏢 Gestão de Filiais
- Cadastro completo de filiais
- Controle de estoque por filial
- Transferências entre filiais com transações atômicas
- Dashboard individual por filial
- Sincronização de dados em tempo real

### 👥 Gestão de Fornecedores
- Cadastro completo de fornecedores
- Informações de contato e dados comerciais
- Histórico de relacionamento

### 📋 Sistema de Relatórios
- Relatórios de estoque em PDF (WeasyPrint/ReportLab)
- Relatórios de movimentação
- Relatórios de vencimentos
- Geração de PDFs com fallback automático
- Templates HTML para PDFs

### 🔔 Sistema de Notificações
- Notificações por email
- Notificações por WhatsApp (via API)
- Alertas de estoque baixo
- Alertas de vencimento próximo

### 👥 Sistema de Usuários
- Controle de acesso por perfis (Admin, Farmacêutico, Operador)
- Sistema de autenticação seguro
- Perfis personalizáveis

## 🛠️ Tecnologias Utilizadas

### Linguagens de Programação
- **Python 3.8+** - Linguagem principal do backend
- **HTML5** - Estrutura semântica das páginas
- **CSS3** - Estilização com variáveis customizadas e animações
- **JavaScript ES6+** - Interatividade e sincronização em tempo real (Vanilla JS)

### Framework e Backend
- **Django 4.2** - Framework web Python
  - Django Admin - Interface administrativa
  - Django ORM - Mapeamento objeto-relacional
  - Django Templates - Sistema de templates
  - Django Sessions - Gerenciamento de sessões
  - Django Messages - Sistema de mensagens
  - Django Middleware - Processamento de requisições/respostas

### Banco de Dados
- **SQLite3** - Banco de dados para desenvolvimento
- **PostgreSQL** - Suporte via psycopg2-binary (produção)

### Bibliotecas Python

#### Geração de PDFs
- **WeasyPrint 60.2+** - Geração de PDFs a partir de HTML/CSS (preferido)
- **ReportLab 4.0.4+** - Geração de PDFs programática (fallback)

#### Processamento de Imagens
- **Pillow 10.1.0+** - Processamento e manipulação de imagens

#### Utilitários Django
- **django-crispy-forms 2.0** - Formulários estilizados
- **django-extensions 3.2.3** - Extensões úteis para desenvolvimento
- **python-decouple 3.8** - Gerenciamento de variáveis de ambiente

#### Servidor e Performance
- **WhiteNoise 6.5.0** - Servir arquivos estáticos em produção
- **psycopg2-binary 2.9.6** - Driver PostgreSQL para Python

#### Processamento de Dados
- **charset-normalizer 3.4.0+** - Normalização de encoding de caracteres
- **requests 2.31.0+** - Requisições HTTP (para APIs externas)
- **cffi 1.16.0+** - Interface C Foreign Function (dependência do WeasyPrint)

### Frontend e UI

#### Bibliotecas de Ícones e Fontes
- **Font Awesome** - Biblioteca de ícones vetoriais
- **Google Fonts (Inter)** - Tipografia moderna

#### Recursos de UX/UI
- Design responsivo (Mobile-first)
- Animações CSS suaves
- Tema moderno com paleta de cores profissional
- Micro-interações para melhor experiência
- Loading screens e feedbacks visuais
- Sincronização em tempo real via AJAX/Fetch API

### Arquitetura e Padrões
- **MVC/MVT** - Arquitetura Django (Model-View-Template)
- **RESTful APIs** - Endpoints JSON para sincronização
- **Transações Atômicas** - Garantia de consistência de dados
- **Database Locks** - Prevenção de condições de corrida
- **Middleware Customizado** - Processamento de requisições/respostas

## 📁 Estrutura do Projeto

```
pharmacy_management/
├── 📁 apps/
│   ├── 📁 core/              # Dashboard e funcionalidades gerais
│   ├── 📁 authentication/    # Sistema de usuários e autenticação
│   ├── 📁 inventory/         # Medicamentos, estoque e categorias
│   ├── 📁 suppliers/         # Gestão de fornecedores
│   ├── 📁 branches/          # Gestão de filiais e transferências
│   ├── 📁 reports/           # Sistema de relatórios e PDFs
│   └── 📁 notifications/     # Sistema de notificações
├── 📁 static/
│   ├── 📁 css/              # Estilos CSS (main.css, modern-dashboard.css, dark-theme.css)
│   ├── 📁 js/               # JavaScript (main.js, modern-dashboard.js)
│   └── 📁 images/           # Imagens e ícones
├── 📁 templates/
│   ├── 📄 base.html         # Template base
│   ├── 📁 auth/             # Templates de autenticação
│   ├── 📁 inventory/        # Templates do inventário
│   ├── 📁 branches/         # Templates de filiais
│   ├── 📁 reports/          # Templates de relatórios
│   └── 📁 components/       # Componentes reutilizáveis
├── 📁 media/                # Upload de arquivos
├── 📁 scripts/              # Scripts utilitários
│   ├── fix_duplicate_stocks.py
│   ├── check_branch_stats.py
│   └── create_admin_user.py
├── 📁 logs/                 # Logs do sistema
├── 📄 manage.py
├── 📄 requirements.txt
└── 📄 README.md
```

## ⚡ Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/farmasystem.git
cd farmasystem
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

**Nota:** No Windows, o WeasyPrint pode requerer bibliotecas GTK+ adicionais. Se encontrar erros, o sistema automaticamente usará ReportLab como fallback.

### 4. Configure o banco de dados
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. (Opcional) Popule dados de exemplo
```bash
python populate_data.py
python add_marilia_branches.py
```

### 6. Crie um superusuário
```bash
python manage.py createsuperuser
```

Ou use o script:
```bash
python scripts/create_admin_user.py
```

### 7. Execute o servidor
```bash
python manage.py runserver
```

**Windows:** Você também pode usar os scripts:
- `iniciar_sistema.bat` (CMD)
- `iniciar_sistema.ps1` (PowerShell)

### 8. Acesse o sistema
Abra seu navegador e acesse: `http://localhost:8000`

### 9. (Opcional) Verificar e corrigir duplicidades
```bash
# Verificar duplicidades (simulação)
python scripts/fix_duplicate_stocks.py

# Corrigir duplicidades (aplicar mudanças)
python scripts/fix_duplicate_stocks.py --fix
```

## 👤 Usuários de Teste

**Administrador:**
- Usuário: `admin`
- Senha: `admin123`

## 🎨 Interface e Design

### Paleta de Cores
- **Primária:** `#2563eb` (Azul profissional)
- **Secundária:** `#10b981` (Verde saúde)
- **Sucesso:** `#22c55e`
- **Aviso:** `#f59e0b`
- **Erro:** `#ef4444`
- **Neutros:** Tons de cinza do `#111827` ao `#f9fafb`

### Componentes de Interface
- **Cards** modernos com sombras suaves
- **Botões** com animações de hover
- **Formulários** com validação em tempo real
- **Tabelas** responsivas com paginação
- **Modais** para ações importantes
- **Alertas** informativos e dismiss automático

## 📱 Responsividade

O sistema é totalmente responsivo e otimizado para:
- 📱 **Mobile** (320px+)
- 📱 **Tablet** (768px+)
- 💻 **Desktop** (1024px+)
- 🖥️ **Large Desktop** (1440px+)

## 🔒 Segurança e Performance

### Recursos de Segurança
- Autenticação obrigatória para todas as páginas
- Proteção CSRF em formulários
- Validação de dados no frontend e backend
- Controle de acesso baseado em perfis
- Sanitização de inputs
- Headers de segurança configurados
- Transações atômicas para operações críticas
- Database locks (select_for_update) para prevenir condições de corrida

### Perfis de Usuário
- **Administrador:** Acesso total ao sistema
- **Farmacêutico:** Gestão de medicamentos e relatórios
- **Operador:** Operações básicas de estoque

### Otimizações
- Queries otimizadas com select_related e prefetch_related
- Operações atômicas usando F() expressions
- Sincronização em tempo real via AJAX
- Cache de estatísticas (com atualização automática)
- Paginação de resultados grandes

## 📊 Funcionalidades Detalhadas

### Dashboard
- Cards com estatísticas principais
- Lista de medicamentos com estoque baixo
- Alertas de vencimento próximo
- Movimentações recentes
- Ações rápidas para tarefas comuns

### Medicamentos
- Cadastro com informações completas
- Upload de imagem do produto
- Código de barras único
- Categorização
- Controle de estoque mínimo
- Status ativo/inativo

### Estoque
- Controle de estoque por filial
- Datas de validade
- Entrada e saída com motivos
- Histórico completo de movimentações
- Alertas automáticos
- Sincronização em tempo real
- Prevenção de duplicidades

### Filiais
- Gestão de múltiplas filiais
- Transferências entre filiais
- Transações atômicas para garantir consistência
- Dashboard individual por filial
- Estatísticas em tempo real

### Fornecedores
- Dados comerciais completos
- Informações de contato
- CNPJ e validações
- Histórico de relacionamento

## 🎯 Funcionalidades Implementadas

- [x] Sistema de gerenciamento de medicamentos
- [x] Controle de estoque por filial
- [x] Transferências entre filiais com transações atômicas
- [x] Sistema de relatórios em PDF (WeasyPrint/ReportLab)
- [x] Notificações por email e WhatsApp
- [x] Sincronização em tempo real frontend/backend
- [x] Prevenção de duplicidades em transferências
- [x] Sistema de autenticação e perfis de usuário
- [x] Dashboard com estatísticas em tempo real
- [x] Interface responsiva e moderna

## 🚧 Próximas Funcionalidades

- [ ] Sistema de vendas/dispensação
- [ ] Integração com código de barras
- [ ] Relatórios avançados com gráficos
- [ ] API REST completa para integrações
- [ ] Sistema de backup automático
- [ ] Dark mode
- [ ] Exportação para Excel
- [ ] Controle de prescrições médicas
- [ ] App mobile

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🔧 Scripts Utilitários

O projeto inclui vários scripts para facilitar o gerenciamento:

- `scripts/create_admin_user.py` - Criar usuário administrador
- `scripts/fix_duplicate_stocks.py` - Verificar e corrigir duplicidades em BranchStock
- `scripts/check_branch_stats.py` - Verificar estatísticas das filiais
- `scripts/db_deduplicate.py` - Remover duplicidades do banco de dados
- `populate_data.py` - Popular dados de exemplo
- `add_marilia_branches.py` - Adicionar filiais de exemplo em Marília-SP

## 📚 Documentação Adicional

- `IMPLEMENTACAO.md` - Detalhes de implementação
- `SOLUCAO_PROBLEMAS.md` - Soluções para problemas comuns
- `SINCRONIZACAO_IMPLEMENTADA.md` - Documentação de sincronização
- `CORRECAO_ENCODING.md` - Correções de encoding
- `GUIA_FILIAIS_NOTIFICACOES.md` - Guia de filiais e notificações
- `ACESSO_RAPIDO.md` - Guia de acesso rápido

## 🆘 Suporte

Para suporte e dúvidas:
- 📧 Email: suporte@farmasystem.com
- 📱 WhatsApp: (11) 99999-9999
- 🌐 Website: [www.farmasystem.com](https://www.farmasystem.com)

## 📦 Dependências Completas

Todas as dependências estão listadas em `requirements.txt`:

```
Django==4.2.0
Pillow>=10.1.0
reportlab>=4.0.4
weasyprint>=60.2
django-crispy-forms==2.0
python-decouple==3.8
whitenoise==6.5.0
psycopg2-binary==2.9.6
django-extensions==3.2.3
charset-normalizer>=3.4.0
requests>=2.31.0
cffi>=1.16.0
```

## 🙏 Agradecimentos

- **Font Awesome** pelos ícones
- **Google Fonts** pela tipografia Inter
- **Comunidade Django** pelo framework incrível
- **WeasyPrint** e **ReportLab** pelas bibliotecas de PDF
- Todos os contribuidores do projeto

---

<div align="center">
  <strong>Desenvolvido com ❤️ para a área da saúde</strong>
  <br>
  <sub>© 2024 FarmaSystem. Todos os direitos reservados.</sub>
</div>
