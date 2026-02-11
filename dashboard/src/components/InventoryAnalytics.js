import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Table, Tag, Progress, Select, Space } from 'antd';
import { Line, Column } from '@ant-design/plots';
import { inventoryService } from '../services/dashboardService';

const { Option } = Select;

const InventoryAnalytics = () => {
  const [inventoryStatus, setInventoryStatus] = useState({});
  const [stockMovements, setStockMovements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    warehouse: 'all',
    productFamily: 'all',
    period: '30days',
  });

  useEffect(() => {
    loadInventoryData();
  }, [filters]);

  const loadInventoryData = async () => {
    try {
      setLoading(true);
      const statusData = await inventoryService.getInventoryStatus();
      const movementsData = await inventoryService.getStockMovements(filters);
      
      setInventoryStatus(statusData);
      setStockMovements(movementsData);
    } catch (error) {
      console.error('Erreur lors du chargement des données de stocks:', error);
    } finally {
      setLoading(false);
    }
  };

  const stockEvolutionConfig = {
    data: [
      { date: '2025-01-01', valeur: 42500 },
      { date: '2025-01-05', valeur: 41800 },
      { date: '2025-01-10', valeur: 43200 },
      { date: '2025-01-15', valeur: 45600 },
      { date: '2025-01-20', valeur: 44200 },
      { date: '2025-01-25', valeur: 46800 },
      { date: '2025-01-30', valeur: 45600 },
    ],
    xField: 'date',
    yField: 'valeur',
    smooth: true,
    color: '#1890ff',
    point: {
      size: 5,
      shape: 'diamond',
    },
    tooltip: {
      formatter: (datum) => ({
        name: 'Valeur stock',
        value: `${datum.valeur.toLocaleString()} €`,
      }),
    },
  };

  const movementsConfig = {
    data: stockMovements.map(movement => ({
      ...movement,
      type: movement.type === 'entree' ? 'Entrée' : 'Sortie',
      quantite_abs: Math.abs(movement.quantite),
    })),
    xField: 'date',
    yField: 'quantite_abs',
    seriesField: 'type',
    color: ['#52c41a', '#ff4d4f'],
    columnWidthRatio: 0.8,
    meta: {
      quantite_abs: {
        alias: 'Quantité',
      },
    },
  };

  const inventoryColumns = [
    {
      title: 'Produit',
      dataIndex: 'produit',
      key: 'produit',
    },
    {
      title: 'Référence',
      dataIndex: 'reference',
      key: 'reference',
    },
    {
      title: 'Famille',
      dataIndex: 'famille',
      key: 'famille',
    },
    {
      title: 'Stock actuel',
      dataIndex: 'stock_actuel',
      key: 'stock_actuel',
      render: (value) => value.toLocaleString(),
    },
    {
      title: 'Seuil alerte',
      dataIndex: 'seuil_alerte',
      key: 'seuil_alerte',
      render: (value) => value.toLocaleString(),
    },
    {
      title: 'Statut',
      dataIndex: 'statut',
      key: 'statut',
      render: (status) => {
        const color = status === 'ALERTE' ? 'red' : status === 'SURSTOCK' ? 'orange' : 'green';
        return <Tag color={color}>{status}</Tag>;
      },
    },
    {
      title: 'Valeur stock',
      dataIndex: 'valeur_stock',
      key: 'valeur_stock',
      render: (value) => `${value.toLocaleString()} €`,
      sorter: (a, b) => a.valeur_stock - b.valeur_stock,
    },
  ];

  const movementsColumns = [
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
    },
    {
      title: 'Produit',
      dataIndex: 'produit',
      key: 'produit',
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type) => {
        const color = type === 'entree' ? 'green' : 'red';
        const text = type === 'entree' ? 'Entrée' : 'Sortie';
        return <Tag color={color}>{text}</Tag>;
      },
    },
    {
      title: 'Quantité',
      dataIndex: 'quantite',
      key: 'quantite',
      render: (value) => {
        const color = value > 0 ? 'green' : 'red';
        return <span style={{ color }}>{Math.abs(value).toLocaleString()}</span>;
      },
    },
    {
      title: 'Motif',
      dataIndex: 'motif',
      key: 'motif',
    },
  ];

  const mockInventoryData = [
    {
      key: 1,
      produit: 'Nettoyant Multi-Usage Écologique 1L',
      reference: 'PE001',
      famille: 'Produits d\'entretien',
      stock_actuel: 245,
      seuil_alerte: 20,
      statut: 'NORMAL',
      valeur_stock: 612.50,
    },
    {
      key: 2,
      produit: 'Savon Liquide Écologique 300ml',
      reference: 'PH001',
      famille: 'Produits d\'hygiène',
      stock_actuel: 45,
      seuil_alerte: 60,
      statut: 'ALERTE',
      valeur_stock: 81.00,
    },
    {
      key: 3,
      produit: 'Sachet Compostable 30x40cm',
      reference: 'EB001',
      famille: 'Emballages biodégradables',
      stock_actuel: 850,
      seuil_alerte: 100,
      statut: 'SURSTOCK',
      valeur_stock: 127.50,
    },
    {
      key: 4,
      produit: 'Gourde Inox 500ml',
      reference: 'ED001',
      famille: 'Équipements durables',
      stock_actuel: 78,
      seuil_alerte: 30,
      statut: 'NORMAL',
      valeur_stock: 429.00,
    },
    {
      key: 5,
      produit: 'Lessive Liquide Éco 5L',
      reference: 'PE002',
      famille: 'Produits d\'entretien',
      stock_actuel: 12,
      seuil_alerte: 15,
      statut: 'ALERTE',
      valeur_stock: 96.00,
    },
  ];

  return (
    <div>
      {/* Filtres */}
      <Card style={{ marginBottom: 24 }}>
        <Space size="large">
          <div>
            <label style={{ marginRight: 8 }}>Entrepôt:</label>
            <Select
              value={filters.warehouse}
              onChange={(value) => setFilters({ ...filters, warehouse: value })}
              style={{ width: 200 }}
            >
              <Option value="all">Tous les entrepôts</Option>
              <Option value="lyon">Entrepôt Lyon</Option>
              <Option value="marseille">Entrepôt Marseille</Option>
              <Option value="lille">Entrepôt Lille</Option>
            </Select>
          </div>
          <div>
            <label style={{ marginRight: 8 }}>Famille produit:</label>
            <Select
              value={filters.productFamily}
              onChange={(value) => setFilters({ ...filters, productFamily: value })}
              style={{ width: 200 }}
            >
              <Option value="all">Toutes les familles</Option>
              <Option value="entretien">Produits d'entretien</Option>
              <Option value="emballages">Emballages biodégradables</Option>
              <Option value="equipements">Équipements durables</Option>
              <Option value="hygiene">Produits d'hygiène</Option>
            </Select>
          </div>
          <div>
            <label style={{ marginRight: 8 }}>Période:</label>
            <Select
              value={filters.period}
              onChange={(value) => setFilters({ ...filters, period: value })}
              style={{ width: 150 }}
            >
              <Option value="7days">7 derniers jours</Option>
              <Option value="30days">30 derniers jours</Option>
              <Option value="90days">90 derniers jours</Option>
            </Select>
          </div>
        </Space>
      </Card>

      {/* KPI Stocks */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>
                {inventoryStatus.totalProducts || 20}
              </div>
              <div>Produits référencés</div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#ff4d4f' }}>
                {inventoryStatus.alertProducts || 3}
              </div>
              <div>Produits en alerte</div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#fa8c16' }}>
                {inventoryStatus.overstockProducts || 2}
              </div>
              <div>Produits en surstock</div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="circle"
                percent={inventoryStatus.turnoverRate || 78}
                size={80}
                format={(percent) => `${percent}%`}
              />
              <div style={{ marginTop: 8 }}>Taux rotation</div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Graphiques */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card title="Évolution de la valeur des stocks" loading={loading}>
            <Line {...stockEvolutionConfig} height={300} />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Mouvements récents" loading={loading}>
            <Column {...movementsConfig} height={300} />
          </Card>
        </Col>
      </Row>

      {/* Tableaux détaillés */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={14}>
          <Card title="État des stocks par produit" loading={loading}>
            <Table
              columns={inventoryColumns}
              dataSource={mockInventoryData}
              pagination={{ pageSize: 10 }}
              size="small"
              scroll={{ y: 400 }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="Mouvements de stocks récents" loading={loading}>
            <Table
              columns={movementsColumns}
              dataSource={stockMovements}
              pagination={{ pageSize: 10 }}
              size="small"
              scroll={{ y: 400 }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default InventoryAnalytics;
