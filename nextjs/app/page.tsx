'use client'; // Home page might have dynamic elements later

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';

// Mock data for market snapshot
const mockMarketSnapshot = {
  hsiValue: 17650.25,
  changePercent: 0.45,
  volumeBillion: 115.5,
  peRatio: 10.8,
  dividendYield: 3.45,
};

// Helper to format currency (simplified for index points)
const formatIndexValue = (value: number) => {
  return value.toLocaleString('zh-HK', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
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
      <h1 className="text-3xl font-bold border-b pb-2">恆生指數策略平台</h1>

      {/* Welcome Message */}
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h2 className="text-xl font-semibold mb-2 text-gray-800">歡迎蒞臨恆生指數策略分析平台</h2>
        <p className="text-gray-600 mb-3">
          本平台匯集專業金融分析工具，為您提供恆生指數市場的深度洞察與先進分析。我們整合了技術指標、形態識別、市場熱度等關鍵數據，助您在複雜多變的香港股市中把握投資良機。
        </p>
        <p className="text-gray-600">
          無論您是資深投資者還是初入市場的新手，我們的平台都能協助您建立更科學的投資策略，做出更精準的市場決策，同時降低投資風險，提升投資效益。
        </p>
      </div>

      {/* Market Snapshot Cards */}
      <div>
        <h2 className="text-2xl font-semibold mb-4 text-gray-700">市場即時概況</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
            <h3 className="text-sm font-medium text-gray-500 mb-1">恆生指數現價</h3>
            <p className="text-2xl font-bold text-blue-600">{formatIndexValue(snapshot.hsiValue)}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
            <h3 className="text-sm font-medium text-gray-500 mb-1">日漲跌幅</h3>
            <p className={`text-2xl font-bold ${getChangeColor(snapshot.changePercent)}`}>
              {snapshot.changePercent >= 0 ? '+' : ''}{snapshot.changePercent.toFixed(2)}%
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
            <h3 className="text-sm font-medium text-gray-500 mb-1">成交金額（十億港元）</h3>
            <p className="text-2xl font-bold">{snapshot.volumeBillion.toFixed(1)} B</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
            <h3 className="text-sm font-medium text-gray-500 mb-1">市盈率（倍）</h3>
            <p className="text-2xl font-bold">{snapshot.peRatio.toFixed(1)}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
            <h3 className="text-sm font-medium text-gray-500 mb-1">平均股息率</h3>
            <p className="text-2xl font-bold">{snapshot.dividendYield.toFixed(2)}%</p>
          </div>
        </div>
      </div>

      {/* Platform Features */}
      <div>
        <h2 className="text-2xl font-semibold mb-4 text-gray-700">平台核心功能</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white p-5 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-blue-700 mb-2">市場總覽</h3>
            <p className="text-gray-600 mb-3">全面監控恆生指數及其成分股表現，提供市場熱力圖、板塊輪動分析及主要成分股貢獻度，幫助您掌握市場整體走勢與熱點板塊。</p>
            <Link href="/market-overview" className="text-sm font-medium text-blue-600 hover:underline">
              分析市場走勢 &rarr;
            </Link>
          </div>
          <div className="bg-white p-5 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-blue-700 mb-2">技術分析</h3>
            <p className="text-gray-600 mb-3">運用多種專業技術指標分析市場趨勢，包括移動平均線、相對強弱指標(RSI)、MACD、KDJ、布林帶等，協助您預判市場轉折點與突破位。</p>
            <Link href="/technical-analysis" className="text-sm font-medium text-blue-600 hover:underline">
              探索技術指標 &rarr;
            </Link>
          </div>
          <div className="bg-white p-5 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-blue-700 mb-2">K線形態識別</h3>
            <p className="text-gray-600 mb-3">結合人工智能技術，自動識別超過20種關鍵K線形態，包括頭肩頂、雙重底、旗形、三角形等，為您提供形態突破信號與潛在反轉點。</p>
            <Link href="/candlestick-ai" className="text-sm font-medium text-blue-600 hover:underline">
              識別形態信號 &rarr;
            </Link>
          </div>
          <div className="bg-white p-5 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-blue-700 mb-2">策略中心</h3>
            <p className="text-gray-600 mb-3">提供多種經過歷史數據回測的交易策略模型，包括趨勢跟蹤、動量交易、反轉策略等，生成精準的入場和出場信號，助您把握市場機會。</p>
            <Link href="/strategy-center" className="text-sm font-medium text-blue-600 hover:underline">
              探索交易策略 &rarr;
            </Link>
          </div>
          <div className="bg-white p-5 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-blue-700 mb-2">模擬交易</h3>
            <p className="text-gray-600 mb-3">在零風險環境中測試您的投資策略，建立虛擬投資組合，追蹤績效表現並分析勝率與風險回報比，優化您的實盤交易策略。</p>
            <Link href="/simulation-trade" className="text-sm font-medium text-blue-600 hover:underline">
              開始虛擬交易 &rarr;
            </Link>
          </div>
          <div className="bg-white p-5 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-blue-700 mb-2">學習中心</h3>
            <p className="text-gray-600 mb-3">豐富的金融知識庫，包含恆生指數投資基礎、技術分析教程、策略構建指南等專業內容，助您從新手晉升為專業投資者。</p>
            <Link href="/learn" className="text-sm font-medium text-blue-600 hover:underline">
              提升投資技能 &rarr;
            </Link>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 p-8 rounded-lg text-white shadow-lg">
        <h2 className="text-2xl font-bold mb-3">立即開始您的智慧投資旅程</h2>
        <p className="mb-4">探索我們先進的分析工具與精準的市場洞察，掌握恆生指數投資先機，實現更高效的資產配置與風險管理。</p>
        <div className="flex flex-wrap gap-4">
          <Link href="/market-overview" className="bg-white text-blue-600 px-6 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors">
            探索市場動態
          </Link>
          <Link href="/learn" className="bg-transparent border border-white text-white px-6 py-2 rounded-lg font-medium hover:bg-white hover:text-blue-600 transition-colors">
            進入學習中心
          </Link>
        </div>
      </div>

      {/* Market News Teaser */}
      <div>
        <h2 className="text-2xl font-semibold mb-4 text-gray-700">市場動態與資訊</h2>
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <p className="text-gray-500 text-sm mb-2">數據更新於：{new Date().toLocaleDateString('zh-HK')}</p>
          <p className="text-gray-600">
            市場資訊功能即將上線，敬請期待。此功能將為您提供最新的恆生指數市場動態、香港股市財經新聞、專家分析報告以及重要經濟數據發布，助您及時把握市場脈搏與投資方向。
          </p>
        </div>
      </div>
    </div>
  );
}