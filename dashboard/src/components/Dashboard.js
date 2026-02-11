import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Progress, Table, Tag } from 'antd';
import { 
  DollarOutlined, 
  ShoppingCartOutlined, 
  UserOutlined, 
  AlertOutlined,
  TrendingUpOutlined,
  TrendingDownOutlined
} from '@ant-design/icons';
import { Line, Column, Pie } from '@ant-design/plots';
import { dashboardService } from '../services/dashboardService';

const Dashboard = () => {
  const [kpiData, setKpiData] = useState({});
  const [salesData, setSalesData] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [stockAlerts, setStockAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const data = await dashboardService.getDashboardData();
      setKpiData(data.kpi);
      setSalesData(data.salesEvolution);
      setTopProducts(data.topProducts);
      setStockAlerts(data.stockAlerts);
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
    } finally {
      setLoading(false);
    }
  };

  const salesConfig = {
    data: salesData,
    xField: 'periode',
    yField: 'ca_ht',
    smooth: true,
    color: '#1890ff',
    point: {
      size: 5,
      shape: 'diamond',
    },
    tooltip: {
      formatter: (datum) => ({
        name: 'CA HT',
        value: `${datum.ca_ht.toLocaleString()} €`,
      }),
    },
  };

  const productConfig = {
    data: topProducts,
    angleField: 'ca_ht',
    colorField: 'libelle',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name} {percentage}',
    },
    interactions: [{ type: 'element-active' }],
  };

  const stockColumns = [
    {
      title: 'Produit',
      dataIndex: 'libelle',
      key: 'libelle',
    },
    {
      title: 'Entrepôt',
      dataIndex: 'entrepot_nom',
      key: 'entrepot_nom',
    },
    {
      title: 'Stock actuel',
      dataIndex: 'stock_actuel',
      key: 'stock_actuel',
      render: (value) => value.toLocaleString(),
    },
    {
      title: 'Statut',
      dataIndex: 'statut_stock',
      key: 'statut_stock',
      render: (status) => (
        <Tag color={status === 'ALERTE' ? 'red' : status === 'SURSTOCK' ? 'orange' : 'green'}>
          {status}
        </Tag>
      ),
    },
  ];

  return (
    <div>
      {/* KPI Principaux */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Chiffre d'affaires HT"
              value={kpiData.ca_ht || 0}
              prefix={<DollarOutlined />}
              suffix="€"
              precision={2}
              valueStyle={{ color: '#3f8600' }}
            />
            <div style={{ marginTop: 8 }}>
              <TrendingUpOutlined style={{ color: '#3f8600' }} /> +12.5% vs mois dernier
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Marge brute"
              value={kpiData.marge_brute || 0}
              prefix={<DollarOutlined />}
              suffix="€"
              precision={2}
              valueStyle={{ color: '#3f8600' }}
            />
            <div style={{ marginTop: 8 }}>
              <TrendingUpOutlined style={{ color: '#3f8600' }} /> +8.3% vs mois dernier
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Commandes"
              value={kpiData.nombre_commandes || 0}
              prefix={<ShoppingCartOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ marginTop: 8 }}>
              <TrendingDownOutlined style={{ color: '#cf1322' }} /> -2.1% vs mois dernier
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Clients actifs"
              value={kpiData.nombre_clients_actifs || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
            <div style={{ marginTop: 8 }}>
              <TrendingUpOutlined style={{ color: '#3f8600' }} /> +5.7% vs mois dernier
            </div>
          </Card>
        </Col>
      </Row>

      {/* Graphiques */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card title="Évolution des ventes (6 derniers mois)" loading={loading}>
            <Line {...salesConfig} height={300} />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Top 5 produits" loading={loading}>
            <Pie {...productConfig} height={300} />
          </Card>
        </Col>
      </Row>

      {/* Alertes stocks et indicateurs */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card 
            title={
              <span>
                <AlertOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
                Alertes stocks
              </span>
            } 
            loading={loading}
          >
            <Table
              columns={stockColumns}
              dataSource={stockAlerts}
              pagination={false}
              size="small"
              scroll={{ y: 300 }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Indicateurs de performance" loading={loading}>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <div style={{ textAlign: 'center' }}>
                  <Progress
                    type="circle"
                    percent={95}
                    format={() => '95%'}
                    strokeColor="#52c41a"
                  />
                  <div style={{ marginTop: 8 }}>Taux de service client</div>
                </div>
              </Col>
              <Col span={12}>
                <div style={{ textAlign: 'center' }}>
                  <Progress
                    type="circle"
                    percent={78}
                    format={() => '78%'}
                    strokeColor="#1890ff"
                  />
                  <div style={{ marginTop: 8 }}>Taux de rotation stocks</div>
                </div>
              </Col>
              <Col span={12} style={{ marginTop: 16 }}>
                <div style={{ textAlign: 'center' }}>
                  <Progress
                    type="circle"
                    percent={23.5}
                    format={() => '23.5%'}
                    strokeColor="#722ed1"
                  />
                  <div style={{ marginTop: 8 }}>Marge moyenne</div>
                </div>
              </Col>
              <Col span={12} style={{ marginTop: 16 }}>
                <div style={{ textAlign: 'center' }}>
                  <Progress
                    type="circle"
                    percent={89}
                    format={() => '89%'}
                    strokeColor="#fa8c16"
                  />
                  <div style={{ marginTop: 8 }}>Livraisons ponctuelles</div>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
