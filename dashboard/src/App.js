import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, Menu, theme } from 'antd';
import {
  DashboardOutlined,
  BarChartOutlined,
  PieChartOutlined,
  LineChartOutlined,
  SettingOutlined
} from '@ant-design/icons';
import Dashboard from './components/Dashboard';
import SalesAnalytics from './components/SalesAnalytics';
import InventoryAnalytics from './components/InventoryAnalytics';
import CustomerAnalytics from './components/CustomerAnalytics';
import './App.css';

const { Header, Sider, Content } = Layout;

function App() {
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Tableau de bord',
    },
    {
      key: '/sales',
      icon: <BarChartOutlined />,
      label: 'Analyse des ventes',
    },
    {
      key: '/inventory',
      icon: <PieChartOutlined />,
      label: 'Gestion des stocks',
    },
    {
      key: '/customers',
      icon: <LineChartOutlined />,
      label: 'Analyse clients',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Paramètres',
    },
  ];

  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider
          theme="light"
          width={250}
          style={{
            position: 'fixed',
            height: '100vh',
            left: 0,
            top: 0,
            bottom: 0,
          }}
        >
          <div className="logo">
            <h2>EcoDistribution</h2>
            <p>Tableau de bord décisionnel</p>
          </div>
          <Menu
            theme="light"
            mode="inline"
            defaultSelectedKeys={['/']}
            items={menuItems}
            onClick={({ key }) => {
              window.location.pathname = key;
            }}
          />
        </Sider>
        <Layout style={{ marginLeft: 250 }}>
          <Header style={{ padding: 0, background: colorBgContainer }}>
            <div style={{ 
              padding: '0 24px', 
              fontSize: '18px', 
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              height: '100%'
            }}>
              Plateforme Décisionnelle
            </div>
          </Header>
          <Content style={{ margin: '24px 16px 0', overflow: 'initial' }}>
            <div
              style={{
                padding: 24,
                minHeight: 360,
                background: colorBgContainer,
                borderRadius: 8,
              }}
            >
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/sales" element={<SalesAnalytics />} />
                <Route path="/inventory" element={<InventoryAnalytics />} />
                <Route path="/customers" element={<CustomerAnalytics />} />
              </Routes>
            </div>
          </Content>
        </Layout>
      </Layout>
    </Router>
  );
}

export default App;
