'use client';

import { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// 註冊 Chart.js 所需的組件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface HsiCurrentData {
  current_price: number;
  change_percent: number;
  volume: number;
  // 可以根據後端 API 的實際返回值添加更多字段
}

interface HsiHistoricalData {
  labels: string[]; // 日期或其他時間標籤
  prices: number[]; // 對應的價格
}

export default function MarketOverviewPage() {
  const [hsiCurrentData, setHsiCurrentData] = useState<HsiCurrentData | null>(null);
  const [hsiHistoricalData, setHsiHistoricalData] = useState<HsiHistoricalData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // 同時獲取即時數據和歷史數據
        const [currentResponse, historyResponse] = await Promise.all([
          fetch('http://localhost:8000/api/indicators/hsi'), // 即時數據 API
          fetch('http://localhost:8000/api/indicators/hsi/history') // 假設的歷史數據 API
        ]);

        if (!currentResponse.ok) {
          throw new Error(`無法獲取即時數據: ${currentResponse.status}`);
        }
        if (!historyResponse.ok) {
          throw new Error(`無法獲取歷史數據: ${historyResponse.status}`);
        }

        const currentData: HsiCurrentData = await currentResponse.json();
        const historicalData: HsiHistoricalData = await historyResponse.json();

        setHsiCurrentData(currentData);
        setHsiHistoricalData(historicalData);

      } catch (err: any) {
        setError(err.message || '獲取恆指數據時出錯');
        console.error("Error fetching HSI data:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
    // 定期刷新邏輯可以根據需要添加
  }, []);

  const priceChangeColor = hsiCurrentData?.change_percent
    ? hsiCurrentData.change_percent > 0 ? 'text-green-600' : hsiCurrentData.change_percent < 0 ? 'text-red-600' : 'text-gray-500'
    : 'text-gray-500';

  // 準備 Chart.js 的數據格式
  const chartData = {
    labels: hsiHistoricalData?.labels || [],
    datasets: [
      {
        label: '恆生指數',
        data: hsiHistoricalData?.prices || [],
        borderColor: 'rgb(59, 130, 246)', // Tailwind blue-500
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        tension: 0.1 // 使線條稍微平滑
      },
    ],
  };

  // Chart.js 的選項配置
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false, // 允許圖表調整高度
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '恆生指數歷史走勢',
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      }
    },
    scales: {
      x: {
        display: true,
        title: {
          display: false,
          text: '日期',
        },
      },
      y: {
        display: true,
        title: {
          display: false,
          text: '指數',
        },
      },
    },
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 border-b pb-2">市場總覽 Market Overview</h1>

      {isLoading && (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
          <p className="ml-4 text-lg text-gray-600">正在加載恆指數據...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">錯誤!</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      )}

      {!isLoading && !error && hsiCurrentData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* 左側數據顯示 */}
          <div className="md:col-span-1 bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">恆生指數 (HSI)</h2>
            <div className="mb-4">
              <span className="text-4xl font-bold">{hsiCurrentData.current_price.toLocaleString()}</span>
            </div>
            <div className={`text-2xl font-semibold mb-4 ${priceChangeColor}`}>
              {hsiCurrentData.change_percent > 0 ? '+' : ''}{hsiCurrentData.change_percent.toFixed(2)}%
            </div>
            <div>
              <span className="text-gray-500">成交量:</span>
              <span className="ml-2 font-medium text-gray-800">{(hsiCurrentData.volume / 1_000_000_000).toFixed(2)} B</span>
            </div>
            {/* 可在此處添加更多即時數據 */}
          </div>

          {/* 右側圖表區域 */}
          <div className="md:col-span-2 bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">指數走勢</h2>
            {/* 修改圖表區域的高度 */}
            <div className="relative h-96"> 
              {hsiHistoricalData ? (
                <Line options={chartOptions} data={chartData} />
              ) : (
                <div className="flex items-center justify-center h-full">
                  <p className="text-gray-500">無法加載歷史數據以生成圖表。</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 其他時間級別圖表或成交量圖表可以在下方繼續添加 */}

    </div>
  );
} 