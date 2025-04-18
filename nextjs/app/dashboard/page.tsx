'use client'; // May need client-side interactions later

import React from 'react';

// Mock data for dashboard summary
const mockAccountSummary = {
  totalValue: 125380.50, // Example: Sum of current holdings value + cash (cash part omitted for simplicity now)
  todayPL: 850.75,
  totalPL: 12880.25,
  buyingPower: 50000.00, // Example simulated cash available
};

// Mock user data
const mockUser = {
  name: '陳大文 (Demo User)',
  email: 'demo@example.com',
  memberSince: '2024-01-01',
};

// Helper to format currency
const formatCurrency = (value: number) => {
  return value.toLocaleString('zh-HK', { style: 'currency', currency: 'HKD' });
};

// Helper to get P/L color
const getPlColor = (pl: number) => {
  if (pl > 0) return 'text-green-600';
  if (pl < 0) return 'text-red-600';
  return 'text-gray-700';
};

export default function DashboardPage() {
  // Use mock data directly for now
  const summary = mockAccountSummary;
  const user = mockUser;

  return (
    <div className="container mx-auto p-4 space-y-8">
      <h1 className="text-3xl font-bold border-b pb-2">我的帳戶 Dashboard</h1>

      {/* Account Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-sm font-medium text-gray-500 mb-1">模擬總資產</h3>
          <p className="text-2xl font-bold text-blue-600">{formatCurrency(summary.totalValue)}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-sm font-medium text-gray-500 mb-1">今日盈虧 (模擬)</h3>
          <p className={`text-2xl font-bold ${getPlColor(summary.todayPL)}`}>
            {summary.todayPL >= 0 ? '+' : ''}{formatCurrency(summary.todayPL)}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-sm font-medium text-gray-500 mb-1">總盈虧 (模擬)</h3>
           <p className={`text-2xl font-bold ${getPlColor(summary.totalPL)}`}>
             {summary.totalPL >= 0 ? '+' : ''}{formatCurrency(summary.totalPL)}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-sm font-medium text-gray-500 mb-1">購買力 (模擬)</h3>
          <p className="text-2xl font-bold">{formatCurrency(summary.buyingPower)}</p>
        </div>
      </div>

      {/* User Info Section */}
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h2 className="text-xl font-semibold mb-4 text-gray-800">用戶資訊</h2>
        <div className="space-y-2 text-sm">
          <p><strong>用戶名稱:</strong> {user.name}</p>
          <p><strong>電郵地址:</strong> {user.email}</p>
          <p><strong>註冊日期:</strong> {new Date(user.memberSince).toLocaleDateString('zh-HK')}</p>
          {/* Add link to profile settings page later */}
          {/* <button className="mt-3 text-sm text-blue-600 hover:underline">編輯個人資料</button> */} 
        </div>
      </div>

      {/* Placeholder for recent activity or other widgets */}
      {/* 
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h2 className="text-xl font-semibold mb-4 text-gray-800">最近活動</h2>
        <p className="text-gray-500">此處顯示最近的交易或策略信號...</p>
      </div>
      */}

    </div>
  );
} 