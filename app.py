import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. Configuração Otimizada para Mobile ---
st.set_page_config(
    page_title="Danki Francês Pro",
    page_icon="🇫🇷",
    layout="centered",  # 'centered' funciona melhor em celulares que 'wide' para flashcards
    initial_sidebar_state="collapsed" # Começa fechado para não tapar a tela no celular
)

# --- 2. CSS Responsivo (Media Queries) ---
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
        border-radius: 20px;
        padding: 60px 20px; /* Padding padrão Desktop */
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
    }

    /* Brilho no topo */
    .flashcard-container::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
    }

    /* Tipografia Desktop */
    .word-fr {
        font-family: 'JetBrains Mono', monospace;
        font-size: 56px;
        font-weight: 800;
        color: #f3f4f6;
        margin: 20px 0;
    }

    .word-pt {
        font-size: 28px;
        color: #10b981;
        font-weight: 600;
        background: rgba(16, 185, 129, 0.1);
        display: inline-block;
        padding: 10px 20px;
        border-radius: 50px;
        border: 1px solid rgba(16, 185, 129, 0.2);
        animation: slideUp 0.4s ease-out;
    }

    /* --- REGRAS ESPECÍFICAS PARA CELULAR (Telas menores que 600px) --- */
    @media only screen and (max-width: 600px) {
        .flashcard-container {
            padding: 30px 10px; /* Menos espaço em branco */
            margin-bottom: 15px;
        }
        .word-fr {
            font-size: 32px; /* Fonte menor para não quebrar linha */
        }
        .word-pt {
            font-size: 20px;
            padding: 5px 15px;
        }
        /* Ajuste fino para os botões do Streamlit ocuparem mais espaço */
        .stButton button {
            width: 100%;
            padding-top: 10px;
            padding-bottom: 10px;
        }
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .rank-badge {
        font-size: 12px;
        text-transform: uppercase;
        color: #9ca3af;
        margin-bottom: 5px;
    }
    
    /* Remove padding excessivo do topo padrão do Streamlit */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
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

# --- Estado ---
if 'current_card' not in st.session_state:
    st.session_state.current_card = df.sample(1).iloc[0]
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False
if 'history' not in st.session_state:
    st.session_state.history = []
if 'xp' not in st.session_state:
    st.session_state.xp = 0
if 'learned_words' not in st.session_state:
    st.session_state.learned_words = set()

# --- Funções ---
def process_answer(known):
    xp_gain = 10 if known else 2
    st.session_state.xp += xp_gain
    
    result_type = 'Conhecido' if known else 'Estudar'
    if known:
        st.session_state.learned_words.add(st.session_state.current_card['Francês'])
    
    st.session_state.history.append({
        'time': datetime.now().strftime("%H:%M:%S"),
        'xp_total': st.session_state.xp,
        'tipo': result_type
    })
    
    st.session_state.current_card = df.sample(1).iloc[0]
    st.session_state.show_answer = False

# --- Sidebar ---
with st.sidebar:
    st.header("👤 Perfil")
    level = int(st.session_state.xp / 100) + 1
    progress_to_next = (st.session_state.xp % 100) / 100.0
    
    c1, c2 = st.columns(2)
    c1.metric("Nível", level)
    c2.metric("XP", st.session_state.xp)
    st.progress(progress_to_next)
    st.divider()
    difficulty = st.slider("Rank Máximo", 100, 1000, 1000, 100)

# --- Área Principal ---
tab_treino, tab_stats, tab_banco = st.tabs(["🔥 Treino", "📈 Stats", "📚 Lista"])

# === TAB 1: FLASHCARD (Responsivo) ===
with tab_treino:
    card = st.session_state.current_card
    
    # Cartão HTML
    html_card = f"""
    <div class="flashcard-container">
        <div class="rank-badge">Rank #{card['Rank']}</div>
        <div class="word-fr">{card['Francês']}</div>
    """
    if st.session_state.show_answer:
        html_card += f'<div class="word-pt">{card["Português"]}</div>'
    else:
        html_card += '<div style="margin-top:20px; opacity: 0.5; color: #6b7280; font-size: 14px;">(Toque para revelar)</div>'
    
    html_card += "</div>"
    st.markdown(html_card, unsafe_allow_html=True)
    
    # --- 3. Botões Responsivos ---
    # Removemos as colunas vazias ([1,2,2,1]) que quebram o mobile.
    # Usamos apenas 2 colunas diretas ou 1 coluna cheia.
    
    if not st.session_state.show_answer:
        # Botão único grande para revelar
        if st.button("👁️ REVELAR RESPOSTA", type="primary", use_container_width=True):
            st.session_state.show_answer = True
            st.rerun()
    else:
        # Dois botões lado a lado (50% cada)
        col_no, col_yes = st.columns(2)
        
        with col_no:
            if st.button("❌ Não sei", use_container_width=True):
                process_answer(known=False)
                st.rerun()
        
        with col_yes:
            if st.button("✅ Já sei!", type="primary", use_container_width=True):
                process_answer(known=True)
                st.rerun()

# === TAB 2: STATS ===
with tab_stats:
    st.subheader("Desempenho")
    if len(st.session_state.history) > 0:
        hist_df = pd.DataFrame(st.session_state.history)
        hist_df['index'] = range(1, len(hist_df) + 1)
        
        # Gráfico simplificado para mobile (remove titulos grandes)
        fig_evolucao = px.area(
            hist_df, x='index', y='xp_total', 
            title="Evolução XP",
            color_discrete_sequence=['#8b5cf6']
        )
        fig_evolucao.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font_color="white",
            margin=dict(l=20, r=20, t=40, b=20), # Margens menores
            height=300 # Altura fixa menor para caber na tela
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)
        
        c1, c2 = st.columns(2)
        c1.metric("Revistos", len(hist_df))
        accuracy = (len(hist_df[hist_df['tipo'] == 'Conhecido']) / len(hist_df)) * 100
        c2.metric("Precisão", f"{accuracy:.0f}%")
    else:
        st.info("Comece a treinar!")

# === TAB 3: BANCO ===
with tab_banco:
    st.dataframe(df, use_container_width=True, hide_index=True)
