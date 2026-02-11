# Démo Visuelle - EcoDistribution Dashboard

## 🖼️ À quoi ressemble le dashboard ?

Le dashboard EcoDistribution est une application web moderne et professionnelle avec plusieurs écrans :

## 📊 Écran Principal - Tableau de Bord

### Header et Navigation
- **Logo EcoDistribution** avec sous-titre "Tableau de bord décisionnel"
- **Menu latéral** avec 5 sections :
  - 🏠 Tableau de bord
  - 📈 Analyse des ventes  
  - 📦 Gestion des stocks
  - 👥 Analyse clients
  - ⚙️ Paramètres

### KPI Principaux (4 cartes)
- **Chiffre d'affaires HT** : 125 450,50 € (+12.5% vs mois dernier)
- **Marge brute** : 28 950,75 € (+8.3% vs mois dernier)
- **Commandes** : 156 (-2.1% vs mois dernier)
- **Clients actifs** : 45 (+5.7% vs mois dernier)

### Graphiques Principaux
- **Évolution des ventes** : Courbe sur 6 mois (août 2024 à janvier 2025)
- **Top 5 produits** : Camembert montrant les produits les plus vendus

### Alertes et Performance
- **Alertes stocks** : Tableau avec produits en alerte/surstock
- **Indicateurs de performance** : 4 jauges circulaires
  - Taux de service client : 95%
  - Taux de rotation stocks : 78%
  - Marge moyenne : 23.5%
  - Livraisons ponctuelles : 89%

## 📈 Écran Analyse des Ventes

### Filtres Supérieurs
- **Période** : 3/6/12 derniers mois
- **Région** : Toutes/Auvergne-Rhône-Alpes/PACA/Hauts-de-France
- **Segment** : Grands comptes/Comptes moyens/Petits comptes

### Graphiques
- **Évolution des ventes** : Courbe temporelle interactive
- **Ventes par segment client** : Camembert des répartitions
- **Ventes par région** : Histogramme comparatif

### Tableaux Détaillés
- **Top produits** : Quantité, CA, prix moyen
- **Performance commerciaux** : CA, marge, taux marge, commandes, panier moyen

## 📦 Écran Gestion des Stocks

### Filtres
- **Entrepôt** : Lyon/Marseille/Lille
- **Famille produit** : Entretien/Emballages/Équipements/Hygiène
- **Période** : 7/30/90 derniers jours

### KPI Stocks
- **Produits référencés** : 20
- **Produits en alerte** : 3
- **Produits en surstock** : 2
- **Taux rotation** : 78% (jauge circulaire)

### Graphiques
- **Évolution valeur stocks** : Courbe sur 30 jours
- **Mouvements récents** : Histogramme entrées/sorties

### Tableaux
- **État des stocks** : Produit, référence, famille, stock actuel, seuil, statut, valeur
- **Mouvements récents** : Date, produit, type, quantité, motif

## 👥 Écran Analyse Clients

### Filtres
- **Segment** : Tous/Grands comptes/Comptes moyens/Petits comptes
- **Période** : 6/12/24 derniers mois

### KPI Clients
- **Clients actifs** : 45 (+5.7% vs mois dernier)
- **Nouveaux clients (mois)** : 3 (+25% vs moyenne)
- **Rentabilité moyenne** : 24.8% (-1.2% vs mois dernier)
- **Panier moyen** : 38€ (+8.3% vs mois dernier)

### Graphiques
- **Évolution clients actifs** : Courbe de croissance
- **Nouveaux clients par mois** : Histogramme
- **Distribution par segment** : Camembert

### Tableaux
- **Top clients rentabilité** : Client, CA, marge, rentabilité (jauge), segment, rang
- **Détail clients** : Secteur, taille, commandes, panier moyen, délai paiement, statut

## 🎨 Design et UX

### Style Visuel
- **Couleurs professionnelles** : Bleu principal (#1890ff), vert pour succès, rouge pour alertes
- **Typographie claire** : Hiérarchie visuelle évidente
- **Cartes avec ombres** : Design moderne et épuré
- **Icônes Ant Design** : Cohérent et intuitif

### Interactions
- **Filtres dynamiques** : Mise à jour instantanée des graphiques
- **Graphiques interactifs** : Tooltips au survol
- **Tableaux triables** : Cliquer sur les en-têtes de colonnes
- **Navigation fluide** : Menu latéral persistant

### Responsive Design
- **Adaptatif** : Fonctionne sur desktop et tablette
- **Scrollbars personnalisées** : Esthétique cohérente
- **Pagination** : Pour les grands tableaux

## 📱 Cas d'Usage Métier

### Pour le Directeur Général
- Vue d'ensemble immédiate de la performance
- KPI clés pour prise de décision rapide
- Tendances et alertes pour anticiper

### Pour le Commercial
- Performance personnelle vs équipe
- Segmentation clients pour ciblage
- Évolution du portefeuille

### Pour le Responsable Logistique
- État des stocks en temps réel
- Alertes pour gestion des approvisionnements
- Performance des livraisons

### Pour le Contrôle de Gestion
- Rentabilité par client/produit
- Suivi des marges et CA
- Analyse des coûts logistiques

## 🔧 Fonctionnalités Techniques

### Performance
- **Chargement asynchrone** des données
- **Mise en cache** côté serveur
- **Pagination** des grands volumes
- **Vues matérialisées** pour agrégations

### Données de Démonstration
- **5 clients** réalistes (hôtels, restaurants, écoles)
- **20 produits** variés (entretien, emballages, équipements)
- **8 commandes** avec statuts différents
- **KPI calculés** avec tendances comparatives

### Export et Impression
- **Export des données** (CSV, PDF) - prévu
- **Impression optimisée** des rapports
- **Mode plein écran** pour présentations

---

## 🚀 Pour voir le dashboard en réel

1. **Installer les prérequis** : PostgreSQL, Python, Node.js
2. **Lancer le setup** : `scripts\setup_database.bat`
3. **Démarrer l'ETL** : `scripts\run_etl.bat`  
4. **Lancer le dashboard** : `scripts\start_dashboard.bat`
5. **Ouvrir** : http://localhost:3000

Le dashboard est **100% fonctionnel** avec des données réalistes et des interactions fluides !
