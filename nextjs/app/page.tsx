'use client'; // Home page might have dynamic elements later

import React from 'react';
import Link from 'next/link'; // Import Link for navigation

// Mock data for market snapshot
const mockMarketSnapshot = {
  hsiValue: 17650.25,
  changePercent: 0.45,
  volumeBillion: 115.5,
};

// Helper to format currency (simplified for index points)
const formatIndexValue = (value: number) => {
  return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

// Helper to get change color
const getChangeColor = (change: number) => {
  if (change > 0) return 'text-green-600';
  if (change < 0) return 'text-red-600';
  return 'text-gray-700';
};

export default function HomePage() {
  const snapshot = mockMarketSnapshot;

  return (
    <div className="container mx-auto p-4 space-y-8">
      <h1 className="text-3xl font-bold border-b pb-2">首頁 Home</h1>

      {/* Welcome Message */}
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h2 className="text-xl font-semibold mb-2 text-gray-800">歡迎使用 HSI Strategy App</h2>
        <p className="text-gray-600">
          本平台旨在提供恆生指數的策略分析工具，助您洞察市場趨勢。探索市場總覽、技術分析、策略信號等功能。
        </p>
      </div>

      {/* Market Snapshot Cards */}
      <div>
        <h2 className="text-2xl font-semibold mb-4 text-gray-700">即市快照 (模擬)</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
            <h3 className="text-sm font-medium text-gray-500 mb-1">恆生指數</h3>
            <p className="text-2xl font-bold text-blue-600">{formatIndexValue(snapshot.hsiValue)}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
            <h3 className="text-sm font-medium text-gray-500 mb-1">漲跌幅</h3>
            <p className={`text-2xl font-bold ${getChangeColor(snapshot.changePercent)}`}>
              {snapshot.changePercent >= 0 ? '+' : ''}{snapshot.changePercent.toFixed(2)}%
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
            <h3 className="text-sm font-medium text-gray-500 mb-1">成交額 (十億)</h3>
            <p className="text-2xl font-bold">{snapshot.volumeBillion.toFixed(1)} B</p>
          </div>
        </div>
      </div>

      {/* Quick Links / Call to Action */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
         <div className="bg-blue-50 p-6 rounded-lg border border-blue-200 hover:shadow-lg transition-shadow">
           <h3 className="text-lg font-semibold text-blue-800 mb-2">探索市場</h3>
           <p className="text-sm text-blue-700 mb-3">查看詳細的市場總覽和技術指標分析。</p>
           <Link href="/market-overview" className="text-sm font-medium text-blue-600 hover:underline">
             前往市場總覽 &rarr;
           </Link>
         </div>
         <div className="bg-green-50 p-6 rounded-lg border border-green-200 hover:shadow-lg transition-shadow">
           <h3 className="text-lg font-semibold text-green-800 mb-2">尋找策略</h3>
           <p className="text-sm text-green-700 mb-3">瀏覽策略中心，發現潛在的交易機會。</p>
           <Link href="/strategy-center" className="text-sm font-medium text-green-600 hover:underline">
             前往策略中心 &rarr;
           </Link>
         </div>
      </div>

    </div>
  );
}
