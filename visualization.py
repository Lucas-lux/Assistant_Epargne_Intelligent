import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st

class VisualizationEngine:
    """Moteur de visualisation pour l'assistant d'épargne"""
    
    def __init__(self):
        # Palette de couleurs personnalisée
        self.color_palette = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', 
            '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43'
        ]
        
        # Couleurs par catégorie
        self.category_colors = {
            'Courses': '#4ECDC4',
            'Restaurants': '#FF6B6B', 
            'Transport': '#45B7D1',
            'Shopping': '#FECA57',
            'Loisirs': '#FF9FF3',
            'Loyer': '#96CEB4',
            'Abonnements': '#54A0FF',
            'Santé': '#5F27CD',
            'Autre': '#DDA0DD'
        }
    
    def create_expenses_pie_chart(self, category_data, title="Répartition des Dépenses"):
        """Graphique camembert des dépenses par catégorie"""
        
        # Préparation des données
        categories = category_data.index.tolist()
        values = category_data['total_depense'].tolist()
        percentages = category_data['pourcentage'].tolist()
        
        # Couleurs personnalisées
        colors = [self.category_colors.get(cat, '#DDA0DD') for cat in categories]
        
        fig = go.Figure(data=[go.Pie(
            labels=categories,
            values=values,
            hole=0.4,
            marker_colors=colors,
            textinfo='label+percent',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>' +
                         'Montant: %{value:.2f}€<br>' +
                         'Pourcentage: %{percent}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'family': 'Arial, sans-serif'}
            },
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=60, b=60, l=20, r=20),
            height=500
        )
        
        return fig
    
    def create_monthly_trends(self, monthly_data, title="Évolution Mensuelle"):
        """Graphique d'évolution mensuelle des finances"""
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Revenus vs Dépenses', 'Solde Mensuel'),
            vertical_spacing=0.1,
            row_heights=[0.6, 0.4]
        )
        
        # Graphique 1: Revenus vs Dépenses
        fig.add_trace(
            go.Scatter(
                x=monthly_data['periode'],
                y=monthly_data['revenus'],
                mode='lines+markers',
                name='Revenus',
                line=dict(color='#4ECDC4', width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=monthly_data['periode'],
                y=monthly_data['depenses'],
                mode='lines+markers',
                name='Dépenses',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Graphique 2: Solde
        colors = ['#4ECDC4' if x >= 0 else '#FF6B6B' for x in monthly_data['solde']]
        
        fig.add_trace(
            go.Bar(
                x=monthly_data['periode'],
                y=monthly_data['solde'],
                name='Solde',
                marker_color=colors,
                showlegend=False
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            height=600,
            hovermode='x unified'
        )
        
        fig.update_xaxes(title_text="Période", row=2, col=1)
        fig.update_yaxes(title_text="Montant (€)", row=1, col=1)
        fig.update_yaxes(title_text="Solde (€)", row=2, col=1)
        
        return fig
    
    def create_category_evolution(self, monthly_by_category, top_n=5):
        """Évolution des top catégories dans le temps"""
        
        # Sélection des top catégories
        total_by_category = monthly_by_category.sum().sort_values(ascending=False)
        top_categories = total_by_category.head(top_n).index
        
        fig = go.Figure()
        
        for i, category in enumerate(top_categories):
            color = self.category_colors.get(category, self.color_palette[i % len(self.color_palette)])
            
            fig.add_trace(go.Scatter(
                x=monthly_by_category.index.astype(str),
                y=monthly_by_category[category],
                mode='lines+markers',
                name=category,
                line=dict(color=color, width=3),
                marker=dict(size=6)
            ))
        
        fig.update_layout(
            title={
                'text': f'Évolution des Top {top_n} Catégories de Dépenses',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title="Période",
            yaxis_title="Montant (€)",
            hovermode='x unified',
            height=400,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig
    
    def create_weekly_spending_heatmap(self, df):
        """Heatmap des dépenses par jour de la semaine et heure"""
        
        # Créer des données d'exemple pour l'heure (simulation)
        import random
        df_copy = df[df['montant'] < 0].copy()
        df_copy['heure'] = [random.randint(8, 22) for _ in range(len(df_copy))]
        
        # Mapping des jours en français
        day_mapping = {
            'Monday': 'Lundi',
            'Tuesday': 'Mardi', 
            'Wednesday': 'Mercredi',
            'Thursday': 'Jeudi',
            'Friday': 'Vendredi',
            'Saturday': 'Samedi',
            'Sunday': 'Dimanche'
        }
        
        df_copy['jour_fr'] = df_copy['jour_semaine'].map(day_mapping)
        
        # Agrégation par jour et heure
        heatmap_data = df_copy.groupby(['jour_fr', 'heure'])['montant'].sum().abs().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='jour_fr', columns='heure', values='montant').fillna(0)
        
        # Réorganiser les jours
        day_order = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        heatmap_pivot = heatmap_pivot.reindex(day_order)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="Montant (€)")
        ))
        
        fig.update_layout(
            title={
                'text': 'Heatmap des Dépenses par Jour et Heure',
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title="Heure de la journée",
            yaxis_title="Jour de la semaine",
            height=400
        )
        
        return fig
    
    def create_savings_gauge(self, current_savings, target_savings):
        """Jauge des économies réalisées"""
        
        percentage = min((current_savings / target_savings) * 100, 100) if target_savings > 0 else 0
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = percentage,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Objectif d'Économies (%)"},
            delta = {'reference': 100},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#4ECDC4"},
                'steps': [
                    {'range': [0, 25], 'color': "#FFE5E5"},
                    {'range': [25, 50], 'color': "#FFD1DC"},
                    {'range': [50, 75], 'color': "#E6F3FF"},
                    {'range': [75, 100], 'color': "#E8F8F5"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        
        return fig
    
    def create_prediction_chart(self, historical_data, predictions):
        """Graphique de prédiction des dépenses"""
        
        fig = go.Figure()
        
        # Données historiques
        fig.add_trace(go.Scatter(
            x=list(range(len(historical_data))),
            y=historical_data,
            mode='lines+markers',
            name='Historique',
            line=dict(color='#4ECDC4', width=2),
            marker=dict(size=4)
        ))
        
        # Prédictions
        future_x = list(range(len(historical_data), len(historical_data) + len(predictions)))
        
        fig.add_trace(go.Scatter(
            x=future_x,
            y=predictions,
            mode='lines+markers',
            name='Prédiction',
            line=dict(color='#FF6B6B', width=2, dash='dash'),
            marker=dict(size=6, symbol='diamond')
        ))
        
        # Zone de transition
        if len(historical_data) > 0 and len(predictions) > 0:
            fig.add_trace(go.Scatter(
                x=[len(historical_data)-1, len(historical_data)],
                y=[historical_data[-1], predictions[0]],
                mode='lines',
                line=dict(color='gray', width=1, dash='dot'),
                showlegend=False
            ))
        
        fig.update_layout(
            title={
                'text': 'Prédiction des Dépenses Futures',
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title="Période",
            yaxis_title="Montant (€)",
            hovermode='x',
            height=400
        )
        
        return fig
    
    def create_financial_health_radar(self, health_data):
        """Graphique radar pour la santé financière"""
        
        categories = ['Solde Moyen', 'Stabilité', 'Régularité', 'Économies', 'Contrôle']
        
        # Conversion des métriques en scores 0-100
        values = [
            min(100, max(0, health_data['details']['solde_moyen'] / 50)), # Solde moyen
            min(100, max(0, 100 - health_data['details']['stabilite'] / 20)), # Stabilité (inversé)
            health_data['details']['ratio_positif'], # Régularité
            min(100, health_data['score']), # Score global comme proxy économies
            min(100, health_data['score']) # Score global comme proxy contrôle
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Votre Score',
            line_color='#4ECDC4',
            fillcolor='rgba(78, 205, 196, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title={
                'text': 'Radar de Santé Financière',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=400
        )
        
        return fig 