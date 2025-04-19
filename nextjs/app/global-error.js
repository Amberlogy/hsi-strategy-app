'use client';

// 這是Next.js的特殊文件，用於捕獲並顯示全局錯誤
// 它必須是客戶端組件
export default function GlobalError({ error, reset }) {
  return (
    <html>
      <body>
        <div>
          <h1>系統錯誤</h1>
          <p>發生了錯誤</p>
          <button onClick={reset}>重試</button>
        </div>
      </body>
    </html>
  );
} 