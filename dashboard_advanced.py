import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AdvancedDashboard:
    """Module d'améliorations avancées pour l'assistant d'épargne"""
    
    def __init__(self, analyzer, visualizer):
        self.analyzer = analyzer
        self.visualizer = visualizer
        
    def create_kpi_dashboard(self, period_filter, date_range):
        """Tableau de bord KPI avancé"""
        st.subheader("📊 Tableau de Bord KPI")
        
        # Calcul des KPIs
        kpis = self._calculate_advanced_kpis(period_filter, date_range)
        
        # Affichage en colonnes responsives
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            delta_color = "normal" if kpis['spending_trend'] >= 0 else "inverse"
            st.metric(
                "Dépenses Moyennes/Semaine",
                f"{kpis['avg_weekly_spending']:.0f}€",
                delta=f"{kpis['spending_trend']:+.1f}%",
                delta_color=delta_color
            )
        
        with col2:
            st.metric(
                "Taux d'Épargne",
                f"{kpis['savings_rate']:.1f}%",
                delta=f"{kpis['savings_trend']:+.1f}%"
            )
        
        with col3:
            st.metric(
                "Volatilité Financière",
                f"{kpis['volatility']:.0f}€",
                delta=f"{kpis['volatility_trend']:+.1f}%",
                delta_color="inverse"
            )
        
        with col4:
            st.metric(
                "Score Prédictibilité",
                f"{kpis['predictability_score']:.0f}/100",
                delta=f"{kpis['pred_trend']:+.0f}pts"
            )
        
        return kpis
    
    def create_waterfall_chart(self, monthly_data):
        """Graphique waterfall des flux financiers"""
        if monthly_data.empty:
            return None
            
        # Prendre le dernier mois avec données complètes
        last_month = monthly_data.iloc[-1]
        
        categories = ['Solde Début', 'Revenus', 'Courses', 'Loyer', 'Restaurants', 
                     'Transport', 'Shopping', 'Autres Dépenses', 'Solde Final']
        
        # Calculer les valeurs (simulées pour l'exemple)
        revenus = last_month['revenus']
        depenses = last_month['depenses']
        
        # Répartition estimée des dépenses
        values = [
            last_month['solde'] - revenus + depenses,  # Solde début (calculé)
            revenus,  # Revenus (positif)
            -depenses * 0.3,  # Courses (négatif)
            -depenses * 0.35,  # Loyer (négatif)
            -depenses * 0.1,   # Restaurants (négatif)
            -depenses * 0.08,  # Transport (négatif)
            -depenses * 0.12,  # Shopping (négatif)
            -depenses * 0.05,  # Autres (négatif)
            last_month['solde']  # Solde final
        ]
        
        fig = go.Figure(go.Waterfall(
            name="Flux Financiers",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "relative", 
                    "relative", "relative", "relative", "total"],
            x=categories,
            textposition="outside",
            text=[f"{v:+.0f}€" for v in values],
            y=values,
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "#4ECDC4"}},
            decreasing={"marker": {"color": "#FF6B6B"}},
            totals={"marker": {"color": "#45B7D1"}}
        ))
        
        fig.update_layout(
            title="Analyse des Flux Financiers (Dernier Mois)",
            showlegend=False,
            height=500,
            yaxis_title="Montant (€)"
        )
        
        return fig
    
    def create_spending_patterns_analysis(self):
        """Analyse des patterns de dépenses avec ML"""
        st.subheader("🧠 Analyse des Patterns de Dépenses (IA)")
        
        # Préparation des données pour le clustering
        df_daily = self.analyzer.depenses_df.groupby([
            self.analyzer.depenses_df['date'].dt.date,
            'categorie'
        ])['montant'].sum().abs().reset_index()
        
        # Pivot pour avoir les catégories en colonnes
        df_pivot = df_daily.pivot(index='date', columns='categorie', values='montant').fillna(0)
        
        if len(df_pivot) > 10:  # Assez de données pour le clustering
            # Normalisation
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(df_pivot.values)
            
            # Clustering K-means
            n_clusters = min(4, len(df_pivot) // 5)  # Max 4 clusters
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(scaled_data)
            
            # Analyse des clusters
            df_pivot['Cluster'] = clusters
            cluster_analysis = df_pivot.groupby('Cluster').agg({
                col: 'mean' for col in df_pivot.columns if col != 'Cluster'
            }).round(2)
            
            # Visualisation
            col1, col2 = st.columns(2)
            
            with col1:
                # Graphique des clusters
                fig_cluster = self._create_cluster_visualization(df_pivot, clusters)
                st.plotly_chart(fig_cluster, use_container_width=True)
            
            with col2:
                # Profils des clusters
                st.write("**Profils de Dépenses Identifiés :**")
                cluster_names = {
                    0: "🟢 Économe",
                    1: "🟡 Équilibré", 
                    2: "🟠 Dépensier",
                    3: "🔴 Impulsif"
                }
                
                for i in range(n_clusters):
                    cluster_name = cluster_names.get(i, f"Profil {i+1}")
                    cluster_data = cluster_analysis.loc[i]
                    main_category = cluster_data.drop('Cluster', errors='ignore').idxmax()
                    avg_spending = cluster_data.drop('Cluster', errors='ignore').sum()
                    
                    st.write(f"**{cluster_name}**")
                    st.write(f"• Principale catégorie: {main_category}")
                    st.write(f"• Dépenses moyennes: {avg_spending:.0f}€/jour")
                    
                    # Compter les jours dans ce cluster
                    days_in_cluster = (clusters == i).sum()
                    st.write(f"• Fréquence: {days_in_cluster} jours")
                    st.write("---")
            
            return cluster_analysis
        else:
            st.info("📊 Pas assez de données pour l'analyse de patterns (minimum 10 jours requis)")
            return None
    
    def create_anomaly_detection(self):
        """Détection d'anomalies dans les dépenses"""
        st.subheader("🚨 Détection d'Anomalies")
        
        # Calcul des dépenses quotidiennes
        daily_spending = self.analyzer.depenses_df.groupby(
            self.analyzer.depenses_df['date'].dt.date
        )['montant'].sum().abs()
        
        if len(daily_spending) > 7:
            # Calcul des seuils d'anomalie (méthode IQR)
            Q1 = daily_spending.quantile(0.25)
            Q3 = daily_spending.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Identification des anomalies
            anomalies = daily_spending[(daily_spending < lower_bound) | (daily_spending > upper_bound)]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Graphique des anomalies
                fig = go.Figure()
                
                # Dépenses normales
                normal_spending = daily_spending[~daily_spending.index.isin(anomalies.index)]
                fig.add_trace(go.Scatter(
                    x=normal_spending.index,
                    y=normal_spending.values,
                    mode='markers+lines',
                    name='Dépenses Normales',
                    marker=dict(color='#4ECDC4', size=6),
                    line=dict(width=1)
                ))
                
                # Anomalies
                if not anomalies.empty:
                    fig.add_trace(go.Scatter(
                        x=anomalies.index,
                        y=anomalies.values,
                        mode='markers',
                        name='Anomalies',
                        marker=dict(color='#FF6B6B', size=10, symbol='diamond')
                    ))
                
                # Seuils
                fig.add_hline(y=upper_bound, line_dash="dash", line_color="red", 
                             annotation_text=f"Seuil haut: {upper_bound:.0f}€")
                fig.add_hline(y=lower_bound, line_dash="dash", line_color="orange", 
                             annotation_text=f"Seuil bas: {lower_bound:.0f}€")
                
                fig.update_layout(
                    title="Détection d'Anomalies dans les Dépenses Quotidiennes",
                    xaxis_title="Date",
                    yaxis_title="Dépenses (€)",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write("**📊 Statistiques d'Anomalies**")
                st.metric("Anomalies Détectées", f"{len(anomalies)}")
                st.metric("Taux d'Anomalie", f"{len(anomalies)/len(daily_spending)*100:.1f}%")
                
                if not anomalies.empty:
                    st.write("**🔍 Dernières Anomalies:**")
                    for date, amount in anomalies.tail(3).items():
                        st.write(f"• {date}: {amount:.0f}€")
                
                # Recommandation
                if len(anomalies) / len(daily_spending) > 0.2:
                    st.warning("⚠️ Taux d'anomalie élevé - Vérifiez vos habitudes de dépenses")
                else:
                    st.success("✅ Dépenses régulières et prévisibles")
            
            return anomalies
        else:
            st.info("📊 Pas assez de données pour la détection d'anomalies")
            return None
    
    def create_budget_simulator(self):
        """Simulateur de budget interactif"""
        st.subheader("💡 Simulateur de Budget")
        
        # Interface de saisie
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🎯 Définir un Budget**")
            budget_type = st.selectbox(
                "Type de budget",
                ["Budget Mensuel", "Budget par Catégorie", "Objectif d'Épargne"]
            )
            
            if budget_type == "Budget Mensuel":
                monthly_budget = st.slider("Budget mensuel (€)", 1000, 5000, 2500, 100)
                current_avg = self.analyzer.get_monthly_summary()['depenses'].mean()
                difference = monthly_budget - current_avg
                
                st.metric("Budget vs Réalité", f"{difference:+.0f}€")
                
                if difference > 0:
                    st.success(f"✅ Marge de {difference:.0f}€ par rapport à vos dépenses actuelles")
                else:
                    st.error(f"⚠️ Dépassement de {abs(difference):.0f}€ par rapport à vos dépenses actuelles")
            
            elif budget_type == "Budget par Catégorie":
                st.write("**Budgets par Catégorie:**")
                category_analysis = self.analyzer.get_category_analysis()
                
                budgets = {}
                for category in category_analysis.index[:5]:  # Top 5 catégories
                    current = category_analysis.loc[category, 'total_depense']
                    budgets[category] = st.slider(
                        f"{category}",
                        0, int(current * 2), int(current), 10
                    )
                
                total_budget = sum(budgets.values())
                total_current = sum(category_analysis['total_depense'][:5])
                
                st.metric("Budget Total vs Actuel", f"{total_budget - total_current:+.0f}€")
        
        with col2:
            st.write("**📊 Simulation Visuelle**")
            
            if budget_type == "Budget Mensuel":
                # Graphique de projection
                months = list(range(1, 13))
                current_trend = [current_avg] * 12
                budget_line = [monthly_budget] * 12
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=months, y=current_trend,
                    mode='lines', name='Dépenses Actuelles',
                    line=dict(color='#FF6B6B', width=3)
                ))
                fig.add_trace(go.Scatter(
                    x=months, y=budget_line,
                    mode='lines', name='Budget Cible',
                    line=dict(color='#4ECDC4', width=3, dash='dash')
                ))
                
                fig.update_layout(
                    title="Projection Budget vs Réalité",
                    xaxis_title="Mois",
                    yaxis_title="Montant (€)",
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calcul d'économies potentielles
                if difference > 0:
                    annual_savings = difference * 12
                    st.info(f"💰 Économies potentielles: {annual_savings:.0f}€/an")
    
    def create_goals_tracker(self):
        """Suivi d'objectifs d'épargne"""
        st.subheader("🎯 Suivi d'Objectifs")
        
        # Interface de définition d'objectifs
        col1, col2 = st.columns(2)
        
        with col1:
            goal_name = st.text_input("Nom de l'objectif", "Vacances d'été")
            target_amount = st.number_input("Montant cible (€)", 0, 50000, 3000, 100)
            target_date = st.date_input("Date cible", datetime.now() + timedelta(days=365))
            
            # Calcul de l'épargne mensuelle nécessaire
            months_remaining = max(1, (target_date - datetime.now().date()).days / 30)
            monthly_needed = target_amount / months_remaining
            
            st.write(f"**Épargne mensuelle nécessaire:** {monthly_needed:.0f}€")
        
        with col2:
            # Simulation de progression
            current_savings = st.slider("Épargne actuelle (€)", 0, target_amount, 500, 50)
            monthly_savings = st.slider("Épargne mensuelle réelle (€)", 0, 1000, int(monthly_needed), 50)
            
            # Calcul de la progression
            progress = (current_savings / target_amount) * 100
            months_to_goal = max(0, (target_amount - current_savings) / max(1, monthly_savings))
            
            # Jauge de progression
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=progress,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Progression - {goal_name}"},
                delta={'reference': 100, 'suffix': '%'},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#4ECDC4"},
                    'steps': [
                        {'range': [0, 50], 'color': "#FFE5E5"},
                        {'range': [50, 80], 'color': "#E6F3FF"},
                        {'range': [80, 100], 'color': "#E8F8F5"}
                    ],
                    'threshold': {
                        'line': {'color': "green", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Informations sur l'objectif
            if monthly_savings > 0:
                completion_date = datetime.now() + timedelta(days=months_to_goal * 30)
                if completion_date.date() <= target_date:
                    st.success(f"✅ Objectif atteignable le {completion_date.strftime('%d/%m/%Y')}")
                else:
                    days_late = (completion_date.date() - target_date).days
                    st.warning(f"⚠️ Retard estimé: {days_late} jours")
    
    def _calculate_advanced_kpis(self, period_filter, date_range):
        """Calcul des KPIs avancés"""
        # Données filtrées
        df_filtered = self.analyzer._apply_period_filter(self.analyzer.df, period_filter, date_range)
        
        # KPIs de base
        weekly_spending = df_filtered[df_filtered['montant'] < 0].resample('W', on='date')['montant'].sum().abs()
        monthly_data = self.analyzer.get_monthly_summary()
        
        kpis = {
            'avg_weekly_spending': weekly_spending.mean() if not weekly_spending.empty else 0,
            'spending_trend': 0,  # Simplification
            'savings_rate': 0,
            'savings_trend': 0,
            'volatility': weekly_spending.std() if not weekly_spending.empty else 0,
            'volatility_trend': 0,
            'predictability_score': 75,  # Score par défaut
            'pred_trend': 5
        }
        
        # Calcul du taux d'épargne
        if not monthly_data.empty:
            avg_income = monthly_data['revenus'].mean()
            avg_expenses = monthly_data['depenses'].mean()
            if avg_income > 0:
                kpis['savings_rate'] = ((avg_income - avg_expenses) / avg_income) * 100
        
        return kpis
    
    def _create_cluster_visualization(self, df_pivot, clusters):
        """Crée la visualisation des clusters"""
        # Réduction de dimensionnalité simple (moyenne par cluster)
        cluster_data = []
        dates = []
        colors = []
        
        color_map = {0: '#4ECDC4', 1: '#FF9FF3', 2: '#FECA57', 3: '#FF6B6B'}
        
        for i, (date, row) in enumerate(df_pivot.iterrows()):
            cluster = clusters[i]
            total_spending = row.drop('Cluster').sum()
            
            cluster_data.append(total_spending)
            dates.append(date)
            colors.append(color_map.get(cluster, '#DDA0DD'))
        
        fig = go.Figure()
        
        for cluster_id in np.unique(clusters):
            cluster_mask = clusters == cluster_id
            cluster_dates = [dates[i] for i in range(len(dates)) if cluster_mask[i]]
            cluster_amounts = [cluster_data[i] for i in range(len(cluster_data)) if cluster_mask[i]]
            
            fig.add_trace(go.Scatter(
                x=cluster_dates,
                y=cluster_amounts,
                mode='markers',
                name=f'Cluster {cluster_id}',
                marker=dict(
                    color=color_map.get(cluster_id, '#DDA0DD'),
                    size=8
                )
            ))
        
        fig.update_layout(
            title="Clusters de Dépenses Quotidiennes",
            xaxis_title="Date",
            yaxis_title="Dépenses Totales (€)",
            height=400
        )
        
        return fig 