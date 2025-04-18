'use client'; // Strategy Center might involve client-side interactions later

import React from 'react';

// Define an interface for the strategy data
interface Strategy {
  id: string;
  name: string;
  description: string;
  currentSignal: 'Buy' | 'Sell' | 'Hold' | 'N/A';
}

// Mock data for strategies
const mockStrategies: Strategy[] = [
  {
    id: 'bb_crossover',
    name: '布林帶通道突破 (Bollinger Bands Crossover)',
    description: '當價格突破布林帶上軌時買入，跌破下軌時賣出。',
    currentSignal: 'Hold', 
  },
  {
    id: 'macd_cross',
    name: 'MACD 黃金交叉/死亡交叉 (MACD Cross)',
    description: 'MACD 線上穿信號線為買入信號，下穿為賣出信號。',
    currentSignal: 'Buy',
  },
  {
    id: 'rsi_divergence',
    name: 'RSI 背離 (RSI Divergence)',
    description: '偵測價格與 RSI 指標之間的背離現象，尋找潛在的反轉點。',
    currentSignal: 'N/A', // Example: No signal currently
  },
   {
    id: 'sma_cross',
    name: '簡單移動平均線交叉 (SMA Crossover)',
    description: '短期均線上穿長期均線為買入信號，下穿為賣出信號 (例如：5日線與20日線)。',
    currentSignal: 'Sell',
  },
  // Add more strategies here
];

// Helper function to get signal color
const getSignalColor = (signal: Strategy['currentSignal']) => {
  switch (signal) {
    case 'Buy': return 'text-green-600';
    case 'Sell': return 'text-red-600';
    case 'Hold': return 'text-yellow-600';
    default: return 'text-gray-500';
  }
};

export default function StrategyCenterPage() {
  // In a real app, you would fetch strategies from an API
  const strategies = mockStrategies;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 border-b pb-2">策略中心 Strategy Center</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {strategies.map((strategy) => (
          <div key={strategy.id} className="bg-white p-6 rounded-lg shadow-md border border-gray-200 flex flex-col justify-between">
            <div>
              <h2 className="text-xl font-semibold mb-2 text-gray-800">{strategy.name}</h2>
              <p className="text-gray-600 text-sm mb-4">{strategy.description}</p>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-sm">
                當前信號 (模擬): 
                <span className={`font-bold ml-2 ${getSignalColor(strategy.currentSignal)}`}>
                  {strategy.currentSignal}
                </span>
              </p>
              {/* Add buttons for details/backtesting later */}
              {/* <button className="mt-3 text-sm text-blue-600 hover:underline">查看詳情</button> */}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 