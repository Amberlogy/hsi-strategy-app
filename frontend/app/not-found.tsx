export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">404 - 找不到頁面</h1>
        <p className="text-gray-600 mb-4">抱歉，您請求的頁面不存在。</p>
        <a
          href="/"
          className="text-blue-600 hover:text-blue-800 underline"
        >
          返回首頁
        </a>
      </div>
    </div>
  );
}