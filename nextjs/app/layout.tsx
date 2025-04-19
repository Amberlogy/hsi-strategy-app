'use client';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-HK">
      <head>
        <title>恆生指數策略平台</title>
        <meta name="description" content="恆生指數分析工具" />
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}
