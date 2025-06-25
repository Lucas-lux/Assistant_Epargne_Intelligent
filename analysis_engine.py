import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

class AnalysisEngine:
    """Moteur d'analyse pour l'assistant d'épargne"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.depenses_df = df[df['montant'] < 0].copy()
        self.revenus_df = df[df['montant'] > 0].copy()
    
    def _apply_period_filter(self, df, period='all', date_range=None):
        """Applique le filtre de période à un DataFrame"""
        df_filtered = df.copy()
        
        if date_range is not None and period == 'custom':
            # Filtre par dates personnalisées
            start_date, end_date = date_range
            df_filtered = df_filtered[
                (df_filtered['date'].dt.date >= start_date) & 
                (df_filtered['date'].dt.date <= end_date)
            ]
        elif period != 'all':
            current_date = df_filtered['date'].max()
            
            if period == 'current_month':
                start_of_month = current_date.replace(day=1)
                df_filtered = df_filtered[df_filtered['date'] >= start_of_month]
            elif period == 'last_month':
                # Mois précédent complet
                start_of_current = current_date.replace(day=1)
                end_of_last = start_of_current - timedelta(days=1)
                start_of_last = end_of_last.replace(day=1)
                df_filtered = df_filtered[
                    (df_filtered['date'] >= start_of_last) & 
                    (df_filtered['date'] <= end_of_last)
                ]
            elif period == 'last_3months':
                three_months_ago = current_date - timedelta(days=90)
                df_filtered = df_filtered[df_filtered['date'] >= three_months_ago]
            elif period == 'last_6months':
                six_months_ago = current_date - timedelta(days=180)
                df_filtered = df_filtered[df_filtered['date'] >= six_months_ago]
            elif period == 'current_year':
                start_of_year = current_date.replace(month=1, day=1)
                df_filtered = df_filtered[df_filtered['date'] >= start_of_year]
            elif period == 'last_year':
                last_year = current_date.year - 1
                start_of_last_year = current_date.replace(year=last_year, month=1, day=1)
                end_of_last_year = current_date.replace(year=last_year, month=12, day=31)
                df_filtered = df_filtered[
                    (df_filtered['date'] >= start_of_last_year) & 
                    (df_filtered['date'] <= end_of_last_year)
                ]
            elif period == 'last_12months':
                twelve_months_ago = current_date - timedelta(days=365)
                df_filtered = df_filtered[df_filtered['date'] >= twelve_months_ago]
        
        return df_filtered
        
    def get_monthly_summary(self):
        """Résumé mensuel des finances"""
        monthly = self.df.groupby(['annee', 'mois']).agg({
            'montant': ['sum', 'count']
        }).round(2)
        
        monthly.columns = ['total', 'nb_transactions']
        monthly = monthly.reset_index()
        monthly['periode'] = monthly.apply(lambda x: f"{int(x['annee'])}-{int(x['mois']):02d}", axis=1)
        
        # Séparation revenus/dépenses par mois
        monthly_income = self.revenus_df.groupby(['annee', 'mois'])['montant'].sum()
        monthly_expenses = self.depenses_df.groupby(['annee', 'mois'])['montant'].sum().abs()
        
        monthly['revenus'] = monthly.apply(lambda x: monthly_income.get((x['annee'], x['mois']), 0), axis=1)
        monthly['depenses'] = monthly.apply(lambda x: monthly_expenses.get((x['annee'], x['mois']), 0), axis=1)
        monthly['solde'] = monthly['revenus'] - monthly['depenses']
        
        return monthly
    
    def get_category_analysis(self, period='all', date_range=None):
        """Analyse par catégorie"""
        df_filtered = self._apply_period_filter(self.depenses_df, period, date_range)
        
        category_stats = df_filtered.groupby('categorie').agg({
            'montant': ['count', 'sum', 'mean', 'std']
        }).round(2)
        
        category_stats.columns = ['nb_transactions', 'total_depense', 'moyenne', 'ecart_type']
        category_stats['total_depense'] = category_stats['total_depense'].abs()
        category_stats = category_stats.sort_values('total_depense', ascending=False)
        
        # Pourcentage du total
        total_depenses = category_stats['total_depense'].sum()
        category_stats['pourcentage'] = (category_stats['total_depense'] / total_depenses * 100).round(1)
        
        return category_stats
    
    def get_spending_trends(self):
        """Analyse des tendances de dépenses"""
        # Dépenses par semaine
        weekly_spending = self.depenses_df.set_index('date').resample('W')['montant'].sum().abs()
        
        # Dépenses par mois
        monthly_spending = self.depenses_df.set_index('date').resample('M')['montant'].sum().abs()
        
        # Top catégories par mois
        monthly_by_category = self.depenses_df.groupby([
            self.depenses_df['date'].dt.to_period('M'), 
            'categorie'
        ])['montant'].sum().abs().unstack(fill_value=0)
        
        return {
            'weekly': weekly_spending,
            'monthly': monthly_spending,
            'monthly_by_category': monthly_by_category
        }
    
    def predict_future_spending(self, periods=4):
        """Prédiction des dépenses futures"""
        try:
            # Agrégation par semaine pour avoir suffisamment de points
            weekly_spending = self.depenses_df.set_index('date').resample('W')['montant'].sum().abs()
            
            if len(weekly_spending) < 10:
                return {
                    'success': False,
                    'message': 'Pas assez de données pour une prédiction fiable',
                    'predictions': None
                }
            
            # Méthode simple: moyenne mobile
            recent_avg = weekly_spending.tail(8).mean()  # Moyenne des 8 dernières semaines
            trend = (weekly_spending.tail(4).mean() - weekly_spending.head(4).mean()) / len(weekly_spending)
            
            predictions = []
            for i in range(1, periods + 1):
                pred_value = recent_avg + (trend * i)
                predictions.append(max(pred_value, 0))  # Pas de dépenses négatives
            
            # Si statsmodels est disponible, utiliser ARIMA
            if STATSMODELS_AVAILABLE and len(weekly_spending) >= 20:
                try:
                    model = ARIMA(weekly_spending.values, order=(1,1,1))
                    fitted_model = model.fit()
                    arima_pred = fitted_model.forecast(steps=periods)
                    predictions = [max(x, 0) for x in arima_pred]
                except:
                    pass  # Garder les prédictions simples
            
            return {
                'success': True,
                'predictions': predictions,
                'current_avg': recent_avg,
                'trend': 'croissante' if trend > 0 else 'décroissante',
                'confidence': 'élevée' if len(weekly_spending) >= 20 else 'modérée'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur dans la prédiction: {str(e)}',
                'predictions': None
            }
    
    def identify_savings_opportunities(self):
        """Identification des opportunités d'économies"""
        opportunities = {}
        
        # 1. Catégories "compressibles"
        compressible_categories = ['Restaurants', 'Loisirs', 'Shopping']
        compressible_spending = self.depenses_df[
            self.depenses_df['categorie'].isin(compressible_categories)
        ].groupby('categorie')['montant'].sum().abs()
        
        total_compressible = compressible_spending.sum()
        opportunities['depenses_compressibles'] = {
            'total': total_compressible,
            'detail': compressible_spending.to_dict(),
            'economie_potentielle_20pct': total_compressible * 0.2,
            'economie_potentielle_30pct': total_compressible * 0.3
        }
        
        # 2. Détection des abonnements
        abonnements = self.depenses_df[self.depenses_df['categorie'] == 'Abonnements']
        if not abonnements.empty:
            monthly_subscriptions = abonnements.groupby('description')['montant'].agg(['count', 'mean'])
            monthly_subscriptions['mean'] = monthly_subscriptions['mean'].abs()
            monthly_subscriptions = monthly_subscriptions[monthly_subscriptions['count'] >= 2]  # Au moins 2 occurrences
            
            opportunities['abonnements'] = {
                'total_mensuel': monthly_subscriptions['mean'].sum() if not monthly_subscriptions.empty else 0,
                'detail': monthly_subscriptions.to_dict('index') if not monthly_subscriptions.empty else {}
            }
        else:
            opportunities['abonnements'] = {
                'total_mensuel': 0,
                'detail': {}
            }
        
        # 3. Dépenses inhabituelles (outliers)
        unusual_expenses = []
        for category in self.depenses_df['categorie'].unique():
            cat_data = self.depenses_df[self.depenses_df['categorie'] == category]['montant'].abs()
            if len(cat_data) > 5:
                threshold = cat_data.mean() + 2 * cat_data.std()
                outliers = self.depenses_df[
                    (self.depenses_df['categorie'] == category) & 
                    (self.depenses_df['montant'].abs() > threshold)
                ]
                if not outliers.empty:
                    unusual_expenses.extend(outliers.to_dict('records'))
        
        opportunities['depenses_inhabituelles'] = unusual_expenses[:10]  # Top 10
        
        # 4. Analyse des habitudes de week-end vs semaine
        weekend_spending = abs(self.depenses_df[
            self.depenses_df['jour_semaine'].isin(['Saturday', 'Sunday'])
        ]['montant'].sum())
        
        weekday_spending = abs(self.depenses_df[
            ~self.depenses_df['jour_semaine'].isin(['Saturday', 'Sunday'])
        ]['montant'].sum())
        
        opportunities['repartition_semaine'] = {
            'weekend': weekend_spending,
            'semaine': weekday_spending,
            'ratio_weekend': weekend_spending / (weekend_spending + weekday_spending) * 100
        }
        
        return opportunities
    
    def get_financial_health_score(self):
        """Calcul d'un score de santé financière"""
        monthly_summary = self.get_monthly_summary()
        
        if monthly_summary.empty:
            return {'score': 0, 'details': {}}
        
        # Critères d'évaluation
        avg_balance = monthly_summary['solde'].mean()
        balance_stability = monthly_summary['solde'].std()
        positive_months = (monthly_summary['solde'] > 0).sum()
        total_months = len(monthly_summary)
        
        # Score de base (0-100)
        score = 50
        
        # Solde moyen positif: +30 points
        if avg_balance > 0:
            score += min(30, avg_balance / 1000 * 10)
        else:
            score -= 20
        
        # Stabilité: +20 points
        if balance_stability < 500:
            score += 20
        elif balance_stability < 1000:
            score += 10
        
        # Pourcentage de mois positifs: +30 points
        positive_ratio = positive_months / total_months if total_months > 0 else 0
        score += positive_ratio * 30
        
        # Limitation 0-100
        score = max(0, min(100, score))
        
        return {
            'score': round(score),
            'details': {
                'solde_moyen': round(avg_balance, 2),
                'stabilite': round(balance_stability, 2),
                'mois_positifs': positive_months,
                'total_mois': total_months,
                'ratio_positif': round(positive_ratio * 100, 1)
            },
            'niveau': self._get_score_level(score)
        }
    
    def _get_score_level(self, score):
        """Conversion du score en niveau"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Bon"
        elif score >= 40:
            return "Moyen"
        elif score >= 20:
            return "Fragile"
        else:
            return "Critique" 