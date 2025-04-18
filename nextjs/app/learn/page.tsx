import React from 'react';

export default function LearnPage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 border-b pb-2">學習中心 Learn</h1>

      <div className="space-y-8">
        {/* Section 1: Introduction */}
        <section>
          <h2 className="text-2xl font-semibold mb-3 text-gray-800">歡迎來到學習中心</h2>
          <p className="text-gray-600 leading-relaxed">
            在這裡，您可以了解恆生指數交易中常用的技術指標、圖表形態以及基本策略概念。掌握這些知識將有助於您更好地理解市場動態和交易信號。
          </p>
        </section>

        {/* Section 2: Technical Indicators */}
        <section>
          <h2 className="text-2xl font-semibold mb-4 text-gray-800">技術指標詳解</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Indicator Card 1: Bollinger Bands */}
            <div className="bg-white p-5 rounded-lg shadow">
              <h3 className="text-xl font-medium mb-2 text-blue-600">布林帶 (Bollinger Bands)</h3>
              <p className="text-gray-600 text-sm">
                布林帶由移動平均線（中軌）以及其上下各一個標準差（上軌和下軌）組成。它有助於判斷價格波動的相對高低點和市場波動性。
                價格觸及上軌可能表示超買，觸及下軌可能表示超賣。
              </p>
            </div>
            {/* Indicator Card 2: MACD */}
            <div className="bg-white p-5 rounded-lg shadow">
              <h3 className="text-xl font-medium mb-2 text-green-600">MACD</h3>
              <p className="text-gray-600 text-sm">
                指數平滑異同移動平均線 (MACD) 顯示兩條指數移動平均線之間的關係。MACD 線穿越信號線（黃金交叉/死亡交叉）常被視為買賣信號。
                柱狀圖 (Histogram) 顯示 MACD 與信號線的差離。
              </p>
            </div>
            {/* Indicator Card 3: RSI */}
            <div className="bg-white p-5 rounded-lg shadow">
              <h3 className="text-xl font-medium mb-2 text-purple-600">相對強弱指數 (RSI)</h3>
              <p className="text-gray-600 text-sm">
                RSI 是一個動量指標，衡量近期價格變動的速度和幅度，用於評估超買或超賣狀況。通常，RSI 高於 70 被視為超買，低於 30 被視為超賣。
              </p>
            </div>
            {/* Add more indicator cards if needed */}
          </div>
        </section>

        {/* Section 3: Candlestick Patterns */}
        <section>
          <h2 className="text-2xl font-semibold mb-3 text-gray-800">陰陽燭 (K線) 教學</h2>
          <p className="text-gray-600 leading-relaxed mb-4">
            陰陽燭圖是技術分析中常用的圖表類型，每根燭體顯示特定時間段內的開盤價、最高價、最低價和收盤價。
            不同的 K 線形態可以提供關於市場情緒和潛在趨勢反轉的線索。
          </p>
          {/* Add examples of candlestick patterns here */}
          <div className="bg-gray-100 p-4 rounded">
            <p className="text-gray-500 text-center">（此處可加入常見 K 線形態圖文說明，例如十字星、吞沒形態等）</p>
          </div>
        </section>

        {/* Section 4: Strategy Examples (Optional) */}
        <section>
          <h2 className="text-2xl font-semibold mb-3 text-gray-800">策略範例 (可選)</h2>
          <p className="text-gray-600 leading-relaxed mb-4">
            了解如何結合不同的技術指標和圖表形態來制定交易策略。
          </p>
          <div className="bg-gray-100 p-4 rounded">
             <p className="text-gray-500 text-center">（此處可加入基於本平台指標的簡單策略範例說明）</p>
          </div>
        </section>

      </div>
    </div>
  );
} 