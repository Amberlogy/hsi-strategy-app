'use client';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-HK">
      <head>
        <title>恆生指數策略平台 | HSI Strategy App</title>
        <meta name="description" content="恆生指數分析工具" />
      </head>
      <body style={{
        margin: 0,
        padding: 0,
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
        backgroundColor: '#f5f5f5',
      }}>
        <div style={{
          display: 'flex',
        }}>
          <div style={{
            width: '250px',
            height: '100vh',
            backgroundColor: '#1f2937',
            color: 'white',
            padding: '20px',
            position: 'fixed',
            overflowY: 'auto',
          }}>
            <h2 style={{
              fontSize: '20px',
              fontWeight: 'bold',
              marginBottom: '24px',
            }}>HSI Strategy</h2>
            <nav>
              <ul style={{
                listStyle: 'none',
                padding: 0,
                margin: 0,
              }}>
                <li style={{ marginBottom: '8px' }}>
                  <a href="/" style={{
                    display: 'block',
                    padding: '8px 0',
                    color: 'white',
                    textDecoration: 'none',
                  }}>首頁</a>
                </li>
                <li style={{ marginBottom: '8px' }}>
                  <a href="/market-overview" style={{
                    display: 'block',
                    padding: '8px 0',
                    color: 'white',
                    textDecoration: 'none',
                  }}>市場總覽</a>
                </li>
                <li style={{ marginBottom: '8px' }}>
                  <a href="/technical-analysis" style={{
                    display: 'block',
                    padding: '8px 0',
                    color: 'white',
                    textDecoration: 'none',
                  }}>技術分析</a>
                </li>
              </ul>
            </nav>
          </div>
          <main style={{
            flexGrow: 1,
            marginLeft: '250px',
            padding: '20px',
          }}>
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
