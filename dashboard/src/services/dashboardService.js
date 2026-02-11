import axios from 'axios';

// Configuration de base pour les requêtes API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Service pour le tableau de bord principal
export const dashboardService = {
  // Récupérer toutes les données du dashboard
  getDashboardData: async () => {
    try {
      const response = await api.get('/dashboard');
      return response.data;
    } catch (error) {
      // En cas d'erreur, retourner des données de démonstration
      console.warn('Utilisation des données de démonstration');
      return getMockDashboardData();
    }
  },

  // Récupérer les KPI principaux
  getKPIs: async () => {
    try {
      const response = await api.get('/dashboard/kpis');
      return response.data;
    } catch (error) {
      return getMockKPIs();
    }
  },

  // Récupérer l'évolution des ventes
  getSalesEvolution: async (period = '6months') => {
    try {
      const response = await api.get(`/dashboard/sales-evolution?period=${period}`);
      return response.data;
    } catch (error) {
      return getMockSalesEvolution();
    }
  },

  // Récupérer les alertes de stock
  getStockAlerts: async () => {
    try {
      const response = await api.get('/dashboard/stock-alerts');
      return response.data;
    } catch (error) {
      return getMockStockAlerts();
    }
  },
};

// Service pour les analytics de ventes
export const salesService = {
  // Récupérer les données de ventes détaillées
  getSalesData: async (filters = {}) => {
    try {
      const response = await api.get('/sales', { params: filters });
      return response.data;
    } catch (error) {
      return getMockSalesData();
    }
  },

  // Récupérer la performance par commercial
  getCommercialPerformance: async () => {
    try {
      const response = await api.get('/sales/commercial-performance');
      return response.data;
    } catch (error) {
      return getMockCommercialPerformance();
    }
  },

  // Récupérer les ventes par segment client
  getSalesBySegment: async () => {
    try {
      const response = await api.get('/sales/by-segment');
      return response.data;
    } catch (error) {
      return getMockSalesBySegment();
    }
  },
};

// Service pour les analytics de stocks
export const inventoryService = {
  // Récupérer l'état des stocks
  getInventoryStatus: async () => {
    try {
      const response = await api.get('/inventory/status');
      return response.data;
    } catch (error) {
      return getMockInventoryStatus();
    }
  },

  // Récupérer les mouvements de stocks
  getStockMovements: async (filters = {}) => {
    try {
      const response = await api.get('/inventory/movements', { params: filters });
      return response.data;
    } catch (error) {
      return getMockStockMovements();
    }
  },
};

// Service pour les analytics clients
export const customerService = {
  // Récupérer la rentabilité par client
  getCustomerProfitability: async () => {
    try {
      const response = await api.get('/customers/profitability');
      return response.data;
    } catch (error) {
      return getMockCustomerProfitability();
    }
  },

  // Récupérer l'évolution du portefeuille clients
  getCustomerEvolution: async () => {
    try {
      const response = await api.get('/customers/evolution');
      return response.data;
    } catch (error) {
      return getMockCustomerEvolution();
    }
  },
};

// ===== DONNÉES DE DÉMONSTRATION =====
// Ces données sont utilisées lorsque l'API n'est pas disponible

const getMockDashboardData = () => ({
  kpi: getMockKPIs(),
  salesEvolution: getMockSalesEvolution(),
  topProducts: [
    { libelle: 'Nettoyant Multi-Usage', ca_ht: 15420 },
    { libelle: 'Lessive Liquide Éco', ca_ht: 12350 },
    { libelle: 'Sachet Compostable', ca_ht: 10890 },
    { libelle: 'Gourde Inox', ca_ht: 9870 },
    { libelle: 'Savon Liquide Éco', ca_ht: 8650 },
  ],
  stockAlerts: getMockStockAlerts(),
});

const getMockKPIs = () => ({
  ca_ht: 125450.50,
  marge_brute: 28950.75,
  nombre_commandes: 156,
  nombre_clients_actifs: 45,
});

const getMockSalesEvolution = () => [
  { periode: '2024-08', ca_ht: 98500 },
  { periode: '2024-09', ca_ht: 102300 },
  { periode: '2024-10', ca_ht: 118900 },
  { periode: '2024-11', ca_ht: 115600 },
  { periode: '2024-12', ca_ht: 142300 },
  { periode: '2025-01', ca_ht: 125450 },
];

const getMockStockAlerts = () => [
  {
    key: 1,
    libelle: 'Savon Liquide Écologique 300ml',
    entrepot_nom: 'Entrepôt Lyon',
    stock_actuel: 45,
    statut_stock: 'ALERTE',
  },
  {
    key: 2,
    libelle: 'Boîte Conservation Verre 1L',
    entrepot_nom: 'Entrepôt Marseille',
    stock_actuel: 8,
    statut_stock: 'ALERTE',
  },
  {
    key: 3,
    libelle: 'Sachet Compostable 30x40cm',
    entrepot_nom: 'Entrepôt Lille',
    stock_actuel: 850,
    statut_stock: 'SURSTOCK',
  },
];

const getMockSalesData = () => ({
  monthlySales: getMockSalesEvolution(),
  productSales: [
    { produit: 'Nettoyant Multi-Usage', quantite: 245, ca: 10290 },
    { produit: 'Lessive Liquide Éco', quantite: 189, ca: 8750 },
    { produit: 'Sachet Compostable', quantite: 567, ca: 7890 },
  ],
  salesByRegion: [
    { region: 'Auvergne-Rhône-Alpes', ca: 45600 },
    { region: 'Provence-Alpes-Côte d\'Azur', ca: 38900 },
    { region: 'Hauts-de-France', ca: 28950 },
  ],
});

const getMockCommercialPerformance = () => [
  { commercial: 'Sophie Durand', ca: 45600, marge: 12450, commandes: 45 },
  { commercial: 'Thomas Bernard', ca: 38900, marge: 9870, commandes: 38 },
  { commercial: 'Claire Petit', ca: 28950, marge: 6230, commandes: 28 },
];

const getMockSalesBySegment = () => [
  { segment: 'Grands comptes', ca: 58900, pourcentage: 47 },
  { segment: 'Comptes moyens', ca: 45600, pourcentage: 36 },
  { segment: 'Petits comptes', ca: 20950, pourcentage: 17 },
];

const getMockInventoryStatus = () => ({
  totalProducts: 20,
  alertProducts: 3,
  overstockProducts: 2,
  totalValue: 45600.50,
  turnoverRate: 78,
});

const getMockStockMovements = () => [
  { date: '2025-01-15', produit: 'Nettoyant Multi-Usage', type: 'sortie', quantite: 50 },
  { date: '2025-01-14', produit: 'Lessive Liquide Éco', type: 'entree', quantite: 200 },
  { date: '2025-01-13', produit: 'Sachet Compostable', type: 'sortie', quantite: 150 },
];

const getMockCustomerProfitability = () => [
  { client: 'Supermarché BioStore', ca: 45600, marge: 12450, rentabilite: 27.3 },
  { client: 'Hôtel Les Oliviers', ca: 23400, marge: 6780, rentabilite: 28.9 },
  { client: 'Bureau Conseil Alpha', ca: 18900, marge: 4560, rentabilite: 24.1 },
];

const getMockCustomerEvolution = () => [
  { mois: '2024-08', nouveaux: 3, actifs: 38 },
  { mois: '2024-09', nouveaux: 5, actifs: 41 },
  { mois: '2024-10', nouveaux: 2, actifs: 43 },
  { mois: '2024-11', nouveaux: 4, actifs: 45 },
  { mois: '2024-12', nouveaux: 6, actifs: 47 },
  { mois: '2025-01', nouveaux: 3, actifs: 45 },
];

export default api;
