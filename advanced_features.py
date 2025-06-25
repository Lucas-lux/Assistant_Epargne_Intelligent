import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class AdvancedFeatures:
    """Fonctionnalités avancées pour l'assistant d'épargne"""
    
    def __init__(self, analyzer, visualizer):
        self.analyzer = analyzer
        self.visualizer = visualizer
        
    def create_expense_flow_diagram(self):
        """Diagramme de flux des dépenses (Sankey)"""
        st.subheader("🌊 Flux des Dépenses")
        
        # Préparation des données pour le diagramme Sankey
        category_analysis = self.analyzer.get_category_analysis()
        
        if not category_analysis.empty:
            # Préparer les nœuds
            categories = category_analysis.index.tolist()
            
            # Créer les liens (de "Revenus" vers chaque catégorie)
            source = [0] * len(categories)  # Toutes les dépenses viennent des revenus
            target = list(range(1, len(categories) + 1))
            values = category_analysis['total_depense'].tolist()
            
            # Couleurs
            colors = [self.visualizer.category_colors.get(cat, '#DDA0DD') for cat in categories]
            
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=["💰 Revenus"] + categories,
                    color=["#4ECDC4"] + colors
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=values,
                    color=[f"rgba(78, 205, 196, 0.4)"] * len(values)
                )
            )])
            
            fig.update_layout(
                title="Flux des Dépenses par Catégorie",
                font_size=12,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Insights automatiques
            top_category = category_analysis.index[0]
            top_percentage = category_analysis.iloc[0]['pourcentage']
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"💡 **Insight:** {top_category} représente {top_percentage:.1f}% de vos dépenses")
            with col2:
                diversification_score = 100 - (category_analysis['pourcentage'].iloc[0])
                if diversification_score > 70:
                    st.success(f"✅ Bonne diversification ({diversification_score:.0f}/100)")
                else:
                    st.warning(f"⚠️ Concentration élevée ({diversification_score:.0f}/100)")
    
    def create_spending_velocity_chart(self):
        """Graphique de vélocité des dépenses"""
        st.subheader("⚡ Vélocité des Dépenses")
        
        # Calcul de la vélocité (dépenses par jour de la semaine)
        df_depenses = self.analyzer.depenses_df.copy()
        
        # Mapping des jours en français
        day_mapping = {
            'Monday': 'Lundi', 'Tuesday': 'Mardi', 'Wednesday': 'Mercredi',
            'Thursday': 'Jeudi', 'Friday': 'Vendredi', 'Saturday': 'Samedi', 'Sunday': 'Dimanche'
        }
        
        df_depenses['jour_fr'] = df_depenses['jour_semaine'].map(day_mapping)
        
        # Analyse par jour de la semaine
        daily_velocity = df_depenses.groupby('jour_fr').agg({
            'montant': ['count', 'sum', 'mean']
        }).round(2)
        
        daily_velocity.columns = ['nb_transactions', 'total_depense', 'depense_moyenne']
        daily_velocity['total_depense'] = daily_velocity['total_depense'].abs()
        daily_velocity['depense_moyenne'] = daily_velocity['depense_moyenne'].abs()
        
        # Réorganiser les jours
        day_order = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        daily_velocity = daily_velocity.reindex(day_order)
        
        # Créer le graphique
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Nombre de Transactions par Jour', 'Montant Moyen par Transaction'),
            vertical_spacing=0.15
        )
        
        # Graphique 1: Nombre de transactions
        fig.add_trace(go.Bar(
            x=daily_velocity.index,
            y=daily_velocity['nb_transactions'],
            name='Transactions',
            marker_color='#4ECDC4',
            showlegend=False
        ), row=1, col=1)
        
        # Graphique 2: Montant moyen
        fig.add_trace(go.Bar(
            x=daily_velocity.index,
            y=daily_velocity['depense_moyenne'],
            name='Montant Moyen',
            marker_color='#FF6B6B',
            showlegend=False
        ), row=2, col=1)
        
        fig.update_layout(
            title="Analyse de la Vélocité des Dépenses",
            height=500,
            showlegend=False
        )
        
        fig.update_yaxes(title_text="Nb Transactions", row=1, col=1)
        fig.update_yaxes(title_text="Montant (€)", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse des patterns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            peak_day = daily_velocity['nb_transactions'].idxmax()
            peak_count = daily_velocity['nb_transactions'].max()
            st.metric("Jour le + Actif", peak_day, f"{peak_count} transactions")
        
        with col2:
            expensive_day = daily_velocity['depense_moyenne'].idxmax()
            expensive_amount = daily_velocity['depense_moyenne'].max()
            st.metric("Jour le + Cher", expensive_day, f"{expensive_amount:.0f}€/transaction")
        
        with col3:
            weekend_ratio = (daily_velocity.loc[['Samedi', 'Dimanche'], 'total_depense'].sum() / 
                           daily_velocity['total_depense'].sum() * 100)
            st.metric("Dépenses Week-end", f"{weekend_ratio:.1f}%")
    
    def create_financial_weather(self):
        """Météo financière"""
        st.subheader("🌤️ Météo Financière")
        
        # Calcul des indicateurs météo
        monthly_summary = self.analyzer.get_monthly_summary()
        
        if not monthly_summary.empty:
            last_month = monthly_summary.iloc[-1]
            
            # Détermination de la météo
            balance = last_month['solde']
            expenses = last_month['depenses']
            revenues = last_month['revenus']
            
            # Calcul du score météo
            weather_score = 50  # Base
            
            if balance > 0:
                weather_score += 30
            else:
                weather_score -= 20
                
            if revenues > expenses * 1.2:
                weather_score += 20
            elif revenues < expenses:
                weather_score -= 30
            
            # Tendance (comparaison avec le mois précédent)
            if len(monthly_summary) > 1:
                prev_month = monthly_summary.iloc[-2]
                if last_month['solde'] > prev_month['solde']:
                    weather_score += 10
                    trend = "📈 En amélioration"
                else:
                    weather_score -= 10
                    trend = "📉 En dégradation"
            else:
                trend = "➡️ Stable"
            
            # Classification météo
            if weather_score >= 80:
                weather = "☀️ Ensoleillé"
                color = "#FFD700"
                advice = "Excellente santé financière ! C'est le moment d'investir."
            elif weather_score >= 60:
                weather = "⛅ Partiellement nuageux"
                color = "#87CEEB"
                advice = "Situation stable, continuez vos efforts d'épargne."
            elif weather_score >= 40:
                weather = "☁️ Nuageux"
                color = "#C0C0C0"
                advice = "Attention aux dépenses, révisez votre budget."
            elif weather_score >= 20:
                weather = "🌧️ Pluvieux"
                color = "#4682B4"
                advice = "Réduisez les dépenses non essentielles."
            else:
                weather = "⛈️ Orageux"
                color = "#8B0000"
                advice = "Situation critique ! Consultez un conseiller financier."
            
            # Affichage
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                st.markdown(f"""
                <div style="text-align: center; padding: 2rem; background: {color}; 
                           border-radius: 15px; margin: 1rem 0;">
                    <h2 style="margin: 0; font-size: 3rem;">{weather.split()[0]}</h2>
                    <h3 style="margin: 0; color: white;">{weather.split()[1]}</h3>
                    <p style="margin: 0; color: white;">Score: {weather_score}/100</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.write("**📊 Conditions Actuelles:**")
                st.write(f"• Solde: {balance:+.0f}€")
                st.write(f"• Revenus: {revenues:.0f}€")
                st.write(f"• Dépenses: {expenses:.0f}€")
                st.write(f"• Tendance: {trend}")
                
                st.write("**💡 Conseil du jour:**")
                st.info(advice)
            
            with col3:
                # Prévisions (simple)
                st.write("**🔮 Prévisions:**")
                
                # Prédiction simple basée sur la tendance
                if weather_score > 50:
                    if trend == "📈 En amélioration":
                        st.success("Demain: ☀️ Amélioration")
                    else:
                        st.info("Demain: ⛅ Stable")
                else:
                    if trend == "📉 En dégradation":
                        st.error("Demain: 🌧️ Dégradation")
                    else:
                        st.warning("Demain: ☁️ Incertain")
                
                # Historique météo (simplifiée)
                st.write("**📅 Historique (7j):**")
                for i in range(7):
                    day_score = weather_score + np.random.randint(-15, 15)
                    if day_score >= 60:
                        icon = "☀️"
                    elif day_score >= 40:
                        icon = "⛅"
                    else:
                        icon = "☁️"
                    st.write(f"J-{i}: {icon}")
    
    def create_expense_correlations(self):
        """Matrice de corrélation des dépenses"""
        st.subheader("🔗 Corrélations entre Catégories")
        
        # Préparer les données
        daily_expenses = self.analyzer.depenses_df.groupby([
            self.analyzer.depenses_df['date'].dt.date,
            'categorie'
        ])['montant'].sum().abs().reset_index()
        
        # Pivot pour avoir les catégories en colonnes
        expense_matrix = daily_expenses.pivot(
            index='date', 
            columns='categorie', 
            values='montant'
        ).fillna(0)
        
        if expense_matrix.shape[1] > 2:  # Au moins 3 catégories
            # Calculer la matrice de corrélation
            corr_matrix = expense_matrix.corr()
            
            # Créer la heatmap
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=np.around(corr_matrix.values, decimals=2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hovertemplate='<b>%{y}</b> vs <b>%{x}</b><br>Corrélation: %{z:.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Matrice de Corrélation des Dépenses",
                height=500,
                xaxis_title="Catégories",
                yaxis_title="Catégories"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Analyse des corrélations
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🔍 Corrélations Fortes (>0.5):**")
                strong_corr = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) > 0.5:
                            cat1 = corr_matrix.columns[i]
                            cat2 = corr_matrix.columns[j]
                            strong_corr.append((cat1, cat2, corr_val))
                
                if strong_corr:
                    for cat1, cat2, corr in strong_corr:
                        if corr > 0:
                            st.write(f"• ✅ {cat1} ↔ {cat2}: {corr:.2f}")
                        else:
                            st.write(f"• ❌ {cat1} ↔ {cat2}: {corr:.2f}")
                else:
                    st.write("Aucune corrélation forte détectée")
            
            with col2:
                st.write("**💡 Insights:**")
                
                # Trouver la catégorie la plus corrélée avec les autres
                avg_corr = corr_matrix.abs().mean().sort_values(ascending=False)
                most_correlated = avg_corr.index[0]
                
                st.write(f"• **Catégorie centrale:** {most_correlated}")
                st.write(f"• **Corrélation moyenne:** {avg_corr.iloc[0]:.2f}")
                
                # Recommandation
                if avg_corr.iloc[0] > 0.3:
                    st.info("🔗 Vos dépenses sont interconnectées. Surveillez les effets domino!")
                else:
                    st.success("🎯 Vos catégories de dépenses sont bien isolées.")
        else:
            st.info("📊 Pas assez de catégories pour l'analyse de corrélation")
    
    def create_expense_seasonality(self):
        """Analyse de saisonnalité des dépenses"""
        st.subheader("📅 Saisonnalité des Dépenses")
        
        df = self.analyzer.depenses_df.copy()
        
        # Ajouter des colonnes pour l'analyse saisonnière
        df['mois'] = df['date'].dt.month
        df['trimestre'] = df['date'].dt.quarter
        df['jour_annee'] = df['date'].dt.dayofyear
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Analyse par mois
            monthly_seasonality = df.groupby('mois')['montant'].sum().abs()
            
            # Noms des mois
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                          'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            
            fig = go.Figure(data=go.Bar(
                x=[month_names[i-1] for i in monthly_seasonality.index],
                y=monthly_seasonality.values,
                marker_color='#4ECDC4',
                name='Dépenses Mensuelles'
            ))
            
            fig.update_layout(
                title="Saisonnalité Mensuelle",
                xaxis_title="Mois",
                yaxis_title="Dépenses (€)",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Mois le plus/moins cher
            peak_month = monthly_seasonality.idxmax()
            low_month = monthly_seasonality.idxmin()
            
            st.write(f"**📈 Mois le + cher:** {month_names[peak_month-1]}")
            st.write(f"**📉 Mois le - cher:** {month_names[low_month-1]}")
        
        with col2:
            # Analyse par trimestre
            quarterly_seasonality = df.groupby('trimestre')['montant'].sum().abs()
            quarter_names = ['T1', 'T2', 'T3', 'T4']
            
            fig = go.Figure(data=go.Bar(
                x=[quarter_names[i-1] for i in quarterly_seasonality.index],
                y=quarterly_seasonality.values,
                marker_color='#FF6B6B',
                name='Dépenses Trimestrielles'
            ))
            
            fig.update_layout(
                title="Saisonnalité Trimestrielle",
                xaxis_title="Trimestre",
                yaxis_title="Dépenses (€)",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Analyse des tendances
            volatility = monthly_seasonality.std() / monthly_seasonality.mean() * 100
            
            if volatility < 20:
                st.success(f"✅ Dépenses régulières (volatilité: {volatility:.1f}%)")
            elif volatility < 40:
                st.warning(f"⚠️ Dépenses modérément variables (volatilité: {volatility:.1f}%)")
            else:
                st.error(f"🚨 Dépenses très variables (volatilité: {volatility:.1f}%)")
    
    def create_smart_alerts(self):
        """Système d'alertes intelligentes"""
        st.subheader("🔔 Alertes Intelligentes")
        
        alerts = []
        
        # Analyse des données récentes
        recent_data = self.analyzer.depenses_df[
            self.analyzer.depenses_df['date'] >= 
            (self.analyzer.depenses_df['date'].max() - timedelta(days=7))
        ]
        
        if not recent_data.empty:
            # Alert 1: Dépenses inhabituellement élevées
            recent_daily = recent_data.groupby(recent_data['date'].dt.date)['montant'].sum().abs()
            historical_avg = self.analyzer.depenses_df.groupby(
                self.analyzer.depenses_df['date'].dt.date
            )['montant'].sum().abs().mean()
            
            max_recent = recent_daily.max()
            if max_recent > historical_avg * 2:
                alerts.append({
                    'type': 'warning',
                    'title': '⚠️ Dépense exceptionnelle détectée',
                    'message': f'Dépense de {max_recent:.0f}€ (moyenne: {historical_avg:.0f}€)',
                    'action': 'Vérifiez vos dernières transactions'
                })
            
            # Alert 2: Nouvelle catégorie de dépense
            recent_categories = set(recent_data['categorie'].unique())
            historical_categories = set(self.analyzer.depenses_df['categorie'].unique())
            new_categories = recent_categories - historical_categories
            
            if new_categories:
                alerts.append({
                    'type': 'info',
                    'title': '📝 Nouvelle catégorie de dépense',
                    'message': f'Catégorie(s): {", ".join(new_categories)}',
                    'action': 'Ajustez votre budget si nécessaire'
                })
            
            # Alert 3: Fréquence inhabituelle
            category_freq = recent_data['categorie'].value_counts()
            for cat, freq in category_freq.items():
                if freq > 10:  # Plus de 10 transactions en 7 jours
                    alerts.append({
                        'type': 'warning',
                        'title': f'🔄 Fréquence élevée - {cat}',
                        'message': f'{freq} transactions en 7 jours',
                        'action': 'Surveillez cette catégorie'
                    })
            
            # Alert 4: Objectif mensuel en danger
            monthly_summary = self.analyzer.get_monthly_summary()
            if not monthly_summary.empty:
                current_month = monthly_summary.iloc[-1]
                if current_month['solde'] < 0:
                    alerts.append({
                        'type': 'error',
                        'title': '🚨 Budget mensuel dépassé',
                        'message': f'Déficit de {abs(current_month["solde"]):.0f}€',
                        'action': 'Réduisez les dépenses non essentielles'
                    })
        
        # Affichage des alertes
        if alerts:
            for alert in alerts[:5]:  # Limiter à 5 alertes
                if alert['type'] == 'error':
                    st.error(f"**{alert['title']}**\n{alert['message']}\n💡 {alert['action']}")
                elif alert['type'] == 'warning':
                    st.warning(f"**{alert['title']}**\n{alert['message']}\n💡 {alert['action']}")
                else:
                    st.info(f"**{alert['title']}**\n{alert['message']}\n💡 {alert['action']}")
        else:
            st.success("✅ Aucune alerte ! Vos finances sont sous contrôle.")
        
        # Configuration des alertes
        with st.expander("⚙️ Configuration des Alertes"):
            st.write("**Personnalisez vos seuils d'alerte:**")
            
            col1, col2 = st.columns(2)
            with col1:
                daily_threshold = st.slider("Seuil dépense quotidienne (€)", 50, 500, 200)
                category_threshold = st.slider("Seuil fréquence catégorie (7j)", 5, 20, 10)
            
            with col2:
                enable_email = st.checkbox("Notifications par email", False)
                enable_push = st.checkbox("Notifications push", True)
            
            if st.button("💾 Sauvegarder Configuration"):
                st.success("Configuration sauvegardée !")
    
    def create_comparison_benchmark(self):
        """Comparaison avec des benchmarks"""
        st.subheader("📊 Comparaison avec la Moyenne")
        
        # Benchmarks fictifs mais réalistes (moyennes nationales françaises)
        benchmarks = {
            'Courses': 400,
            'Loyer': 800,
            'Transport': 150,
            'Restaurants': 200,
            'Shopping': 120,
            'Loisirs': 180,
            'Santé': 80,
            'Abonnements': 60
        }
        
        # Données utilisateur
        user_data = self.analyzer.get_category_analysis()
        
        # Créer le graphique de comparaison
        categories = []
        user_values = []
        benchmark_values = []
        differences = []
        
        for category in benchmarks.keys():
            if category in user_data.index:
                categories.append(category)
                user_val = user_data.loc[category, 'total_depense']
                bench_val = benchmarks[category]
                
                user_values.append(user_val)
                benchmark_values.append(bench_val)
                differences.append(((user_val - bench_val) / bench_val) * 100)
        
        fig = go.Figure()
        
        # Barres utilisateur
        fig.add_trace(go.Bar(
            name='Vos Dépenses',
            x=categories,
            y=user_values,
            marker_color='#4ECDC4',
            offsetgroup=1
        ))
        
        # Barres benchmark
        fig.add_trace(go.Bar(
            name='Moyenne Nationale',
            x=categories,
            y=benchmark_values,
            marker_color='#FF6B6B',
            offsetgroup=2
        ))
        
        fig.update_layout(
            title="Comparaison avec la Moyenne Nationale",
            xaxis_title="Catégories",
            yaxis_title="Montant (€)",
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse des écarts
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📈 Au-dessus de la moyenne:**")
            above_avg = [(cat, diff) for cat, diff in zip(categories, differences) if diff > 10]
            if above_avg:
                for cat, diff in above_avg:
                    st.write(f"• {cat}: +{diff:.0f}%")
            else:
                st.write("Aucune catégorie significativement au-dessus")
        
        with col2:
            st.write("**📉 En-dessous de la moyenne:**")
            below_avg = [(cat, diff) for cat, diff in zip(categories, differences) if diff < -10]
            if below_avg:
                for cat, diff in below_avg:
                    st.write(f"• {cat}: {diff:.0f}%")
            else:
                st.write("Aucune catégorie significativement en-dessous")
        
        # Score global de comparaison
        avg_difference = np.mean([abs(d) for d in differences])
        if avg_difference < 20:
            st.success(f"✅ Profil équilibré (écart moyen: {avg_difference:.0f}%)")
        elif avg_difference < 40:
            st.warning(f"⚠️ Profil modérément atypique (écart moyen: {avg_difference:.0f}%)")
        else:
            st.error(f"🔍 Profil très spécifique (écart moyen: {avg_difference:.0f}%)")

# Fonction d'intégration dans l'app principale
def integrate_advanced_features(analyzer, visualizer):
    """Intègre les fonctionnalités avancées dans l'application"""
    advanced = AdvancedFeatures(analyzer, visualizer)
    
    st.markdown("---")
    st.header("🚀 Fonctionnalités Avancées")
    
    # Onglets pour les fonctionnalités avancées
    adv_tab1, adv_tab2, adv_tab3, adv_tab4 = st.tabs([
        "🌊 Analyses Visuelles", 
        "📊 Patterns & Corrélations", 
        "🌤️ Météo & Alertes",
        "📈 Comparaisons"
    ])
    
    with adv_tab1:
        col1, col2 = st.columns(2)
        with col1:
            advanced.create_expense_flow_diagram()
        with col2:
            advanced.create_spending_velocity_chart()
    
    with adv_tab2:
        advanced.create_expense_correlations()
        advanced.create_expense_seasonality()
    
    with adv_tab3:
        col1, col2 = st.columns([2, 1])
        with col1:
            advanced.create_financial_weather()
        with col2:
            advanced.create_smart_alerts()
    
    with adv_tab4:
        advanced.create_comparison_benchmark()
    
    return advanced 