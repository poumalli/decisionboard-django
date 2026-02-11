import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Table, Progress, Select, Space } from 'antd';
import { Line, Column, Pie } from '@ant-design/plots';
import { customerService } from '../services/dashboardService';

const { Option } = Select;

const CustomerAnalytics = () => {
  const [customerProfitability, setCustomerProfitability] = useState([]);
  const [customerEvolution, setCustomerEvolution] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    segment: 'all',
    period: '12months',
  });

  useEffect(() => {
    loadCustomerData();
  }, [filters]);

  const loadCustomerData = async () => {
    try {
      setLoading(true);
      const profitabilityData = await customerService.getCustomerProfitability();
      const evolutionData = await customerService.getCustomerEvolution();
      
      setCustomerProfitability(profitabilityData);
      setCustomerEvolution(evolutionData);
    } catch (error) {
      console.error('Erreur lors du chargement des données clients:', error);
    } finally {
      setLoading(false);
    }
  };

  const evolutionConfig = {
    data: customerEvolution,
    xField: 'mois',
    yField: 'actifs',
    smooth: true,
    color: '#1890ff',
    point: {
      size: 5,
      shape: 'diamond',
    },
    tooltip: {
      formatter: (datum) => ({
        name: 'Clients actifs',
        value: datum.actifs,
      }),
    },
  };

  const newCustomersConfig = {
    data: customerEvolution,
    xField: 'mois',
    yField: 'nouveaux',
    color: '#52c41a',
    columnWidthRatio: 0.8,
    meta: {
      nouveaux: {
        alias: 'Nouveaux clients',
      },
    },
  };

  const segmentDistributionConfig = {
    data: [
      { segment: 'Grands comptes', nombre: 5, ca: 58900 },
      { segment: 'Comptes moyens', nombre: 15, ca: 45600 },
      { segment: 'Petits comptes', nombre: 25, ca: 20950 },
    ],
    angleField: 'nombre',
    colorField: 'segment',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name} {percentage}',
    },
    interactions: [{ type: 'element-active' }],
  };

  const profitabilityColumns = [
    {
      title: 'Client',
      dataIndex: 'client',
      key: 'client',
      fixed: 'left',
      width: 200,
    },
    {
      title: 'CA HT',
      dataIndex: 'ca',
      key: 'ca',
      render: (value) => `${value.toLocaleString()} €`,
      sorter: (a, b) => a.ca - b.ca,
      width: 120,
    },
    {
      title: 'Marge HT',
      dataIndex: 'marge',
      key: 'marge',
      render: (value) => `${value.toLocaleString()} €`,
      sorter: (a, b) => a.marge - b.marge,
      width: 120,
    },
    {
      title: 'Rentabilité',
      dataIndex: 'rentabilite',
      key: 'rentabilite',
      render: (value) => (
        <Progress
          percent={parseFloat(value)}
          size="small"
          status={value >= 25 ? 'success' : value >= 15 ? 'normal' : 'exception'}
          format={() => `${value}%`}
        />
      ),
      sorter: (a, b) => a.rentabilite - b.rentabilite,
      width: 150,
    },
    {
      title: 'Segment',
      key: 'segment',
      render: (_, record) => {
        if (record.ca >= 40000) return 'Grand compte';
        if (record.ca >= 20000) return 'Compte moyen';
        return 'Petit compte';
      },
      width: 120,
    },
    {
      title: 'Rang',
      key: 'rang',
      render: (_, record, index) => index + 1,
      width: 80,
    },
  ];

  const detailedColumns = [
    {
      title: 'Client',
      dataIndex: 'client',
      key: 'client',
    },
    {
      title: 'Secteur',
      dataIndex: 'secteur',
      key: 'secteur',
    },
    {
      title: 'Taille',
      dataIndex: 'taille',
      key: 'taille',
    },
    {
      title: 'Nombre commandes',
      dataIndex: 'commandes',
      key: 'commandes',
      render: (value) => value.toLocaleString(),
    },
    {
      title: 'Panier moyen',
      dataIndex: 'panier_moyen',
      key: 'panier_moyen',
      render: (value) => `${value.toFixed(2)} €`,
    },
    {
      title: 'Délai paiement',
      dataIndex: 'delai_paiement',
      key: 'delai_paiement',
      render: (value) => `${value} jours`,
    },
    {
      title: 'Statut',
      dataIndex: 'statut',
      key: 'statut',
      render: (status) => {
        const color = status === 'actif' ? 'green' : 'red';
        return <span style={{ color }}>{status.toUpperCase()}</span>;
      },
    },
  ];

  const mockDetailedData = [
    {
      key: 1,
      client: 'Supermarché BioStore',
      secteur: 'Grande distribution',
      taille: 'ETI',
      commandes: 12,
      panier_moyen: 3825.00,
      delai_paiement: 45,
      statut: 'actif',
    },
    {
      key: 2,
      client: 'Hôtel Les Oliviers',
      secteur: 'Hôtellerie',
      taille: 'PME',
      commandes: 8,
      panier_moyen: 2925.00,
      delai_paiement: 30,
      statut: 'actif',
    },
    {
      key: 3,
      client: 'Bureau Conseil Alpha',
      secteur: 'Services',
      taille: 'PME',
      commandes: 6,
      panier_moyen: 3150.00,
      delai_paiement: 30,
      statut: 'actif',
    },
    {
      key: 4,
      client: 'Restaurant Le Gourmet',
      secteur: 'Restauration',
      taille: 'TPE',
      commandes: 4,
      panier_moyen: 1875.00,
      delai_paiement: 30,
      statut: 'actif',
    },
    {
      key: 5,
      client: 'École Primaire Verte',
      secteur: 'Éducation',
      taille: 'TPE',
      commandes: 3,
      panier_moyen: 1250.00,
      delai_paiement: 45,
      statut: 'actif',
    },
  ];

  return (
    <div>
      {/* Filtres */}
      <Card style={{ marginBottom: 24 }}>
        <Space size="large">
          <div>
            <label style={{ marginRight: 8 }}>Segment:</label>
            <Select
              value={filters.segment}
              onChange={(value) => setFilters({ ...filters, segment: value })}
              style={{ width: 150 }}
            >
              <Option value="all">Tous les segments</Option>
              <Option value="grands-comptes">Grands comptes</Option>
              <Option value="comptes-moyens">Comptes moyens</Option>
              <Option value="petits-comptes">Petits comptes</Option>
            </Select>
          </div>
          <div>
            <label style={{ marginRight: 8 }}>Période:</label>
            <Select
              value={filters.period}
              onChange={(value) => setFilters({ ...filters, period: value })}
              style={{ width: 150 }}
            >
              <Option value="6months">6 derniers mois</Option>
              <Option value="12months">Dernière année</Option>
              <Option value="24months">2 dernières années</Option>
            </Select>
          </div>
        </Space>
      </Card>

      {/* KPI Clients */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>
                45
              </div>
              <div>Clients actifs</div>
              <div style={{ fontSize: 12, color: '#52c41a', marginTop: 4 }}>
                +5.7% vs mois dernier
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#52c41a' }}>
                3
              </div>
              <div>Nouveaux clients (mois)</div>
              <div style={{ fontSize: 12, color: '#52c41a', marginTop: 4 }}>
                +25% vs moyenne
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                24.8%
              </div>
              <div>Rentabilité moyenne</div>
              <div style={{ fontSize: 12, color: '#cf1322', marginTop: 4 }}>
                -1.2% vs mois dernier
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#fa8c16' }}>
                38
              </div>
              <div>Panier moyen (€)</div>
              <div style={{ fontSize: 12, color: '#52c41a', marginTop: 4 }}>
                +8.3% vs mois dernier
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Graphiques */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Évolution des clients actifs" loading={loading}>
            <Line {...evolutionConfig} height={300} />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Nouveaux clients par mois" loading={loading}>
            <Column {...newCustomersConfig} height={300} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={8}>
          <Card title="Distribution par segment" loading={loading}>
            <Pie {...segmentDistributionConfig} height={300} />
          </Card>
        </Col>
        <Col xs={24} lg={16}>
          <Card title="Top clients rentabilité" loading={loading}>
            <Table
              columns={profitabilityColumns}
              dataSource={customerProfitability}
              pagination={false}
              size="small"
              scroll={{ x: 800, y: 300 }}
            />
          </Card>
        </Col>
      </Row>

      {/* Tableau détaillé */}
      <Row gutter={[16, 16]}>
        <Col xs={24}>
          <Card title="Détail des clients" loading={loading}>
            <Table
              columns={detailedColumns}
              dataSource={mockDetailedData}
              pagination={{ pageSize: 10 }}
              scroll={{ x: 800 }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default CustomerAnalytics;
