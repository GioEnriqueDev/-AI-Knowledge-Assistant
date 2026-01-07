"""
VERITAS PRO - STREAMLIT APP
La Faccia del Sistema

Interfaccia utente moderna e interattiva costruita con Streamlit.
"""

import streamlit as st
from ai_core import VeritasAI, VeritasAnalyzer
from datetime import datetime
import time


# Configurazione della pagina
st.set_page_config(
    page_title="Veritas Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizzato per un look premium
st.markdown("""
<style>
    /* Tema principale */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Titolo principale */
    .title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(120deg, #ffffff, #e0e7ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Sottotitolo */
    .subtitle {
        text-align: center;
        color: #e0e7ff;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Card container */
    .card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    /* Messaggi chat */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .ai-message {
        background: rgba(255, 255, 255, 0.95);
        color: #1a202c;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Pulsanti */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Inizializza lo stato della sessione."""
    if 'ai' not in st.session_state:
        st.session_state.ai = VeritasAI()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = VeritasAnalyzer()


def render_header():
    """Renderizza l'header dell'applicazione."""
    st.markdown('<h1 class="title">🧠 VERITAS PRO</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Il Tuo Assistente AI di Nuova Generazione</p>', unsafe_allow_html=True)
    st.markdown("---")


def render_sidebar():
    """Renderizza la sidebar con controlli e statistiche."""
    with st.sidebar:
        st.markdown("## ⚙️ Configurazione")
        
        # Controllo temperatura
        temperature = st.slider(
            "Creatività AI",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="0.0 = Preciso | 1.0 = Creativo"
        )
        st.session_state.ai.set_temperature(temperature)
        
        st.markdown("---")
        
        # Statistiche
        st.markdown("## 📊 Statistiche")
        stats = st.session_state.ai.get_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Messaggi Totali", stats['total_messages'])
            st.metric("Messaggi Utente", stats['user_messages'])
        with col2:
            st.metric("Risposte AI", stats['ai_messages'])
            st.metric("Temperatura", f"{stats['temperature']:.1f}")
        
        st.markdown("---")
        
        # Pulsante reset
        if st.button("🗑️ Cancella Cronologia", use_container_width=True):
            st.session_state.ai.clear_history()
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🎯 Modello")
        st.info(f"**{stats['model']}**")


def render_chat_interface():
    """Renderizza l'interfaccia di chat principale."""
    st.markdown("## 💬 Chat con Veritas")
    
    # Container per i messaggi
    chat_container = st.container()
    
    # Mostra messaggi esistenti
    with chat_container:
        for message in st.session_state.messages:
            if message['role'] == 'user':
                st.markdown(f'<div class="user-message">👤 **Tu:** {message["content"]}</div>', 
                          unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-message">🧠 **Veritas:** {message["content"]}</div>', 
                          unsafe_allow_html=True)
    
    # Input utente
    st.markdown("---")
    user_input = st.text_input(
        "Scrivi il tuo messaggio...",
        key="user_input",
        placeholder="Chiedi qualsiasi cosa a Veritas..."
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        send_button = st.button("📤 Invia", use_container_width=True)
    
    with col2:
        analyze_button = st.button("🔍 Analizza", use_container_width=True)
    
    # Gestione invio messaggio
    if send_button and user_input:
        # Aggiungi messaggio utente
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Ottieni risposta AI
        with st.spinner("🤔 Veritas sta pensando..."):
            time.sleep(0.5)  # Effetto di attesa
            result = st.session_state.ai.analyze(user_input)
        
        # Aggiungi risposta AI
        st.session_state.messages.append({
            'role': 'assistant',
            'content': result['response'],
            'timestamp': result['timestamp']
        })
        
        st.rerun()
    
    # Gestione analisi avanzata
    if analyze_button and user_input:
        st.markdown("### 🔬 Analisi Avanzata")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Sentiment")
            sentiment = st.session_state.analyzer.sentiment_analysis(user_input)
            st.json(sentiment)
        
        with col2:
            st.markdown("#### Keywords")
            keywords = st.session_state.analyzer.extract_keywords(user_input)
            st.write(", ".join(keywords))


def render_analytics_tab():
    """Renderizza il tab delle analytics."""
    st.markdown("## 📈 Analytics & Insights")
    
    col1, col2, col3 = st.columns(3)
    
    stats = st.session_state.ai.get_stats()
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric(
            label="Conversazioni Totali",
            value=stats['total_messages'] // 2,
            delta="+1" if stats['total_messages'] > 0 else "0"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric(
            label="Messaggi Processati",
            value=stats['user_messages'],
            delta=f"+{stats['user_messages']}"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric(
            label="Risposte Generate",
            value=stats['ai_messages'],
            delta=f"+{stats['ai_messages']}"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Cronologia conversazioni
    if st.session_state.messages:
        st.markdown("### 📜 Cronologia Completa")
        for i, msg in enumerate(st.session_state.messages):
            with st.expander(f"Messaggio {i+1} - {msg['role'].upper()}"):
                st.write(f"**Contenuto:** {msg['content']}")
                st.write(f"**Timestamp:** {msg['timestamp']}")


def main():
    """Funzione principale dell'applicazione."""
    # Inizializza stato
    initialize_session_state()
    
    # Renderizza header
    render_header()
    
    # Renderizza sidebar
    render_sidebar()
    
    # Tabs principali
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📈 Analytics", "ℹ️ Info"])
    
    with tab1:
        render_chat_interface()
    
    with tab2:
        render_analytics_tab()
    
    with tab3:
        st.markdown("## ℹ️ Informazioni su Veritas Pro")
        st.markdown("""
        **Veritas Pro** è un assistente AI di nuova generazione che combina:
        
        - 🧠 **AI Core**: Cervello intelligente basato su modelli avanzati
        - 🎨 **UI Moderna**: Interfaccia Streamlit elegante e reattiva
        - 📊 **Analytics**: Statistiche e insights in tempo reale
        - 🔍 **Analisi Avanzate**: Sentiment analysis e keyword extraction
        
        ### 🚀 Caratteristiche
        
        - ✅ Conversazioni naturali e contestuali
        - ✅ Analisi del sentiment in tempo reale
        - ✅ Estrazione automatica di keywords
        - ✅ Cronologia completa delle conversazioni
        - ✅ Controllo della creatività AI
        - ✅ Design premium con glassmorphism
        
        ### 🛠️ Tecnologie
        
        - **Backend**: Python 3.x
        - **Frontend**: Streamlit
        - **AI**: Architettura modulare (pronta per OpenAI/Anthropic)
        
        ---
        
        **Versione:** 1.0.0  
        **Autore:** Veritas Team  
        **Licenza:** MIT
        """)


if __name__ == "__main__":
    main()
