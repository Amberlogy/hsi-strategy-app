'use client';

import { useState, useEffect } from 'react';

interface HsiData {
  current_price: number;
  change_percent: number;
  volume: number;
  // 可以根據後端 API 的實際返回值添加更多字段
}

export default function MarketOverviewPage() {
  const [hsiData, setHsiData] = useState<HsiData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // 注意：這裡假設後端 API 在 http://localhost:8000
        // 在實際部署中，您可能需要配置一個基礎 URL 或使用相對路徑（如果前端和後端部署在同一來源）
        const response = await fetch('http://localhost:8000/api/indicators/hsi');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: HsiData = await response.json();
        setHsiData(data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch HSI data');
        console.error("Error fetching HSI data:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
    // 可以在這裡設置定時器定期刷新數據
    // const intervalId = setInterval(fetchData, 60000); // 例如每分鐘刷新一次
    // return () => clearInterval(intervalId); // 清除定時器
  }, []);

  const priceChangeColor = hsiData?.change_percent
    ? hsiData.change_percent > 0 ? 'text-green-600' : hsiData.change_percent < 0 ? 'text-red-600' : 'text-gray-500'
    : 'text-gray-500';

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
          <span className="block sm:inline"> 無法獲取恆指數據: {error}</span>
        </div>
      )}

      {!isLoading && !error && hsiData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* 左側數據顯示 */}
          <div className="md:col-span-1 bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">恆生指數 (HSI)</h2>
            <div className="mb-4">
              <span className="text-4xl font-bold">{hsiData.current_price.toLocaleString()}</span>
            </div>
            <div className={`text-2xl font-semibold mb-4 ${priceChangeColor}`}>
              {hsiData.change_percent > 0 ? '+' : ''}{hsiData.change_percent.toFixed(2)}%
            </div>
            <div>
              <span className="text-gray-500">成交量:</span>
              <span className="ml-2 font-medium text-gray-800">{(hsiData.volume / 1_000_000_000).toFixed(2)} B</span>
            </div>
            {/* 可在此處添加更多即時數據，如高低點等 */}
          </div>

          {/* 右側圖表區域 */}
          <div className="md:col-span-2 bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">指數走勢</h2>
            <div className="bg-gray-100 h-96 flex items-center justify-center rounded">
              <p className="text-gray-500">走勢圖表將在此處顯示</p>
              {/* 圖表組件將替換此處 */}
            </div>
          </div>
        </div>
      )}

      {/* 其他時間級別圖表或成交量圖表可以在下方繼續添加 */}

    </div>
  );
} 