'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}) {
  useEffect(() => {
    // 可選：將錯誤發送到報告服務
    console.error('頁面錯誤:', error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <div className="p-8 bg-white rounded-lg shadow-md max-w-md w-full">
        <h1 className="text-4xl font-bold text-red-600 mb-4">出錯了</h1>
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">發生了一些問題</h2>
        <p className="text-gray-600 mb-6">
          很抱歉，加載頁面時發生了錯誤。請嘗試刷新頁面或返回首頁。
        </p>
        <div className="flex flex-col sm:flex-row gap-4">
          <button
            onClick={() => reset()}
            className="px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
          >
            重試
          </button>
          <a
            href="/"
            className="px-6 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors text-center"
          >
            返回首頁
          </a>
        </div>
      </div>
    </div>
  );
} 