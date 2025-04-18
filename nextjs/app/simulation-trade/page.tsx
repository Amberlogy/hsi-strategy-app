'use client'; // This page will likely involve client-side state and interactions

import React, { useState } from 'react';

// Interfaces for data structures
interface Holding {
  symbol: string;
  name: string;
  quantity: number;
  avgCost: number;
  currentPrice: number; // Needed to calculate current value and P/L
}

interface Transaction {
  id: string;
  date: string;
  type: 'Buy' | 'Sell';
  symbol: string;
  quantity: number;
  price: number;
}

// Mock data
const mockHoldings: Holding[] = [
  { symbol: '0700.HK', name: '騰訊控股', quantity: 100, avgCost: 350.50, currentPrice: 380.20 },
  { symbol: '0005.HK', name: '匯豐控股', quantity: 200, avgCost: 65.80, currentPrice: 68.10 },
  { symbol: '9988.HK', name: '阿里巴巴', quantity: 50, avgCost: 85.20, currentPrice: 75.50 }, 
];

const mockTransactions: Transaction[] = [
  { id: 't3', date: '2024-03-05', type: 'Sell', symbol: '9988.HK', quantity: 50, price: 88.00 },
  { id: 't2', date: '2024-02-20', type: 'Buy', symbol: '0005.HK', quantity: 200, price: 65.80 },
  { id: 't1', date: '2024-01-15', type: 'Buy', symbol: '0700.HK', quantity: 100, price: 350.50 },
];

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

export default function SimulationTradePage() {
  // State for the trading panel (add more sophisticated logic later)
  const [symbol, setSymbol] = useState('');
  const [quantity, setQuantity] = useState('');

  // Mock data state (in a real app, this would come from state management/API)
  const holdings = mockHoldings;
  const transactions = mockTransactions;

  const handleTrade = (type: 'Buy' | 'Sell') => {
    // Basic validation (improve later)
    if (!symbol || !quantity || isNaN(Number(quantity)) || Number(quantity) <= 0) {
      alert('請輸入有效的股票代號和數量。');
      return;
    }
    alert(`模擬 ${type === 'Buy' ? '買入' : '賣出'}: ${quantity} 股 ${symbol}`);
    // TODO: Add logic to update holdings and transactions state
    setSymbol('');
    setQuantity('');
  };

  return (
    <div className="container mx-auto p-4 space-y-8">
      <h1 className="text-3xl font-bold border-b pb-2">模擬交易 Simulation Trade</h1>

      {/* Trading Panel */}
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h2 className="text-xl font-semibold mb-4 text-gray-800">交易面板</h2>
        <div className="flex flex-wrap gap-4 items-end">
          <div className="flex-grow">
            <label htmlFor="symbol" className="block text-sm font-medium text-gray-700 mb-1">股票代號</label>
            <input 
              type="text" 
              id="symbol" 
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())} 
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="例如: 0700.HK"
            />
          </div>
          <div className="flex-grow">
            <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">數量 (股)</label>
            <input 
              type="number" 
              id="quantity" 
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)} 
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="例如: 100"
              min="1"
            />
          </div>
          <div className="flex gap-2">
            <button 
              onClick={() => handleTrade('Buy')} 
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              模擬買入
            </button>
            <button 
              onClick={() => handleTrade('Sell')} 
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              模擬賣出
            </button>
          </div>
        </div>
      </div>

      {/* Current Holdings */}
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h2 className="text-xl font-semibold mb-4 text-gray-800">模擬持倉</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">名稱 (代號)</th>
                <th scope="col" className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">數量</th>
                <th scope="col" className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">平均成本</th>
                <th scope="col" className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">現價</th>
                <th scope="col" className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">市值</th>
                <th scope="col" className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">盈虧</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200 text-sm">
              {holdings.map((holding) => {
                const currentValue = holding.quantity * holding.currentPrice;
                const profitLoss = currentValue - (holding.quantity * holding.avgCost);
                return (
                  <tr key={holding.symbol}>
                    <td className="px-4 py-2 whitespace-nowrap font-medium text-gray-900">{holding.name} ({holding.symbol})</td>
                    <td className="px-4 py-2 whitespace-nowrap text-right">{holding.quantity.toLocaleString()}</td>
                    <td className="px-4 py-2 whitespace-nowrap text-right">{formatCurrency(holding.avgCost)}</td>
                    <td className="px-4 py-2 whitespace-nowrap text-right">{formatCurrency(holding.currentPrice)}</td>
                    <td className="px-4 py-2 whitespace-nowrap text-right">{formatCurrency(currentValue)}</td>
                    <td className={`px-4 py-2 whitespace-nowrap text-right font-semibold ${getPlColor(profitLoss)}`}>{formatCurrency(profitLoss)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Transaction History */}
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h2 className="text-xl font-semibold mb-4 text-gray-800">交易紀錄</h2>
        <div className="overflow-x-auto">
           <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">日期</th>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">類型</th>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">股票代號</th>
                <th scope="col" className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">數量</th>
                <th scope="col" className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">價格</th>
                <th scope="col" className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">總金額</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200 text-sm">
              {transactions.map((tx) => (
                <tr key={tx.id}>
                  <td className="px-4 py-2 whitespace-nowrap">{new Date(tx.date).toLocaleDateString('zh-HK')}</td>
                  <td className="px-4 py-2 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${tx.type === 'Buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {tx.type === 'Buy' ? '買入' : '賣出'}
                    </span>
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap font-medium text-gray-900">{tx.symbol}</td>
                  <td className="px-4 py-2 whitespace-nowrap text-right">{tx.quantity.toLocaleString()}</td>
                  <td className="px-4 py-2 whitespace-nowrap text-right">{formatCurrency(tx.price)}</td>
                  <td className="px-4 py-2 whitespace-nowrap text-right">{formatCurrency(tx.quantity * tx.price)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
} 