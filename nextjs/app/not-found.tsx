'use client';

export default function NotFound() {
  return (
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
          fontSize: '48px',
          fontWeight: 'bold',
          color: '#333',
          marginBottom: '16px',
        }}>404</h1>
        <h2 style={{
          fontSize: '24px',
          fontWeight: 'bold',
          color: '#444',
          marginBottom: '16px',
        }}>頁面未找到</h2>
        <p style={{
          color: '#666',
          marginBottom: '24px',
        }}>對不起，您要尋找的頁面不存在或已經被移除。</p>
        <a
          href="/"
          style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            padding: '10px 20px',
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
  );
} 