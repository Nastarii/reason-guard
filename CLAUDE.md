Atue como um Engenheiro de Software Full-Stack Sênior e Especialista em IA. Sua tarefa é criar o ReasonGuard, uma plataforma de auditoria de raciocínio de IA, do zero

# Pilha Tecnológica

Backend: Python (FastAPI) para atuar como middleware de observabilidade.

Frontend: React (utilizando bibliotecas de visualização como D3.js ou React Flow para grafos e árvores).

Banco de Dados: PostgreSQL

# Arquitetura do Sistema

O sistema deve funcionar como um middleware entre uma aplicação cliente e um LLM. Toda interação deve ser capturada, analisada e documentada. Implemente o modo de integração através de API Proxy

# Implementação dos Módulos Core

Implemente os seguintes módulos baseados nas especificações:


Módulo 1: Reasoning Tracer (CoT): Intercepta requisições, injeta instruções de Chain-of-Thought, realiza o parsing da resposta para extrair premissas e passos intermediários, e armazena tudo em JSON com hash de integridade.


Módulo 2: Path Analyzer (ToT): Decompõe problemas em subproblemas, explora múltiplas hipóteses em paralelo (árvore de possibilidades) e documenta a poda de caminhos menos promissores.


Módulo 3: Logic Validator (GoT): Transforma o raciocínio em um grafo de proposições. Deve detectar contradições, saltos lógicos, premissas ocultas e circularidade.


Módulo 4: Consistency Checker: Executa a mesma consulta múltiplas vezes com variações, calcula a taxa de convergência e gera um score de confiança.


Módulo 5: Audit Trail Generator: Consolida os dados em relatórios PDF, JSON e Excel para diferentes stakeholders (Compliance, Jurídico, Técnico).

# Dashboard (Frontend React)

Crie uma interface que contenha:

Visualização interativa da árvore de decisão (Path Analyzer).

Visualização de grafos lógicos (Logic Validator).

KPIs em tempo real: Total de decisões, Taxa de Consistência e Alertas Críticos.

Filtros para drill-down por decisão individual.

# Implementação do sistema de autenticação

Configuração e Provedor:

Configurar o Clerk como provedor principal de autenticação.

Implementar suporte para login via E-mail/Senha e OAuth (Google).

Fluxo de Registro e Login:

Criar páginas customizadas de /sign-in e /sign-up utilizando os componentes.

Garantir que o redirecionamento pós-login leve o usuário para a dashboard principal, após confirmação de email.

Gestão de Sessão e Persistência:

Configurar o middleware para proteger rotas privadas (ex: /dashboard, /settings).

Garantir a persistência da sessão para que o usuário permaneça logado entre atualizações de página.

Implementar um botão de Logout funcional.

Isolamento de Dados (Multitenancy de Usuário):

O sistema deve ser estruturado de forma que cada usuário acesse apenas seu próprio conteúdo.

# Implementação da Demo

Crie um projeto simples de chatbot com o streamlit que consuma esse serviço do ReasonGuard para ser utilizado como exemplo

# Requisitos da entrega

Escreva o código em ingles

A interface precisa estar em português do Brasil

O código precisa seguir as boas práticas de desenvolvimento

Utilize uma arquitetura modularizada, onde cada funcionalidade deve estar contida de um componente próprio