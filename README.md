# 💊 FarmaSystem - Sistema de Gerenciamento de Farmácia

Um sistema completo e moderno para gerenciamento de estoque de medicamentos, desenvolvido com Django e interface responsiva em CSS puro.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/django-4.2-green.svg)

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
- Controle de lotes e datas de validade
- Entrada e saída de produtos
- Histórico completo de movimentações
- Alertas automáticos para estoque baixo
- Controle de medicamentos próximos ao vencimento

### 🏢 Gestão de Fornecedores
- Cadastro completo de fornecedores
- Informações de contato e dados comerciais
- Histórico de compras por fornecedor

### 📋 Sistema de Relatórios
- Relatórios de estoque em PDF
- Relatórios de movimentação
- Relatórios de vencimentos
- Exportação de dados

### 👥 Sistema de Usuários
- Controle de acesso por perfis (Admin, Farmacêutico, Operador)
- Sistema de autenticação seguro
- Perfis personalizáveis

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.8+**
- **Django 4.2** - Framework web
- **SQLite** - Banco de dados (desenvolvimento)
- **Pillow** - Processamento de imagens

### Frontend
- **HTML5** semântico
- **CSS3** com variáveis customizadas
- **JavaScript ES6+** vanilla
- **Font Awesome** - Ícones
- **Google Fonts** - Tipografia (Inter)

### Recursos de UX/UI
- Design responsivo (Mobile-first)
- Animações CSS suaves
- Tema moderno com paleta de cores profissional
- Micro-interações para melhor experiência
- Loading screens e feedbacks visuais

## 📁 Estrutura do Projeto

```
pharmacy_management/
├── 📁 apps/
│   ├── 📁 core/              # Dashboard e funcionalidades gerais
│   ├── 📁 authentication/    # Sistema de usuários e autenticação
│   ├── 📁 inventory/         # Medicamentos, estoque e categorias
│   ├── 📁 suppliers/         # Gestão de fornecedores
│   └── 📁 reports/           # Sistema de relatórios
├── 📁 static/
│   ├── 📁 css/              # Estilos CSS
│   ├── 📁 js/               # JavaScript
│   └── 📁 images/           # Imagens e ícones
├── 📁 templates/
│   ├── 📄 base.html         # Template base
│   ├── 📁 auth/             # Templates de autenticação
│   ├── 📁 inventory/        # Templates do inventário
│   └── 📁 components/       # Componentes reutilizáveis
├── 📁 media/                # Upload de arquivos
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

### 4. Configure o banco de dados
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crie um superusuário
```bash
python manage.py createsuperuser
```

### 6. Execute o servidor
```bash
python manage.py runserver
```

### 7. Acesse o sistema
Abra seu navegador e acesse: `http://localhost:8000`

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

## 🔒 Segurança

### Recursos Implementados
- Autenticação obrigatória para todas as páginas
- Proteção CSRF em formulários
- Validação de dados no frontend e backend
- Controle de acesso baseado em perfis
- Sanitização de inputs
- Headers de segurança configurados

### Perfis de Usuário
- **Administrador:** Acesso total ao sistema
- **Farmacêutico:** Gestão de medicamentos e relatórios
- **Operador:** Operações básicas de estoque

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
- Controle por lotes
- Datas de validade
- Entrada e saída com motivos
- Histórico completo de movimentações
- Alertas automáticos

### Fornecedores
- Dados comerciais completos
- Informações de contato
- CNPJ e validações
- Histórico de relacionamento

## 🎯 Próximas Funcionalidades

- [ ] Sistema de vendas/dispensação
- [ ] Integração com código de barras
- [ ] Relatórios avançados com gráficos
- [ ] API REST para integrações
- [ ] Sistema de backup automático
- [ ] Notificações por email
- [ ] Dark mode
- [ ] Exportação para Excel
- [ ] Controle de prescrições médicas

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

Para suporte e dúvidas:
- 📧 Email: suporte@farmasystem.com
- 📱 WhatsApp: (11) 99999-9999
- 🌐 Website: [www.farmasystem.com](https://www.farmasystem.com)

## 🙏 Agradecimentos

- Font Awesome pelos ícones
- Google Fonts pela tipografia Inter
- Comunidade Django pelo framework incrível
- Todos os contribuidores do projeto

---

<div align="center">
  <strong>Desenvolvido com ❤️ para a área da saúde</strong>
  <br>
  <sub>© 2024 FarmaSystem. Todos os direitos reservados.</sub>
</div>
