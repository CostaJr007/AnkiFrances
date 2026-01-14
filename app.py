import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- Configuração da Página e Tema ---
st.set_page_config(
    page_title="Danki Francês Pro",
    page_icon="🇫🇷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Profissional (Glassmorphism & Neon) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&display=swap');

    /* Reset e Fonte Base */
    .stApp {
        background-color: #0f1116;
        font-family: 'Inter', sans-serif;
    }

    /* Cartão Principal */
    .flashcard-container {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #374151;
        border-radius: 24px;
        padding: 60px 20px;
        text-align: center;
        box-shadow: 0 20px 50px -12px rgba(0, 0, 0, 0.5);
        position: relative;
        overflow: hidden;
        margin-bottom: 30px;
    }

    /* Efeito de brilho no topo do cartão */
    .flashcard-container::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 6px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
    }

    /* Tipografia */
    .word-fr {
        font-family: 'JetBrains Mono', monospace;
        font-size: 56px;
        font-weight: 800;
        color: #f3f4f6;
        text-shadow: 0 0 30px rgba(59, 130, 246, 0.3);
        margin: 20px 0;
    }

    .word-pt {
        font-size: 28px;
        color: #10b981;
        font-weight: 600;
        background: rgba(16, 185, 129, 0.1);
        display: inline-block;
        padding: 8px 24px;
        border-radius: 50px;
        border: 1px solid rgba(16, 185, 129, 0.2);
        animation: slideUp 0.4s ease-out;
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Badges e Infos */
    .rank-badge {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #9ca3af;
        margin-bottom: 10px;
    }

    /* Botões Customizados via CSS hack não são ideais no Streamlit, 
       mas vamos estilizar as métricas */
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)


# --- Carregamento de Dados ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('frances_verbs.csv', sep='\t')
        df.columns = ['Rank', 'Francês', 'Português']
        return df
    except Exception as e:
        st.error(f"Erro ao carregar base de dados: {e}")
        return pd.DataFrame()


df = load_data()
if df.empty: st.stop()

# --- Gerenciamento de Estado (Session State) ---
if 'current_card' not in st.session_state:
    st.session_state.current_card = df.sample(1).iloc[0]
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False
if 'history' not in st.session_state:
    # Formato: {'time': timestamp, 'result': 'acerto'/'erro', 'xp': int}
    st.session_state.history = []
if 'xp' not in st.session_state:
    st.session_state.xp = 0
if 'learned_words' not in st.session_state:
    st.session_state.learned_words = set()


# --- Funções Lógicas ---
def process_answer(known):
    # Lógica de Gamificação
    xp_gain = 10 if known else 2
    st.session_state.xp += xp_gain

    result_type = 'Conhecido' if known else 'Estudar'
    if known:
        st.session_state.learned_words.add(st.session_state.current_card['Francês'])

    # Registra no histórico para o gráfico
    st.session_state.history.append({
        'time': datetime.now().strftime("%H:%M:%S"),
        'xp_total': st.session_state.xp,
        'tipo': result_type
    })

    # Próxima carta
    st.session_state.current_card = df.sample(1).iloc[0]
    st.session_state.show_answer = False


# --- Layout: Sidebar (Perfil do Usuário) ---
with st.sidebar:
    st.header("👤 Perfil do Estudante")

    # Cálculo de Nível
    level = int(st.session_state.xp / 100) + 1
    progress_to_next = (st.session_state.xp % 100) / 100.0

    c1, c2 = st.columns(2)
    c1.metric("Nível", level)
    c2.metric("XP Total", st.session_state.xp)

    st.write(f"Progresso p/ Nível {level + 1}")
    st.progress(progress_to_next)

    st.divider()

    st.subheader("⚙️ Configuração")
    difficulty = st.slider("Filtro de Rank (Top X)", 100, 1000, 1000, 100)
    # Filtra o dataset globalmente para o sorteio, se quiser implementar
    # df_active = df[df['Rank'] <= difficulty]

# --- Layout: Área Principal (Tabs) ---
tab_treino, tab_stats, tab_banco = st.tabs(["🔥 Área de Treino", "📈 Evolução & Stats", "📚 Dicionário"])

# === TAB 1: FLASHCARD ===
with tab_treino:
    col_center, _ = st.columns(
        [1, 0.01])  # Truque para centralizar visualmente se usar 'centered', mas aqui estamos em 'wide'

    card = st.session_state.current_card

    # HTML do Cartão
    html_card = f"""
    <div class="flashcard-container">
        <div class="rank-badge">Palavra #{card['Rank']} • Frequência Alta</div>
        <div class="word-fr">{card['Francês']}</div>
    """
    if st.session_state.show_answer:
        html_card += f'<div class="word-pt">{card["Português"]}</div>'
    else:
        html_card += '<div style="height: 45px; opacity: 0.5; color: #6b7280;">(Pense na tradução...)</div>'

    html_card += "</div>"
    st.markdown(html_card, unsafe_allow_html=True)

    # Controles
    c1, c2, c3, c4 = st.columns([1, 2, 2, 1])

    if not st.session_state.show_answer:
        with c2:
            st.write("")  # Spacer
        with c3:
            if st.button("👁️ REVELAR RESPOSTA", type="primary", use_container_width=True):
                st.session_state.show_answer = True
                st.rerun()
    else:
        # Botões de Feedback
        with c2:
            if st.button("❌ Não sei ainda (+2 XP)", use_container_width=True):
                process_answer(known=False)
                st.rerun()
        with c3:
            if st.button("✅ Já sei! (+10 XP)", type="primary", use_container_width=True):
                process_answer(known=True)
                st.rerun()

# === TAB 2: ESTATÍSTICAS (GRÁFICOS) ===
with tab_stats:
    st.subheader("Seu Desempenho na Sessão Atual")

    if len(st.session_state.history) > 0:
        # Cria DataFrame do Histórico
        hist_df = pd.DataFrame(st.session_state.history)
        hist_df['index'] = range(1, len(hist_df) + 1)

        # 1. Gráfico de Evolução de XP (Área)
        fig_evolucao = px.area(
            hist_df,
            x='index',
            y='xp_total',
            title="Crescimento de XP por Jogada",
            labels={'index': 'Número de Flashcards', 'xp_total': 'XP Acumulado'},
            color_discrete_sequence=['#8b5cf6']
        )
        fig_evolucao.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_evolucao, use_container_width=True)

        # 2. Métricas Lado a Lado
        col_m1, col_m2 = st.columns(2)

        # Gráfico de Pizza (Acertos vs Erros)
        counts = hist_df['tipo'].value_counts().reset_index()
        counts.columns = ['Status', 'Qtd']

        fig_pizza = px.pie(
            counts,
            values='Qtd',
            names='Status',
            title="Precisão da Sessão",
            color='Status',
            color_discrete_map={'Conhecido': '#10b981', 'Estudar': '#ef4444'},
            hole=0.5
        )
        fig_pizza.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")

        with col_m1:
            st.plotly_chart(fig_pizza, use_container_width=True)

        with col_m2:
            st.metric("Total Revisado", len(hist_df))
            st.metric("Palavras Dominadas", len(st.session_state.learned_words))
            accuracy = (len(hist_df[hist_df['tipo'] == 'Conhecido']) / len(hist_df)) * 100
            st.metric("Taxa de Precisão", f"{accuracy:.1f}%")

    else:
        st.info("Comece a estudar na aba 'Área de Treino' para gerar gráficos!")

# === TAB 3: BANCO DE DADOS ===
with tab_banco:
    st.subheader("📚 Todos os Verbos")
    st.dataframe(df, use_container_width=True, hide_index=True)