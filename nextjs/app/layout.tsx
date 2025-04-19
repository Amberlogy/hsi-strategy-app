'use client';

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
// 移除這兩個導入以防止預渲染問題
// import Navbar from '../components/Navbar';
// import Footer from '../components/Footer';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: '恆生指數策略平台 | HSI Strategy App',
  description: '專業的恆生指數分析工具，提供技術指標、K線形態識別、策略回測及模擬交易功能，助您掌握香港股市投資先機。',
  keywords: '恆生指數, 技術分析, 股市策略, HSI, 香港股市, 投資分析, 交易信號, 市場洞察',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // 在提供一個極簡的布局，避免任何可能導致渲染問題的組件
  return (
    <html lang="zh-HK" className="h-full">
      <body className={`${inter.className} flex flex-col min-h-screen bg-gray-50`}>
        <div className="w-64 h-screen bg-gray-800 text-white p-5 fixed">
          <h2 className="text-xl font-semibold mb-5">HSI Strategy</h2>
          <ul>
            <li className="mb-2">
              <a href="/" className="hover:text-gray-300">首頁 Home</a>
            </li>
            <li className="mb-2">
              <a href="/market-overview" className="hover:text-gray-300">市場總覽 Market Overview</a>
            </li>
            <li className="mb-2">
              <a href="/technical-analysis" className="hover:text-gray-300">技術分析 Technical Analysis</a>
            </li>
          </ul>
        </div>
        <main className="flex-grow ml-64">
          {children}
        </main>
      </body>
    </html>
  );
}
