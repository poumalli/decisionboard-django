import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Table, Select, DatePicker, Space } from 'antd';
import { Line, Column, Pie } from '@ant-design/plots';
import { salesService } from '../services/dashboardService';

const { RangePicker } = DatePicker;
const { Option } = Select;

const SalesAnalytics = () => {
  const [salesData, setSalesData] = useState({});
  const [commercialPerformance, setCommercialPerformance] = useState([]);
  const [salesBySegment, setSalesBySegment] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    period: '6months',
    region: 'all',
    segment: 'all',
  });

  useEffect(() => {
    loadSalesData();
  }, [filters]);

  const loadSalesData = async () => {
    try {
      setLoading(true);
      const data = await salesService.getSalesData(filters);
      const commercialData = await salesService.getCommercialPerformance();
      const segmentData = await salesService.getSalesBySegment();
      
      setSalesData(data);
      setCommercialPerformance(commercialData);
      setSalesBySegment(segmentData);
    } catch (error) {
      console.error('Erreur lors du chargement des données de ventes:', error);
    } finally {
      setLoading(false);
    }
  };

  const salesEvolutionConfig = {
    data: salesData.monthlySales || [],
    xField: 'periode',
    yField: 'ca',
    smooth: true,
    color: '#1890ff',
    point: {
      size: 5,
      shape: 'diamond',
    },
    tooltip: {
      formatter: (datum) => ({
        name: 'CA HT',
        value: `${datum.ca.toLocaleString()} €`,
      }),
    },
  };

  const regionSalesConfig = {
    data: salesData.salesByRegion || [],
    xField: 'region',
    yField: 'ca',
    color: '#52c41a',
    columnWidthRatio: 0.8,
    meta: {
      ca: {
        alias: 'CA HT (€)',
        formatter: (v) => `${v.toLocaleString()} €`,
      },
    },
  };

  const segmentConfig = {
    data: salesBySegment,
    angleField: 'ca',
    colorField: 'segment',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name} {percentage}',
    },
    interactions: [{ type: 'element-active' }],
  };

  const productColumns = [
    {
      title: 'Produit',
      dataIndex: 'produit',
      key: 'produit',
    },
    {
      title: 'Quantité vendue',
      dataIndex: 'quantite',
      key: 'quantite',
      render: (value) => value.toLocaleString(),
    },
    {
      title: 'CA HT',
      dataIndex: 'ca',
      key: 'ca',
      render: (value) => `${value.toLocaleString()} €`,
    },
    {
      title: 'Prix moyen',
      key: 'prix_moyen',
      render: (_, record) => `${(record.ca / record.quantite).toFixed(2)} €`,
    },
  ];

  const commercialColumns = [
    {
      title: 'Commercial',
      dataIndex: 'commercial',
      key: 'commercial',
    },
    {
      title: 'CA HT',
      dataIndex: 'ca',
      key: 'ca',
      render: (value) => `${value.toLocaleString()} €`,
      sorter: (a, b) => a.ca - b.ca,
    },
    {
      title: 'Marge HT',
      dataIndex: 'marge',
      key: 'marge',
      render: (value) => `${value.toLocaleString()} €`,
      sorter: (a, b) => a.marge - b.marge,
    },
    {
      title: 'Taux marge',
      key: 'taux_marge',
      render: (_, record) => `${((record.marge / record.ca) * 100).toFixed(1)}%`,
      sorter: (a, b) => (a.marge / a.ca) - (b.marge / b.ca),
    },
    {
      title: 'Commandes',
      dataIndex: 'commandes',
      key: 'commandes',
      sorter: (a, b) => a.commandes - b.commandes,
    },
    {
      title: 'Panier moyen',
      key: 'panier_moyen',
      render: (_, record) => `${(record.ca / record.commandes).toFixed(2)} €`,
    },
  ];

  return (
    <div>
      {/* Filtres */}
      <Card style={{ marginBottom: 24 }}>
        <Space size="large">
          <div>
            <label style={{ marginRight: 8 }}>Période:</label>
            <Select
              value={filters.period}
              onChange={(value) => setFilters({ ...filters, period: value })}
              style={{ width: 150 }}
            >
              <Option value="3months">3 derniers mois</Option>
              <Option value="6months">6 derniers mois</Option>
              <Option value="1year">Dernière année</Option>
            </Select>
          </div>
          <div>
            <label style={{ marginRight: 8 }}>Région:</label>
            <Select
              value={filters.region}
              onChange={(value) => setFilters({ ...filters, region: value })}
              style={{ width: 200 }}
            >
              <Option value="all">Toutes les régions</Option>
              <Option value="auvergne-rhone-alpes">Auvergne-Rhône-Alpes</Option>
              <Option value="paca">Provence-Alpes-Côte d'Azur</Option>
              <Option value="hauts-de-france">Hauts-de-France</Option>
            </Select>
          </div>
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
        </Space>
      </Card>

      {/* Graphiques principaux */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card title="Évolution des ventes" loading={loading}>
            <Line {...salesEvolutionConfig} height={350} />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Ventes par segment client" loading={loading}>
            <Pie {...segmentConfig} height={350} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24}>
          <Card title="Ventes par région" loading={loading}>
            <Column {...regionSalesConfig} height={300} />
          </Card>
        </Col>
      </Row>

      {/* Tableaux détaillés */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Top produits" loading={loading}>
            <Table
              columns={productColumns}
              dataSource={salesData.productSales || []}
              pagination={false}
              size="small"
              scroll={{ y: 400 }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Performance des commerciaux" loading={loading}>
            <Table
              columns={commercialColumns}
              dataSource={commercialPerformance}
              pagination={false}
              size="small"
              scroll={{ y: 400 }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SalesAnalytics;
