import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

class DataGenerator:
    """Générateur de données bancaires fictives pour l'assistant d'épargne"""
    
    def __init__(self):
        self.categories_depenses = {
            'Courses': [
                'SUPER U PARIS', 'CARREFOUR CITY', 'LIDL MARKET', 'FRANPRIX', 
                'MONOPRIX', 'AUCHAN', 'LECLERC', 'PICARD SURGELES'
            ],
            'Restaurants': [
                'MCDONALDS', 'BURGER KING', 'PIZZA HUT', 'RESTO ASIAT',
                'BISTROT PARISIEN', 'CAFE DE FLORE', 'BOULANGERIE PAUL'
            ],
            'Transport': [
                'PASS NAVIGO', 'SNCF CONNECT', 'UBER', 'TICKET RATP',
                'STATION ESSENCE', 'PARKING INDIGO', 'VELIB METROPOLE'
            ],
            'Loyer': [
                'ORPI GESTION LOYER', 'CENTURY 21 LOYER', 'NEXITY LOYER',
                'FONCIA TRANSACTION'
            ],
            'Shopping': [
                'ZARA', 'H&M', 'AMAZON.FR', 'FNAC', 'DECATHLON',
                'SEPHORA', 'UNIQLO', 'GALERIES LAFAYETTE'
            ],
            'Abonnements': [
                'NETFLIX.COM', 'SPOTIFY AB', 'AMAZON PRIME', 'DISNEY PLUS',
                'ORANGE MOBILE', 'FREE MOBILE', 'EDF ENERGIE'
            ],
            'Loisirs': [
                'CINEMA GAUMONT', 'MUSEE DU LOUVRE', 'BAR LE PROGRES',
                'PARC ASTERIX', 'THEATRE CHATELET', 'FNAC SPECTACLES'
            ],
            'Santé': [
                'PHARMACIE LAFAYETTE', 'CABINET MEDICAL', 'DENTISTE DR MARTIN',
                'OPTICIEN KRYS', 'LABORATOIRE ANALYSES'
            ]
        }
        
        # Montants typiques par catégorie
        self.montants_ranges = {
            'Loyer': (700, 1200),
            'Courses': (15, 120),
            'Shopping': (20, 250),
            'Restaurants': (8, 60),
            'Transport': (5, 50),
            'Abonnements': (9, 50),
            'Loisirs': (10, 80),
            'Santé': (15, 150)
        }
    
    def generate_transactions(self, nb_transactions=500, start_date=None, end_date=None):
        """Génère un dataset de transactions fictives"""
        
        if start_date is None:
            start_date = datetime(2023, 1, 1)
        if end_date is None:
            end_date = datetime.now()
        
        data = []
        
        # Ajout de revenus mensuels réguliers
        current_date = start_date.replace(day=1)
        while current_date <= end_date:
            # Salaire mensuel - gérer les mois avec moins de 31 jours
            max_day = 28  # Jour sûr pour tous les mois
            if current_date.month in [1, 3, 5, 7, 8, 10, 12]:
                max_day = 31
            elif current_date.month in [4, 6, 9, 11]:
                max_day = 30
            elif current_date.month == 2:
                # Vérifier si c'est une année bissextile
                if current_date.year % 4 == 0 and (current_date.year % 100 != 0 or current_date.year % 400 == 0):
                    max_day = 29
                else:
                    max_day = 28
            
            salary_day = min(random.randint(28, 31), max_day)
            salary_date = current_date.replace(day=salary_day)
            
            if salary_date <= end_date:
                data.append([
                    salary_date, 
                    'VIREMENT SALAIRE ENTREPRISE', 
                    random.uniform(2800, 3500)
                ])
            current_date = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        # Génération des dépenses
        days_range = (end_date - start_date).days
        
        for i in range(nb_transactions):
            categorie = random.choice(list(self.categories_depenses.keys()))
            description = random.choice(self.categories_depenses[categorie])
            
            # Montants réalistes par catégorie
            min_amount, max_amount = self.montants_ranges[categorie]
            montant = -round(random.uniform(min_amount, max_amount), 2)
            
            # Date aléatoire dans la plage
            random_days = random.randint(0, days_range)
            date = start_date + timedelta(days=random_days)
            
            # Ajout de variabilité dans les descriptions
            if random.random() < 0.3:  # 30% de chance d'avoir des détails
                description += f" {random.choice(['PARIS', 'LYON', 'MARSEILLE'])}"
            
            data.append([date, description, montant])
        
        # Création du DataFrame
        df = pd.DataFrame(data, columns=['date', 'description', 'montant'])
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    def categorize_expense(self, description):
        """Assigne une catégorie basée sur des mots-clés dans la description"""
        description = description.upper()
        
        # Gestion des revenus
        if any(keyword in description for keyword in ['SALAIRE', 'VIREMENT', 'REMBOURSEMENT']):
            return 'Revenus'
        
        # Catégorisation des dépenses
        for categorie, keywords in self.categories_depenses.items():
            for keyword in keywords:
                if keyword.upper() in description:
                    return categorie
        
        return 'Autre'
    
    def process_data(self, df):
        """Traite et enrichit le DataFrame avec les catégories et métadonnées"""
        # Conversion des dates
        df['date'] = pd.to_datetime(df['date'])
        
        # Catégorisation
        df['categorie'] = df['description'].apply(self.categorize_expense)
        
        # Colonnes temporelles
        df['annee'] = df['date'].dt.year
        df['mois'] = df['date'].dt.month
        df['mois_nom'] = df['date'].dt.month_name()
        df['jour_semaine'] = df['date'].dt.day_name()
        df['semaine'] = df['date'].dt.isocalendar().week
        df['trimestre'] = df['date'].dt.quarter
        
        # Séparation revenus/dépenses
        df['type_transaction'] = df['montant'].apply(lambda x: 'Crédit' if x > 0 else 'Débit')
        
        return df
    
    def save_to_csv(self, df, filename='releve_bancaire_fictif.csv'):
        """Sauvegarde le DataFrame en CSV"""
        df.to_csv(filename, index=False, encoding='utf-8')
        return filename

if __name__ == "__main__":
    # Test du générateur
    generator = DataGenerator()
    df = generator.generate_transactions(nb_transactions=400)
    df = generator.process_data(df)
    
    filename = generator.save_to_csv(df)
    print(f"✅ Fichier '{filename}' généré avec succès.")
    print(f"📊 {len(df)} transactions générées")
    print(f"📅 Période: {df['date'].min().strftime('%d/%m/%Y')} - {df['date'].max().strftime('%d/%m/%Y')}")
    
    # Aperçu des données
    print("\n📋 Aperçu des données:")
    print(df.head())
    
    print("\n💰 Résumé par catégorie:")
    summary = df[df['montant'] < 0].groupby('categorie')['montant'].agg(['count', 'sum']).round(2)
    summary['sum'] = summary['sum'].abs()
    summary = summary.sort_values('sum', ascending=False)
    print(summary) 