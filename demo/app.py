"""
ReasonGuard Demo - Chatbot com Auditoria de Raciocínio
Este aplicativo demonstra como integrar o ReasonGuard como middleware
para auditoria de raciocínio de IA.
"""

import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações
API_URL = os.getenv("REASONGUARD_API_URL", "http://localhost:8000")
API_TOKEN = os.getenv("REASONGUARD_API_TOKEN", "demo-token")

# Configuração da página
st.set_page_config(
    page_title="ReasonGuard Demo",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1976d2;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
    }
    .error-box {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f44336;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown('<div class="main-header">🛡️ ReasonGuard Demo</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Plataforma de Auditoria de Raciocínio de IA</div>', unsafe_allow_html=True)

# Inicializar estado da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []

if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []


def call_reasonguard_api(prompt: str, settings: dict) -> dict:
    """Chama a API do ReasonGuard."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }

    payload = {
        "prompt": prompt,
        "model_provider": settings.get("provider", "openai"),
        "enable_cot": settings.get("enable_cot", True),
        "enable_tot": settings.get("enable_tot", False),
        "enable_got": settings.get("enable_got", False),
        "enable_consistency": settings.get("enable_consistency", False),
        "consistency_runs": settings.get("consistency_runs", 3),
        "temperature": settings.get("temperature", 0.7),
    }

    try:
        response = requests.post(
            f"{API_URL}/proxy/chat",
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# Barra lateral - Configurações
with st.sidebar:
    st.header("⚙️ Configurações")

    st.subheader("Provedor de LLM")
    provider = st.selectbox(
        "Selecione o provedor",
        options=["openai", "anthropic"],
        index=0
    )

    st.subheader("Temperatura")
    temperature = st.slider(
        "Controla a criatividade das respostas",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1
    )

    st.divider()

    st.subheader("🔍 Módulos de Análise")

    enable_cot = st.checkbox(
        "Chain of Thought (CoT)",
        value=True,
        help="Rastreia o processo de raciocínio passo a passo"
    )

    enable_tot = st.checkbox(
        "Tree of Thought (ToT)",
        value=False,
        help="Explora múltiplos caminhos de raciocínio"
    )

    enable_got = st.checkbox(
        "Graph of Thought (GoT)",
        value=False,
        disabled=not enable_cot,
        help="Valida a lógica do raciocínio (requer CoT)"
    )

    enable_consistency = st.checkbox(
        "Verificação de Consistência",
        value=False,
        help="Executa múltiplas vezes para verificar consistência"
    )

    if enable_consistency:
        consistency_runs = st.slider(
            "Número de execuções",
            min_value=2,
            max_value=10,
            value=3
        )
    else:
        consistency_runs = 3

    st.divider()

    st.subheader("📊 Estatísticas da Sessão")
    st.metric("Mensagens", len(st.session_state.messages))
    st.metric("Análises", len(st.session_state.analysis_history))

    if st.button("🗑️ Limpar Conversa"):
        st.session_state.messages = []
        st.session_state.analysis_history = []
        st.rerun()


# Área principal - Chat
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Chat")

    # Container para mensagens
    chat_container = st.container()

    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])

    # Input do usuário
    user_input = st.chat_input("Digite sua pergunta...")

    if user_input:
        # Adicionar mensagem do usuário
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # Mostrar mensagem do usuário
        st.chat_message("user").write(user_input)

        # Chamar API
        settings = {
            "provider": provider,
            "enable_cot": enable_cot,
            "enable_tot": enable_tot,
            "enable_got": enable_got,
            "enable_consistency": enable_consistency,
            "consistency_runs": consistency_runs,
            "temperature": temperature,
        }

        with st.spinner("Processando com ReasonGuard..."):
            result = call_reasonguard_api(user_input, settings)

        if "error" in result:
            st.error(f"Erro na API: {result['error']}")
            response_text = "Desculpe, ocorreu um erro ao processar sua solicitação."
        else:
            response_text = result.get("response", "Sem resposta")

            # Salvar análise
            analysis = {
                "prompt": user_input,
                "response": response_text,
                "metadata": result.get("metadata", {}),
                "reasoning_trace_id": result.get("reasoning_trace_id"),
                "path_analysis_id": result.get("path_analysis_id"),
                "logic_graph_id": result.get("logic_graph_id"),
                "consistency_check_id": result.get("consistency_check_id"),
            }
            st.session_state.analysis_history.append(analysis)

        # Adicionar resposta
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text
        })

        st.chat_message("assistant").write(response_text)

        st.rerun()

with col2:
    st.subheader("📊 Análise")

    if st.session_state.analysis_history:
        latest = st.session_state.analysis_history[-1]
        metadata = latest.get("metadata", {})

        # Tabs para diferentes análises
        tabs = st.tabs(["CoT", "ToT", "GoT", "Consistência"])

        with tabs[0]:
            if "cot" in metadata:
                cot_data = metadata["cot"]
                st.markdown('<div class="info-box">', unsafe_allow_html=True)
                st.write("**Chain of Thought**")
                st.write(f"📝 Passos de raciocínio: {cot_data.get('steps_count', 0)}")
                st.write(f"🔐 Hash de integridade: `{cot_data.get('integrity_hash', 'N/A')[:16]}...`")
                st.markdown('</div>', unsafe_allow_html=True)

                if latest.get("reasoning_trace_id"):
                    st.caption(f"ID: {latest['reasoning_trace_id']}")
            else:
                st.info("CoT não habilitado para esta consulta")

        with tabs[1]:
            if "tot" in metadata:
                tot_data = metadata["tot"]
                st.markdown('<div class="info-box">', unsafe_allow_html=True)
                st.write("**Tree of Thought**")
                st.write(f"🌳 Nós explorados: {tot_data.get('nodes_explored', 0)}")
                st.write(f"✂️ Caminhos podados: {tot_data.get('paths_pruned', 0)}")

                if tot_data.get("selected_path"):
                    st.success(f"Melhor caminho: {tot_data['selected_path'].get('selected_approach', 'N/A')[:100]}")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("ToT não habilitado para esta consulta")

        with tabs[2]:
            if "got" in metadata:
                got_data = metadata["got"]
                validity = got_data.get("validity_score", 0)

                if validity >= 0.7:
                    box_class = "success-box"
                elif validity >= 0.4:
                    box_class = "warning-box"
                else:
                    box_class = "error-box"

                st.markdown(f'<div class="{box_class}">', unsafe_allow_html=True)
                st.write("**Graph of Thought**")
                st.write(f"📊 Score de validade: {validity * 100:.1f}%")

                issues = []
                if got_data.get("has_contradictions"):
                    issues.append("⚠️ Contradições detectadas")
                if got_data.get("has_logic_gaps"):
                    issues.append("⚠️ Lacunas lógicas")
                if got_data.get("has_hidden_premises"):
                    issues.append("⚠️ Premissas ocultas")
                if got_data.get("has_circularity"):
                    issues.append("⚠️ Raciocínio circular")

                if issues:
                    for issue in issues:
                        st.write(issue)
                else:
                    st.write("✅ Nenhum problema lógico detectado")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("GoT não habilitado para esta consulta")

        with tabs[3]:
            if "consistency" in metadata:
                cons_data = metadata["consistency"]
                convergence = cons_data.get("convergence_rate", 0)
                confidence = cons_data.get("confidence_score", 0)

                if confidence >= 0.8:
                    box_class = "success-box"
                elif confidence >= 0.5:
                    box_class = "warning-box"
                else:
                    box_class = "error-box"

                st.markdown(f'<div class="{box_class}">', unsafe_allow_html=True)
                st.write("**Verificação de Consistência**")
                st.write(f"🔄 Execuções: {cons_data.get('total_runs', 0)}")
                st.write(f"📈 Taxa de convergência: {convergence * 100:.1f}%")
                st.write(f"🎯 Score de confiança: {confidence * 100:.1f}%")

                if confidence >= 0.8:
                    st.write("✅ Resultados altamente confiáveis")
                elif confidence >= 0.5:
                    st.write("⚠️ Revisar pontos divergentes")
                else:
                    st.write("❌ Resultados podem não ser confiáveis")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Verificação de consistência não habilitada")

    else:
        st.info("Faça uma pergunta para ver a análise de raciocínio")


# Rodapé
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🛡️ <strong>ReasonGuard</strong> - Plataforma de Auditoria de Raciocínio de IA</p>
    <p>Esta é uma demonstração do sistema de middleware para auditoria de decisões de IA.</p>
</div>
""", unsafe_allow_html=True)
