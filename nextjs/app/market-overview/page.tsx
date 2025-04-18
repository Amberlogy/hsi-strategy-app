'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic'; // Import dynamic
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement, // For Volume
  Title,
  Tooltip,
  Legend,
  TimeScale, // Import TimeScale for time series data
} from 'chart.js';
// import { Line, Chart } from 'react-chartjs-2'; // Remove static import of Chart
import zoomPlugin from 'chartjs-plugin-zoom'; // Import zoom plugin
import 'chartjs-adapter-date-fns'; // Adapter for time scale

// Register necessary Chart.js components and plugins
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  zoomPlugin
);

// --- Data Interfaces ---
interface HsiCurrentData {
  current_price: number;
  change_percent: number;
  volume: number;
}

interface HistoricalPoint {
  time: string; 
  close: number;
  volume: number;
}

// --- Mock Data ---
const mockHistoricalData: HistoricalPoint[] = [
  { time: '2024-03-01', close: 17000, volume: 150000000 },
  { time: '2024-03-02', close: 17100, volume: 160000000 },
  { time: '2024-03-03', close: 17200, volume: 175000000 },
  { time: '2024-03-04', close: 17250, volume: 170000000 },
  { time: '2024-03-05', close: 17300, volume: 180000000 },
  { time: '2024-03-06', close: 17350, volume: 165000000 },
  { time: '2024-03-07', close: 17400, volume: 190000000 },
];

// Add mock current data
const mockCurrentData: HsiCurrentData = {
    current_price: 17425.50,
    change_percent: 0.35, // Example positive change
    volume: 195000000,
};

// Dynamically import the *generic* Chart component, disable SSR
const DynamicChart = dynamic(() => import('react-chartjs-2').then(mod => mod.Chart), {
  ssr: false,
  loading: () => <p>正在加載圖表...</p> // Optional loading state
});

// --- Main Page Component ---
export default function MarketOverviewPage() {
  // Use mock data directly
  const [hsiCurrentData] = useState<HsiCurrentData>(mockCurrentData);

  // Keep historical data mocked
  const hsiHistoricalData: HistoricalPoint[] = mockHistoricalData;

  const priceChangeColor = hsiCurrentData.change_percent > 0 ? 'text-green-600' : hsiCurrentData.change_percent < 0 ? 'text-red-600' : 'text-gray-500';

  // --- Prepare Chart.js Data --- 
  const chartData = {
    labels: hsiHistoricalData.map(d => d.time),
    datasets: [
      {
        type: 'line' as const,
        label: '恆生指數 (收盤價)',
        data: hsiHistoricalData.map(d => d.close),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        tension: 0.1,
        pointRadius: 1,
        yAxisID: 'yPrice',
      },
      {
        type: 'bar' as const,
        label: '成交量',
        data: hsiHistoricalData.map(d => d.volume),
        backgroundColor: 'rgba(156, 163, 175, 0.4)',
        borderColor: 'rgba(156, 163, 175, 0.6)',
        yAxisID: 'yVolume',
        order: 1
      },
    ],
  };

  // --- Chart.js Options --- 
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '恆生指數走勢與成交量 (模擬數據)',
        font: { size: 16 }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        titleFont: { size: 14 },
        bodyFont: { size: 12 },
        padding: 10,
      },
      zoom: {
        pan: {
          enabled: true,
          mode: 'x' as const,
        },
        zoom: {
          wheel: { enabled: true },
          pinch: { enabled: true },
          mode: 'x' as const,
        },
      }
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          unit: 'day' as const,
          tooltipFormat: 'yyyy-MM-dd',
          displayFormats: {
             day: 'MM-dd'
          }
        },
        grid: {
          color: 'rgba(200, 200, 200, 0.1)',
        },
        ticks: {
          source: 'auto' as const,
          maxRotation: 0,
          autoSkip: true,
        }
      },
      yPrice: { 
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        grid: {
          color: 'rgba(200, 200, 200, 0.1)',
        },
        title: {
          display: true,
          text: '指數'
        }
      },
      yVolume: { 
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        grid: { drawOnChartArea: false }, 
        ticks: {
          callback: function(value: number | string) {
            if (typeof value === 'number') {
              return value / 1_000_000 + 'M'; 
            }
            return value;
          }
        },
        title: {
          display: true,
          text: '成交量'
        }
      }
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 border-b pb-2">市場總覽 Market Overview (模擬數據)</h1>

      {/* Display Mock Current Data */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 bg-white p-4 rounded-lg shadow-sm">
        <div className="text-center md:text-left">
          <h2 className="text-sm font-medium text-gray-500">恆生指數 (HSI)</h2>
          <p className="text-2xl font-bold">{hsiCurrentData.current_price.toLocaleString()}</p>
        </div>
         <div className="text-center md:text-left">
           <h2 className="text-sm font-medium text-gray-500">漲跌幅</h2>
           <p className={`text-2xl font-bold ${priceChangeColor}`}>
             {hsiCurrentData.change_percent > 0 ? '+' : ''}{hsiCurrentData.change_percent.toFixed(2)}%
           </p>
        </div>
         <div className="text-center md:text-left">
           <h2 className="text-sm font-medium text-gray-500">今日成交量</h2>
           <p className="text-xl font-semibold">{(hsiCurrentData.volume / 1_000_000_000).toFixed(2)} B</p>
         </div>
         <div className="text-center md:text-left">
           <h2 className="text-sm font-medium text-gray-500">--</h2>
           <p className="text-xl font-semibold">--</p>
         </div>
      </div>

      {/* Chart Area */} 
      <div className="bg-white p-4 md:p-6 rounded-lg shadow-md">
        <div className="relative h-[500px]">
          {/* Use the dynamically imported component with type prop */}
          <DynamicChart type='line' options={chartOptions} data={chartData} />
        </div>
      </div>

    </div>
  );
} 