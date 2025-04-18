'use client';

import { useState, useEffect } from 'react';
import { getSimulatorStatus, simulateStrategy, type SimulatorStatus } from '../services/api';

export default function Home() {
  const [status, setStatus] = useState<SimulatorStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    shortPeriod: 5,
    longPeriod: 20,
    maType: 'sma'
  });

  useEffect(() => {
    fetchStatus();
  }, []);

  async function fetchStatus() {
    try {
      const data = await getSimulatorStatus();
      setStatus(data);
    } catch (error) {
      console.error('Failed to fetch status:', error);
    }
  }

  async function handleSimulate() {
    setIsLoading(true);
    try {
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      
      const result = await simulateStrategy({
        start_date: startDate,
        end_date: endDate,
        strategy_name: 'macross',
        short_period: formData.shortPeriod,
        long_period: formData.longPeriod,
        ma_type: formData.maType as 'sma' | 'ema'
      });
      
      await fetchStatus(); // 重新獲取更新後的狀態
    } catch (error) {
      console.error('Simulation failed:', error);
    } finally {
      setIsLoading(false);
    }
  }

  function formatNumber(num: number | undefined) {
    if (num === undefined) return '--';
    return num.toLocaleString('zh-TW', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }

  function formatPercentage(num: number | undefined) {
    if (num === undefined) return '--';
    return (num * 100).toLocaleString('zh-TW', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }) + '%';
  }

  return (
    <div className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">HSI 交易策略系統</h1>
      </header>
      
      <main className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 策略績效概覽 */}
        <section className="p-6 bg-white rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">策略績效</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-gray-600">總收益率</p>
              <p className="text-2xl font-bold text-green-600">
                {formatPercentage(status?.performance?.total_return)}
              </p>
            </div>
            <div>
              <p className="text-gray-600">最大回撤</p>
              <p className="text-2xl font-bold text-red-600">
                {formatPercentage(status?.performance?.max_drawdown)}
              </p>
            </div>
            <div>
              <p className="text-gray-600">勝率</p>
              <p className="text-2xl font-bold">
                {formatPercentage(status?.performance?.win_rate)}
              </p>
            </div>
            <div>
              <p className="text-gray-600">交易次數</p>
              <p className="text-2xl font-bold">
                {status?.performance?.trade_count ?? '--'}
              </p>
            </div>
          </div>
        </section>

        {/* 當前交易狀態 */}
        <section className="p-6 bg-white rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">交易狀態</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-gray-600">當前資金</p>
              <p className="text-2xl font-bold">
                ${formatNumber(status?.cash)}
              </p>
            </div>
            <div>
              <p className="text-gray-600">持倉數量</p>
              <p className="text-2xl font-bold">
                {status?.positions?.HSI ?? '--'}
              </p>
            </div>
            <div>
              <p className="text-gray-600">最新信號</p>
              <p className="text-2xl font-bold">
                {status?.trade_log?.[0]?.type === 'buy' ? '買入' : 
                 status?.trade_log?.[0]?.type === 'sell' ? '賣出' : '--'}
              </p>
            </div>
            <div>
              <p className="text-gray-600">市值</p>
              <p className="text-2xl font-bold">
                ${formatNumber(status?.positions?.HSI ?? 0)}
              </p>
            </div>
          </div>
        </section>

        {/* 策略設置 */}
        <section className="p-6 bg-white rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">策略設置</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-gray-600">移動平均線週期</label>
              <div className="flex gap-4">
                <input 
                  type="number" 
                  placeholder="短期" 
                  className="p-2 border rounded w-full"
                  value={formData.shortPeriod}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    shortPeriod: parseInt(e.target.value) || 0
                  }))}
                />
                <input 
                  type="number" 
                  placeholder="長期"
                  className="p-2 border rounded w-full"
                  value={formData.longPeriod}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    longPeriod: parseInt(e.target.value) || 0
                  }))}
                />
              </div>
            </div>
            <div>
              <label className="block text-gray-600">移動平均線類型</label>
              <select 
                className="w-full p-2 border rounded"
                value={formData.maType}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  maType: e.target.value
                }))}
              >
                <option value="sma">SMA</option>
                <option value="ema">EMA</option>
              </select>
            </div>
            <button 
              className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-blue-300"
              onClick={handleSimulate}
              disabled={isLoading}
            >
              {isLoading ? '模擬中...' : '開始回測'}
            </button>
          </div>
        </section>

        {/* 最近交易記錄 */}
        <section className="p-6 bg-white rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">最近交易</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">時間</th>
                  <th className="text-left py-2">類型</th>
                  <th className="text-left py-2">價格</th>
                  <th className="text-left py-2">數量</th>
                </tr>
              </thead>
              <tbody>
                {status?.trade_log?.slice(0, 5).map((trade, index) => (
                  <tr key={index} className="text-gray-600">
                    <td className="py-2">
                      {new Date(trade.timestamp).toLocaleString('zh-TW')}
                    </td>
                    <td className="py-2">
                      {trade.type === 'buy' ? '買入' : '賣出'}
                    </td>
                    <td className="py-2">{formatNumber(trade.price)}</td>
                    <td className="py-2">{trade.quantity}</td>
                  </tr>
                ))}
                {(!status?.trade_log || status.trade_log.length === 0) && (
                  <tr className="text-gray-600">
                    <td className="py-2">--</td>
                    <td className="py-2">--</td>
                    <td className="py-2">--</td>
                    <td className="py-2">--</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}
