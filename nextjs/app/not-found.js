export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <div className="p-8 bg-white rounded-lg shadow-md max-w-md w-full">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">頁面未找到</h2>
        <p className="text-gray-600 mb-6">
          很抱歉，您請求的頁面不存在。可能是網址錯誤或該頁面已被移除。
        </p>
        <a
          href="/"
          className="px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors inline-block"
        >
          返回首頁
        </a>
      </div>
    </div>
  );
} 