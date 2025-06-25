import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

def apply_custom_css():
    """Applique le CSS personnalisé pour améliorer l'interface"""
    
    st.markdown("""
    <style>
        /* Variables CSS pour les thèmes */
        :root {
            --primary-color: #4ECDC4;
            --secondary-color: #45B7D1;
            --accent-color: #FF6B6B;
            --success-color: #96CEB4;
            --warning-color: #FECA57;
            --error-color: #FF6B6B;
            --text-color: #2E86AB;
            --bg-color: #F8F9FA;
            --card-bg: #FFFFFF;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            --border-radius: 12px;
        }
        
        /* Animation keyframes */
        @keyframes slideInFromLeft {
            0% {
                transform: translateX(-100%);
                opacity: 0;
            }
            100% {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        @keyframes shimmer {
            0% { background-position: -200px 0; }
            100% { background-position: calc(200px + 100%) 0; }
        }
        
        /* Classes d'animation */
        .animate-slide-in {
            animation: slideInFromLeft 0.6s ease-out;
        }
        
        .animate-fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        .animate-pulse {
            animation: pulse 2s infinite;
        }
        
        .loading-shimmer {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200px 100%;
            animation: shimmer 1.5s infinite;
        }
        
        /* Améliorations de l'interface */
        .main-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            padding: 2rem;
            border-radius: var(--border-radius);
            text-align: center;
            color: white;
            margin-bottom: 2rem;
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
        }
        
        .main-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: repeating-linear-gradient(
                45deg,
                rgba(255,255,255,0.1) 0px,
                rgba(255,255,255,0.1) 1px,
                transparent 1px,
                transparent 10px
            );
            animation: shimmer 3s linear infinite;
        }
        
        .metric-card {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            border-left: 4px solid var(--primary-color);
            margin-bottom: 1rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(78, 205, 196, 0.2), transparent);
            transition: left 0.5s;
        }
        
        .metric-card:hover::before {
            left: 100%;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: var(--text-color);
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .metric-label {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .enhanced-card {
            background: var(--card-bg);
            border-radius: var(--border-radius);
            padding: 1.5rem;
            box-shadow: var(--shadow);
            margin-bottom: 1rem;
            border: 1px solid rgba(78, 205, 196, 0.2);
            transition: all 0.3s ease;
        }
        
        .enhanced-card:hover {
            border-color: var(--primary-color);
            transform: translateY(-2px);
        }
        
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-excellent {
            background-color: rgba(150, 206, 180, 0.2);
            color: #2D7D56;
            border: 1px solid #96CEB4;
        }
        
        .status-good {
            background-color: rgba(78, 205, 196, 0.2);
            color: #2B8A7A;
            border: 1px solid #4ECDC4;
        }
        
        .status-warning {
            background-color: rgba(254, 202, 87, 0.2);
            color: #B8860B;
            border: 1px solid #FECA57;
        }
        
        .status-critical {
            background-color: rgba(255, 107, 107, 0.2);
            color: #CC2936;
            border: 1px solid #FF6B6B;
        }
        
        .progress-container {
            background-color: #E9ECEF;
            border-radius: 10px;
            overflow: hidden;
            height: 8px;
            margin: 1rem 0;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            border-radius: 10px;
            transition: width 1s ease-in-out;
            position: relative;
        }
        
        .progress-bar::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            bottom: 0;
            right: 0;
            background-image: linear-gradient(
                -45deg,
                rgba(255, 255, 255, .2) 25%,
                transparent 25%,
                transparent 50%,
                rgba(255, 255, 255, .2) 50%,
                rgba(255, 255, 255, .2) 75%,
                transparent 75%,
                transparent
            );
            background-size: 50px 50px;
            animation: shimmer 2s linear infinite;
        }
        
        .info-tooltip {
            position: relative;
            cursor: help;
        }
        
        .info-tooltip:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            width: 200px;
            background-color: #333;
            color: white;
            text-align: center;
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
            z-index: 1;
        }
        
        .floating-action {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 60px;
            height: 60px;
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            border-radius: 50%;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            cursor: pointer;
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .floating-action:hover {
            transform: scale(1.1) rotate(180deg);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        }
        
        /* Responsive Design Amélioré */
        @media (max-width: 768px) {
            .main-header {
                padding: 1rem;
                margin-bottom: 1rem;
            }
            
            .metric-card {
                padding: 1rem;
                margin-bottom: 0.5rem;
            }
            
            .metric-value {
                font-size: 1.5rem;
            }
            
            .floating-action {
                bottom: 1rem;
                right: 1rem;
                width: 50px;
                height: 50px;
                font-size: 20px;
            }
        }
        
        @media (max-width: 480px) {
            .main-header h1 {
                font-size: 1.5rem;
            }
            
            .metric-card {
                padding: 0.75rem;
            }
            
            .metric-value {
                font-size: 1.25rem;
            }
        }
        
        /* Dark Mode Support */
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-color: #1E1E1E;
                --card-bg: #2D2D2D;
                --text-color: #FFFFFF;
            }
            
            .metric-card {
                background: var(--card-bg);
                color: var(--text-color);
            }
            
            .enhanced-card {
                background: var(--card-bg);
                color: var(--text-color);
            }
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--secondary-color);
        }
        
        /* Loading Animations */
        .loading-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
        }
        
        .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Success/Error Messages Enhanced */
        .alert-enhanced {
            padding: 1rem 1.5rem;
            border-radius: var(--border-radius);
            margin: 1rem 0;
            position: relative;
            overflow: hidden;
        }
        
        .alert-success {
            background: linear-gradient(135deg, rgba(150, 206, 180, 0.1), rgba(150, 206, 180, 0.2));
            border-left: 4px solid var(--success-color);
            color: #2D7D56;
        }
        
        .alert-warning {
            background: linear-gradient(135deg, rgba(254, 202, 87, 0.1), rgba(254, 202, 87, 0.2));
            border-left: 4px solid var(--warning-color);
            color: #B8860B;
        }
        
        .alert-error {
            background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(255, 107, 107, 0.2));
            border-left: 4px solid var(--error-color);
            color: #CC2936;
        }
        
        .alert-info {
            background: linear-gradient(135deg, rgba(69, 183, 209, 0.1), rgba(69, 183, 209, 0.2));
            border-left: 4px solid var(--secondary-color);
            color: #1B5E75;
        }
    </style>
    """, unsafe_allow_html=True)

def create_enhanced_metric_card(title, value, delta=None, delta_color="normal", help_text=None):
    """Crée une carte de métrique améliorée avec animations"""
    
    delta_html = ""
    if delta is not None:
        delta_class = "success" if delta_color == "normal" else "error"
        delta_symbol = "▲" if delta >= 0 else "▼"
        delta_html = f"""
        <div class="metric-delta {delta_class}">
            {delta_symbol} {abs(delta):.1f}%
        </div>
        """
    
    help_html = ""
    if help_text:
        help_html = f'<span class="info-tooltip" data-tooltip="{help_text}">ℹ️</span>'
    
    card_html = f"""
    <div class="metric-card animate-fade-in">
        <div class="metric-label">{title} {help_html}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    
    return card_html

def create_status_badge(status, text):
    """Crée un badge de statut coloré"""
    status_class = f"status-{status.lower()}"
    return f'<span class="status-badge {status_class}">{text}</span>'

def create_progress_bar(percentage, color="primary"):
    """Crée une barre de progression animée"""
    return f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {percentage}%"></div>
    </div>
    <div style="text-align: center; margin-top: 0.5rem;">
        <small>{percentage:.1f}% complété</small>
    </div>
    """

def create_enhanced_alert(type, title, message, dismissible=False):
    """Crée une alerte améliorée avec style personnalisé"""
    
    icons = {
        "success": "✅",
        "warning": "⚠️", 
        "error": "❌",
        "info": "ℹ️"
    }
    
    icon = icons.get(type, "ℹ️")
    
    dismiss_btn = ""
    if dismissible:
        dismiss_btn = '<button style="float: right; background: none; border: none; font-size: 1.2rem; cursor: pointer;">×</button>'
    
    return f"""
    <div class="alert-enhanced alert-{type} animate-fade-in">
        {dismiss_btn}
        <strong>{icon} {title}</strong><br>
        {message}
    </div>
    """

def create_loading_spinner(text="Chargement..."):
    """Crée un spinner de chargement"""
    return f"""
    <div class="loading-container">
        <div style="text-align: center;">
            <div class="loading-spinner"></div>
            <p style="margin-top: 1rem; color: #666;">{text}</p>
        </div>
    </div>
    """

def apply_theme_selector():
    """Ajoute un sélecteur de thème dans la sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.subheader("🎨 Personnalisation")
        
        theme = st.selectbox(
            "Choisir un thème",
            ["Défaut", "Sombre", "Bleu", "Vert", "Orange"]
        )
        
        if theme == "Sombre":
            st.markdown("""
            <style>
                .stApp {
                    background-color: #1E1E1E;
                    color: white;
                }
                .metric-card {
                    background-color: #2D2D2D !important;
                    color: white !important;
                }
            </style>
            """, unsafe_allow_html=True)
        elif theme == "Bleu":
            st.markdown("""
            <style>
                :root {
                    --primary-color: #007BFF !important;
                    --secondary-color: #6C757D !important;
                }
            </style>
            """, unsafe_allow_html=True)
        elif theme == "Vert":
            st.markdown("""
            <style>
                :root {
                    --primary-color: #28A745 !important;
                    --secondary-color: #20C997 !important;
                }
            </style>
            """, unsafe_allow_html=True)
        elif theme == "Orange":
            st.markdown("""
            <style>
                :root {
                    --primary-color: #FD7E14 !important;
                    --secondary-color: #FF6B6B !important;
                }
            </style>
            """, unsafe_allow_html=True)
        
        # Options d'animation
        animations_enabled = st.checkbox("Activer les animations", True)
        if not animations_enabled:
            st.markdown("""
            <style>
                * {
                    animation: none !important;
                    transition: none !important;
                }
            </style>
            """, unsafe_allow_html=True)
        
        # Compact mode
        compact_mode = st.checkbox("Mode compact", False)
        if compact_mode:
            st.markdown("""
            <style>
                .metric-card {
                    padding: 0.75rem !important;
                    margin-bottom: 0.5rem !important;
                }
                .main-header {
                    padding: 1rem !important;
                }
            </style>
            """, unsafe_allow_html=True)

def add_floating_action_button():
    """Ajoute un bouton d'action flottant"""
    st.markdown("""
    <div class="floating-action" onclick="window.scrollTo(0,0)" title="Retour en haut">
        ↑
    </div>
    """, unsafe_allow_html=True)

def create_dashboard_header(title, subtitle, show_time=True):
    """Crée un en-tête de dashboard amélioré"""
    
    time_html = ""
    if show_time:
        current_time = datetime.now().strftime("%d/%m/%Y à %H:%M")
        time_html = f"<p style='margin: 0; opacity: 0.8;'>Dernière mise à jour: {current_time}</p>"
    
    return f"""
    <div class="main-header animate-slide-in">
        <h1 style="margin: 0; font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">{title}</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">{subtitle}</p>
        {time_html}
    </div>
    """ 