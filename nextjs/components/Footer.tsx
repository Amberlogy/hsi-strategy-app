import React from 'react';
import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-gray-800 text-white p-6">
      <div className="container mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-3">關於我們</h3>
            <p className="text-gray-300 text-sm">
              恆生指數策略平台為投資者提供全面的技術分析工具和策略研究，助您把握香港股市投資良機。
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-3">快速鏈接</h3>
            <ul className="space-y-2 text-sm">
              <li><Link href="/market-overview" className="text-gray-300 hover:text-white">市場總覽</Link></li>
              <li><Link href="/technical-analysis" className="text-gray-300 hover:text-white">技術分析</Link></li>
              <li><Link href="/learn" className="text-gray-300 hover:text-white">學習中心</Link></li>
              <li><Link href="/about" className="text-gray-300 hover:text-white">關於我們</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-3">聯絡我們</h3>
            <p className="text-gray-300 text-sm">
              如有任何問題或建議，請發送郵件至 <a href="mailto:contact@hsistrategy.com" className="underline hover:text-white">contact@hsistrategy.com</a>
            </p>
          </div>
        </div>
        <div className="border-t border-gray-700 mt-6 pt-6 text-center text-sm text-gray-400">
          <p>© {new Date().getFullYear()} 恆生指數策略平台. 版權所有。</p>
        </div>
      </div>
    </footer>
  );
} 