'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  TimeScale,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import 'chartjs-adapter-date-fns';

// Dynamically import the Chart component
const DynamicChart = dynamic(() => import('react-chartjs-2').then((mod) => mod.Chart), {
  ssr: false,
  loading: () => <p>Loading chart...</p>,
});

// Mock OHLC data for Candlestick chart
const mockCandlestickData = [
  { x: new Date(2024, 2, 1), o: 17000, h: 17150, l: 16950, c: 17100 },
  { x: new Date(2024, 2, 2), o: 17100, h: 17250, l: 17050, c: 17200 },
  { x: new Date(2024, 2, 3), o: 17200, h: 17300, l: 17150, c: 17250 },
  { x: new Date(2024, 2, 4), o: 17250, h: 17400, l: 17200, c: 17350 },
  { x: new Date(2024, 2, 5), o: 17350, h: 17380, l: 17280, c: 17300 }, // Doji example
  { x: new Date(2024, 2, 6), o: 17300, h: 17450, l: 17250, c: 17420 },
  { x: new Date(2024, 2, 7), o: 17420, h: 17500, l: 17380, c: 17480 },
];

export default function CandlestickAiPage() {
  const [chartRegistered, setChartRegistered] = useState(false);

  useEffect(() => {
    const registerChart = async () => {
      // Dynamically import the financial chart library
      const { CandlestickController, CandlestickElement, OhlcController, OhlcElement } = await import('chartjs-chart-financial');
      await import('chartjs-adapter-date-fns');

      ChartJS.register(
        CategoryScale,
        LinearScale,
        TimeScale,
        Title,
        Tooltip,
        Legend,
        // Register financial elements
        CandlestickController,
        CandlestickElement,
        OhlcController,
        OhlcElement
      );
      setChartRegistered(true);
    };

    if (!chartRegistered) {
      registerChart();
    }
  }, [chartRegistered]);

  const chartData = {
    datasets: [{
      label: '恆生指數 (K線)',
      data: mockCandlestickData,
      // No specific backgroundColor/borderColor needed for candlestick type by default
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }, // Hide legend for candlestick
      title: {
        display: true,
        text: '恆生指數 K線圖 (模擬數據)',
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          unit: 'day' as const,
          tooltipFormat: 'yyyy-MM-dd',
        },
        adapters: {
          date: { locale: 'zh-HK' } // Optional: Set locale for date formatting
        }
      },
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: '指數'
        }
      }
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">陰陽燭辨識 Candlestick AI</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Chart Area */}
        <div className="md:col-span-2 bg-white p-4 md:p-6 rounded-lg shadow-md h-[500px]">
          {chartRegistered ? (
            <DynamicChart type='candlestick' options={chartOptions} data={chartData} />
          ) : (
            <p>Loading chart...</p>
          )}
        </div>

        {/* AI Analysis Area */}
        <div className="md:col-span-1 bg-white p-4 md:p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">AI 形態辨識結果</h2>
          <div className="space-y-2 text-sm">
            <p><strong>日期 2024-03-05:</strong> 偵測到 <span className="font-semibold text-blue-600">十字星 (Doji)</span> - 市場猶豫不決。</p>
            <p><strong>日期 2024-03-07:</strong> 陽燭形態，顯示上升趨勢。</p>
            {/* Placeholder for more AI results */}
            <p className="text-gray-500 mt-4">* AI 分析結果僅供參考，不構成投資建議。</p>
          </div>
        </div>
      </div>
    </div>
  );
} 