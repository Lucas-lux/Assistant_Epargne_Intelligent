import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Import des modules personnalisés
from data_generator import DataGenerator
from analysis_engine import AnalysisEngine
from visualization import VisualizationEngine
from advanced_features import integrate_advanced_features

# Configuration de la page
st.set_page_config(
    page_title="💰 Assistant d'Épargne Intelligent",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour le design responsive
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #4ECDC4 0%, #45B7D1 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #4ECDC4;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2E86AB;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1rem;
        border-radius: 0.375rem;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1rem;
        border-radius: 0.375rem;
    }
    
    .alert-info {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1rem;
        border-radius: 0.375rem;
    }
    
    @media (max-width: 640px) {
        .main-header {
            padding: 1rem;
        }
        .metric-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def main():
    # En-tête principal
    st.markdown("""
    <div class="main-header">
        <h1>💰 Assistant d'Épargne Intelligent</h1>
        <p>Analysez vos finances, prédisez vos dépenses et découvrez des opportunités d'économies</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar pour la navigation et les contrôles
    with st.sidebar:
        st.header("🎛️ Configuration")
        
        # Option pour générer de nouvelles données
        if st.button("🔄 Générer Nouvelles Données", type="primary"):
            generate_new_data()
            st.rerun()
        
        # Filtre de période amélioré
        st.subheader("📅 Période d'Analyse")
        
        # Type de filtre
        filter_type = st.radio(
            "Type de filtre",
            ["Période prédéfinie", "Dates personnalisées"],
            index=0,
            horizontal=True
        )
        
        if filter_type == "Période prédéfinie":
            period_options = {
                "Toute la période": "all",
                "Mois en cours": "current_month",
                "Mois dernier": "last_month", 
                "3 derniers mois": "last_3months",
                "6 derniers mois": "last_6months",
                "Année en cours": "current_year",
                "Année dernière": "last_year",
                "12 derniers mois": "last_12months"
            }
            selected_period = st.selectbox(
                "Choisissez la période",
                options=list(period_options.keys()),
                index=0
            )
            period_filter = period_options[selected_period]
            date_range = None
        else:
            # Sélection de dates personnalisées
            st.write("Sélectionnez la période d'analyse :")
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Date de début",
                    value=datetime.now() - timedelta(days=90),
                    min_value=datetime(2020, 1, 1),
                    max_value=datetime.now()
                )
            with col2:
                end_date = st.date_input(
                    "Date de fin",
                    value=datetime.now(),
                    min_value=datetime(2020, 1, 1),
                    max_value=datetime.now()
                )
            
            # Validation des dates
            if start_date > end_date:
                st.error("⚠️ La date de début doit être antérieure à la date de fin!")
                period_filter = "all"
                date_range = None
            else:
                period_filter = "custom"
                date_range = (start_date, end_date)
                
                # Affichage de la période sélectionnée
                duration = (end_date - start_date).days
                st.info(f"📊 Période sélectionnée: {duration + 1} jours ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})")
        
        # Objectif d'économies
        st.subheader("🎯 Objectifs")
        savings_target = st.number_input(
            "Objectif d'économies mensuel (€)",
            min_value=0,
            max_value=2000,
            value=300,
            step=50
        )
    
    # Chargement des données
    df = load_or_generate_data()
    
    # Affichage des statistiques de la période sélectionnée dans la sidebar
    if df is not None and not df.empty:
        analyzer_temp = AnalysisEngine(df)
        if period_filter == 'custom' and date_range:
            filtered_df = analyzer_temp._apply_period_filter(df, period_filter, date_range)
            st.sidebar.markdown("---")
            st.sidebar.markdown("📊 **Statistiques de la période**")
            st.sidebar.write(f"• Transactions: {len(filtered_df)}")
            st.sidebar.write(f"• Dépenses: {len(filtered_df[filtered_df['montant'] < 0])}")
            st.sidebar.write(f"• Revenus: {len(filtered_df[filtered_df['montant'] > 0])}")
        elif period_filter != 'all':
            filtered_df = analyzer_temp._apply_period_filter(df, period_filter, date_range)
            st.sidebar.markdown("---")
            st.sidebar.markdown("📊 **Statistiques de la période**")
            st.sidebar.write(f"• Transactions: {len(filtered_df)}")
            st.sidebar.write(f"• Dépenses: {len(filtered_df[filtered_df['montant'] < 0])}")
            st.sidebar.write(f"• Revenus: {len(filtered_df[filtered_df['montant'] > 0])}")
    
    if df is not None and not df.empty:
        # Création des moteurs d'analyse et de visualisation
        analyzer = AnalysisEngine(df)
        visualizer = VisualizationEngine()
        
        # Navigation par onglets
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Vue d'Ensemble", 
            "📈 Analyse Détaillée", 
            "🔮 Prédictions", 
            "💡 Opportunités d'Économies",
            "🏥 Santé Financière",
            "🚀 Fonctionnalités Avancées"
        ])
        
        with tab1:
            display_overview(analyzer, visualizer, period_filter, date_range)
        
        with tab2:
            display_detailed_analysis(analyzer, visualizer, period_filter, date_range)
        
        with tab3:
            display_predictions(analyzer, visualizer, period_filter, date_range)
        
        with tab4:
            display_savings_opportunities(analyzer, visualizer, savings_target, period_filter, date_range)
        
        with tab5:
            display_financial_health(analyzer, visualizer, period_filter, date_range)
        
        with tab6:
            integrate_advanced_features(analyzer, visualizer)
    
    else:
        st.error("❌ Impossible de charger les données. Veuillez générer de nouvelles données.")

@st.cache_data
def load_or_generate_data():
    """Charge les données existantes ou en génère de nouvelles"""
    filename = 'releve_bancaire_fictif.csv'
    
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename)
            if 'categorie' not in df.columns:
                # Retraitement nécessaire
                generator = DataGenerator()
                df = generator.process_data(df)
            else:
                df['date'] = pd.to_datetime(df['date'])
            return df
        except Exception as e:
            st.warning(f"Erreur lors du chargement: {e}")
            return generate_new_data()
    else:
        return generate_new_data()

def generate_new_data():
    """Génère un nouveau jeu de données"""
    with st.spinner("🔄 Génération de nouvelles données..."):
        generator = DataGenerator()
        df = generator.generate_transactions(nb_transactions=600)
        df = generator.process_data(df)
        generator.save_to_csv(df)
        st.success("✅ Nouvelles données générées avec succès!")
        return df

def display_overview(analyzer, visualizer, period_filter, date_range):
    """Affiche la vue d'ensemble"""
    st.header("📊 Vue d'Ensemble Financière")
    
    # Affichage de la période analysée
    if period_filter == 'custom' and date_range:
        start_date, end_date = date_range
        st.info(f"📊 Analyse pour la période : {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
    elif period_filter != 'all':
        period_names = {
            'current_month': 'Mois en cours',
            'last_month': 'Mois dernier',
            'last_3months': '3 derniers mois',
            'last_6months': '6 derniers mois',
            'current_year': 'Année en cours',
            'last_year': 'Année dernière',
            'last_12months': '12 derniers mois'
        }
        st.info(f"📊 Analyse pour : {period_names.get(period_filter, 'Période sélectionnée')}")
    
    # Métriques principales
    monthly_summary = analyzer.get_monthly_summary()
    category_analysis = analyzer.get_category_analysis(period_filter, date_range)
    
    if not monthly_summary.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_income = monthly_summary['revenus'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Revenus Moyens Mensuels</div>
                <div class="metric-value">{avg_income:.0f}€</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_expenses = monthly_summary['depenses'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Dépenses Moyennes Mensuelles</div>
                <div class="metric-value">{avg_expenses:.0f}€</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_balance = monthly_summary['solde'].mean()
            color = "#28a745" if avg_balance >= 0 else "#dc3545"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Solde Moyen Mensuel</div>
                <div class="metric-value" style="color: {color}">{avg_balance:.0f}€</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            nb_transactions = len(analyzer.df)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Transactions</div>
                <div class="metric-value">{nb_transactions}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Graphiques principaux
    col1, col2 = st.columns(2)
    
    with col1:
        if not category_analysis.empty:
            pie_chart = visualizer.create_expenses_pie_chart(category_analysis)
            st.plotly_chart(pie_chart, use_container_width=True)
    
    with col2:
        if not monthly_summary.empty:
            trends_chart = visualizer.create_monthly_trends(monthly_summary)
            st.plotly_chart(trends_chart, use_container_width=True)

def display_detailed_analysis(analyzer, visualizer, period_filter, date_range):
    """Affiche l'analyse détaillée"""
    st.header("📈 Analyse Détaillée des Dépenses")
    
    # Analyse par catégorie
    category_analysis = analyzer.get_category_analysis(period_filter, date_range)
    
    if not category_analysis.empty:
        st.subheader("💳 Analyse par Catégorie")
        
        # Tableau détaillé
        st.dataframe(
            category_analysis.style.format({
                'total_depense': '{:.2f}€',
                'moyenne': '{:.2f}€',
                'ecart_type': '{:.2f}€',
                'pourcentage': '{:.1f}%'
            }),
            use_container_width=True
        )
        
        # Tendances des dépenses
        trends = analyzer.get_spending_trends()
        
        if not trends['monthly_by_category'].empty:
            st.subheader("📊 Évolution des Principales Catégories")
            evolution_chart = visualizer.create_category_evolution(
                trends['monthly_by_category'], 
                top_n=5
            )
            st.plotly_chart(evolution_chart, use_container_width=True)
        
        # Heatmap des habitudes de dépenses
        st.subheader("🗓️ Habitudes de Dépenses par Jour")
        heatmap = visualizer.create_weekly_spending_heatmap(analyzer.df)
        st.plotly_chart(heatmap, use_container_width=True)

def display_predictions(analyzer, visualizer, period_filter, date_range):
    """Affiche les prédictions"""
    st.header("🔮 Prédictions des Dépenses Futures")
    
    # Note sur la prédiction
    if period_filter != 'all':
        st.info("🔍 Les prédictions sont basées sur l'ensemble des données historiques pour plus de précision.")
    
    prediction_result = analyzer.predict_future_spending(periods=4)
    
    if prediction_result['success']:
        # Informations sur la prédiction
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="alert-info">
                <strong>Moyenne Actuelle:</strong> {prediction_result['current_avg']:.2f}€/semaine
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            trend_color = "#28a745" if prediction_result['trend'] == 'décroissante' else "#ffc107"
            st.markdown(f"""
            <div class="alert-info">
                <strong>Tendance:</strong> <span style="color: {trend_color}">
                {prediction_result['trend'].capitalize()}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="alert-info">
                <strong>Confiance:</strong> {prediction_result['confidence'].capitalize()}
            </div>
            """, unsafe_allow_html=True)
        
        # Graphique de prédiction
        trends = analyzer.get_spending_trends()
        historical_weekly = trends['weekly'].values[-12:]  # 12 dernières semaines
        
        prediction_chart = visualizer.create_prediction_chart(
            historical_weekly, 
            prediction_result['predictions']
        )
        st.plotly_chart(prediction_chart, use_container_width=True)
        
        # Prédictions détaillées
        st.subheader("📋 Prédictions Détaillées")
        predictions_df = pd.DataFrame({
            'Semaine': [f"Semaine +{i+1}" for i in range(len(prediction_result['predictions']))],
            'Dépenses Prédites (€)': [f"{pred:.2f}" for pred in prediction_result['predictions']]
        })
        st.dataframe(predictions_df, use_container_width=True)
        
    else:
        st.warning(f"⚠️ {prediction_result['message']}")

def display_savings_opportunities(analyzer, visualizer, savings_target, period_filter, date_range):
    """Affiche les opportunités d'économies"""
    st.header("💡 Opportunités d'Économies")
    
    # Utiliser le filtre pour l'analyse des économies
    filtered_analyzer = AnalysisEngine(analyzer._apply_period_filter(analyzer.df, period_filter, date_range))
    opportunities = filtered_analyzer.identify_savings_opportunities()
    
    # Dépenses compressibles
    st.subheader("🎯 Dépenses Compressibles")
    compressible = opportunities['depenses_compressibles']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="alert-warning">
            <strong>Total Dépenses Compressibles:</strong> {compressible['total']:.2f}€<br>
            <strong>Économie potentielle (20%):</strong> {compressible['economie_potentielle_20pct']:.2f}€<br>
            <strong>Économie potentielle (30%):</strong> {compressible['economie_potentielle_30pct']:.2f}€
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Détail par catégorie compressible
        compressible_df = pd.DataFrame.from_dict(
            compressible['detail'], 
            orient='index', 
            columns=['Montant Total']
        )
        st.dataframe(
            compressible_df.style.format({'Montant Total': '{:.2f}€'}),
            use_container_width=True
        )
    
    # Abonnements
    st.subheader("📱 Analyse des Abonnements")
    subscriptions = opportunities['abonnements']
    
    if subscriptions['detail']:
        st.markdown(f"""
        <div class="alert-info">
            <strong>Total Abonnements Détectés:</strong> {subscriptions['total_mensuel']:.2f}€/mois
        </div>
        """, unsafe_allow_html=True)
        
        subs_df = pd.DataFrame.from_dict(subscriptions['detail'], orient='index')
        subs_df.columns = ['Occurrences', 'Montant Moyen']
        st.dataframe(
            subs_df.style.format({
                'Montant Moyen': '{:.2f}€',
                'Occurrences': '{:.0f}'
            }),
            use_container_width=True
        )
    else:
        st.info("Aucun abonnement récurrent détecté.")
    
    # Habitudes week-end vs semaine
    st.subheader("📅 Répartition Semaine/Week-end")
    repartition = opportunities['repartition_semaine']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Dépenses Semaine", f"{repartition['semaine']:.2f}€")
    
    with col2:
        st.metric("Dépenses Week-end", f"{repartition['weekend']:.2f}€")
    
    with col3:
        st.metric("% Week-end", f"{repartition['ratio_weekend']:.1f}%")
    
    # Jauge d'économies vs objectif
    st.subheader("🎯 Progression vers l'Objectif d'Économies")
    current_savings = compressible['economie_potentielle_20pct']
    
    gauge = visualizer.create_savings_gauge(current_savings, savings_target)
    st.plotly_chart(gauge, use_container_width=True)

def display_financial_health(analyzer, visualizer, period_filter, date_range):
    """Affiche la santé financière"""
    st.header("🏥 Santé Financière")
    
    # Utiliser le filtre pour l'analyse de santé financière
    if period_filter != 'all':
        filtered_analyzer = AnalysisEngine(analyzer._apply_period_filter(analyzer.df, period_filter, date_range))
        health_score = filtered_analyzer.get_financial_health_score()
        st.info("🔍 Score calculé sur la période sélectionnée")
    else:
        health_score = analyzer.get_financial_health_score()
    
    # Score principal
    col1, col2 = st.columns([1, 2])
    
    with col1:
        score_color = "#28a745" if health_score['score'] >= 70 else "#ffc107" if health_score['score'] >= 40 else "#dc3545"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: {score_color}; 
                    color: white; border-radius: 15px; margin-bottom: 1rem;">
            <h1 style="margin: 0; font-size: 3rem;">{health_score['score']}/100</h1>
            <h3 style="margin: 0;">{health_score['niveau']}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        radar_chart = visualizer.create_financial_health_radar(health_score)
        st.plotly_chart(radar_chart, use_container_width=True)
    
    # Détails du score
    st.subheader("📋 Détails de l'Évaluation")
    
    details = health_score['details']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Solde Moyen Mensuel</div>
            <div class="metric-value">{details['solde_moyen']:.2f}€</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Mois avec Solde Positif</div>
            <div class="metric-value">{details['mois_positifs']}/{details['total_mois']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Stabilité Financière</div>
            <div class="metric-value">{details['stabilite']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Taux de Réussite</div>
            <div class="metric-value">{details['ratio_positif']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recommandations
    st.subheader("💡 Recommandations")
    
    if health_score['score'] >= 80:
        st.success("""
        🎉 **Excellente santé financière !**
        - Continuez sur cette voie
        - Envisagez d'augmenter vos investissements
        - Diversifiez vos sources de revenus
        """)
    elif health_score['score'] >= 60:
        st.info("""
        👍 **Bonne santé financière**
        - Travaillez sur la régularité de vos économies
        - Réduisez les dépenses variables
        - Constituez un fonds d'urgence
        """)
    elif health_score['score'] >= 40:
        st.warning("""
        ⚠️ **Santé financière moyenne**
        - Analysez vos dépenses non essentielles
        - Mettez en place un budget strict
        - Surveillez vos abonnements
        """)
    else:
        st.error("""
        🚨 **Santé financière fragile**
        - Réduisez immédiatement les dépenses non essentielles
        - Cherchez des sources de revenus supplémentaires
        - Consultez un conseiller financier
        """)

if __name__ == "__main__":
    main() 