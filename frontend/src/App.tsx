import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from './layouts/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { AlertsList } from './pages/AlertsList';
import { AlertDetail } from './pages/AlertDetail';
import { CustomerDetail } from './pages/CustomerDetail';
import { Analytics } from './pages/Analytics';
import { Videos } from './pages/Videos';
import { VideoDetail } from './pages/VideoDetail';
import { Settings } from './pages/Settings';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="alerts" element={<AlertsList />} />
          <Route path="alerts/:id" element={<AlertDetail />} />
          <Route path="customers/:id" element={<CustomerDetail />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="videos" element={<Videos />} />
          <Route path="videos/:id" element={<VideoDetail />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
