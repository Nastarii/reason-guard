# ReasonGuard

🛡️ **Plataforma de Auditoria de Raciocínio de IA**

ReasonGuard é uma plataforma completa para auditoria e análise de raciocínio de sistemas de IA. Funciona como um middleware entre aplicações cliente e LLMs, capturando, analisando e documentando todas as interações.

## 📋 Visão Geral

O sistema oferece cinco módulos principais de análise:

1. **Reasoning Tracer (CoT)** - Rastreamento de Chain-of-Thought
2. **Path Analyzer (ToT)** - Análise de Tree-of-Thought
3. **Logic Validator (GoT)** - Validação de Graph-of-Thought
4. **Consistency Checker** - Verificação de consistência multi-execução
5. **Audit Trail Generator** - Geração de relatórios para diferentes stakeholders

## 🏗️ Arquitetura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Cliente/Demo   │────▶│   ReasonGuard   │────▶│   LLM Provider  │
│   (Streamlit)   │◀────│   (FastAPI)     │◀────│ (OpenAI/Claude) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   PostgreSQL    │
                        │   (Database)    │
                        └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │    Frontend     │
                        │    (React)      │
                        └─────────────────┘
```

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Docker (opcional)

### Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Iniciar o servidor
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Iniciar o servidor de desenvolvimento
npm run dev
```

### Demo (Streamlit)

```bash
cd demo

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env

# Iniciar a demo
streamlit run app.py
```

## 📊 Módulos

### 1. Reasoning Tracer (CoT)

Intercepta requisições e injeta instruções de Chain-of-Thought para extrair:
- Premissas
- Inferências
- Conclusões
- Hash de integridade para auditoria

### 2. Path Analyzer (ToT)

Decompõe problemas em subproblemas e explora múltiplas hipóteses:
- Decomposição automática de problemas
- Exploração em árvore de possibilidades
- Poda de caminhos menos promissores
- Seleção do melhor caminho

### 3. Logic Validator (GoT)

Transforma o raciocínio em grafo de proposições e detecta:
- Contradições
- Saltos lógicos
- Premissas ocultas
- Circularidade

### 4. Consistency Checker

Executa a mesma consulta múltiplas vezes para verificar:
- Taxa de convergência
- Score de confiança
- Pontos divergentes

### 5. Audit Trail Generator

Gera relatórios consolidados em múltiplos formatos:
- **PDF** - Para apresentações e documentação
- **Excel** - Para análise de dados
- **JSON** - Para integração com outros sistemas

Tipos de relatório:
- **Compliance** - Foco em conformidade e auditoria
- **Jurídico** - Foco em trilha de auditoria e evidências
- **Técnico** - Dados completos para análise técnica

## 🔐 Autenticação

O sistema utiliza Clerk para autenticação, suportando:
- Login com E-mail/Senha
- OAuth (Google)
- Proteção de rotas
- Multitenancy (isolamento de dados por usuário)

## 📱 Dashboard

O dashboard oferece:
- KPIs em tempo real
- Visualização interativa de árvores de decisão
- Grafos lógicos interativos
- Filtros para drill-down por decisão
- Histórico de atividades

## 🛠️ API

### Endpoints Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/proxy/chat` | Chat com análise completa |
| GET | `/dashboard/stats` | Estatísticas do dashboard |
| POST | `/reasoning/trace` | Criar rastreamento CoT |
| POST | `/path-analysis/analyze` | Criar análise ToT |
| POST | `/logic/validate` | Validar lógica (GoT) |
| POST | `/consistency/check` | Verificar consistência |
| POST | `/audit/reports` | Gerar relatório |

### Exemplo de Requisição

```bash
curl -X POST "http://localhost:8000/proxy/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "prompt": "Qual a capital do Brasil?",
    "model_provider": "openai",
    "enable_cot": true,
    "enable_tot": false,
    "enable_got": true,
    "enable_consistency": false
  }'
```

## 📁 Estrutura do Projeto

```
reason-guard/
├── backend/
│   ├── app/
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── modules/        # Módulos de análise
│   │   ├── routers/        # Rotas da API
│   │   ├── schemas/        # Schemas Pydantic
│   │   ├── config.py       # Configurações
│   │   ├── database.py     # Conexão com banco
│   │   └── main.py         # Aplicação FastAPI
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── pages/          # Páginas
│   │   ├── services/       # Serviços de API
│   │   └── App.tsx         # Aplicação principal
│   └── package.json
├── demo/
│   ├── app.py              # Demo Streamlit
│   └── requirements.txt
└── README.md
```

## 🔧 Configuração

### Variáveis de Ambiente (Backend)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/reasonguard
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
CLERK_SECRET_KEY=your_clerk_secret_key
SECRET_KEY=your_secret_key
DEBUG=True
```

### Variáveis de Ambiente (Frontend)

```env
VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
VITE_API_URL=http://localhost:8000
```

## 📄 Licença

Este projeto é de uso educacional e demonstrativo.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.
