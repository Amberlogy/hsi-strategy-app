'use client';

// 這是Next.js的特殊文件，用於捕獲並顯示全局錯誤
// 它必須是客戶端組件
export default function GlobalError({
  error,
  reset,
}) {
  return (
    <html lang="zh-Hant">
      <body>
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
          <div className="p-8 bg-white rounded-lg shadow-md max-w-md w-full">
            <h1 className="text-4xl font-bold text-gray-700 mb-4">系統錯誤</h1>
            <p className="text-gray-600 mb-6">
              很抱歉，系統發生了錯誤。我們已記錄此問題並將盡快修復。
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={reset}
                className="px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
              >
                重試
              </button>
              <a
                href="/"
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-100 transition-colors text-center"
              >
                返回首頁
              </a>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
} 