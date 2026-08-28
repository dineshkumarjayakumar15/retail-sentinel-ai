import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { Navbar } from '../components/Navbar';

export const MainLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#070b14] flex text-slate-100 antialiased selection:bg-cyan-500/30 selection:text-cyan-200">
      <Sidebar />
      <div className="pl-64 flex-1 flex flex-col min-w-0">
        <Navbar />
        <main className="p-8 flex-1 max-w-7xl mx-auto w-full">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
