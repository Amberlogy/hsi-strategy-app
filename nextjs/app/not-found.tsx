'use client';

import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 px-4">
      <div className="text-center max-w-md">
        <h1 className="text-6xl font-bold text-gray-800 mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">頁面未找到</h2>
        <p className="mb-8 text-gray-600">
          對不起，您要尋找的頁面不存在或已經被移除。
        </p>
        <Link 
          href="/" 
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors duration-300 inline-block"
        >
          返回首頁
        </Link>
      </div>
    </div>
  );
} 