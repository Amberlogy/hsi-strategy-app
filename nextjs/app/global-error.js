'use client';

// 這是Next.js的特殊文件，用於捕獲並顯示全局錯誤
// 它必須是客戶端組件
export default function GlobalError({
  error,
  reset,
}) {
  return (
    <html lang="zh-Hant">
      <head>
        <title>系統錯誤</title>
      </head>
      <body>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          padding: '20px',
          backgroundColor: '#f5f5f5',
        }}>
          <div style={{
            maxWidth: '500px',
            width: '100%',
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '30px',
            boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
            textAlign: 'center',
          }}>
            <h1 style={{
              fontSize: '24px',
              fontWeight: 'bold',
              color: '#333',
              marginBottom: '16px',
            }}>系統錯誤</h1>
            <p style={{
              color: '#666',
              marginBottom: '24px',
            }}>很抱歉，系統發生了錯誤。請嘗試重新載入頁面。</p>
            <div>
              <button
                onClick={reset}
                style={{
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  padding: '8px 16px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  marginRight: '8px',
                  fontWeight: '500',
                }}
              >
                重試
              </button>
              <a
                href="/"
                style={{
                  backgroundColor: '#f3f4f6',
                  color: '#374151',
                  border: '1px solid #d1d5db',
                  padding: '8px 16px',
                  borderRadius: '4px',
                  textDecoration: 'none',
                  display: 'inline-block',
                  fontWeight: '500',
                }}
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