import Link from 'next/link';

const pages = [
  { href: '/', name: '首頁 Home' },
  { href: '/market-overview', name: '市場總覽 Market Overview' },
  { href: '/technical-analysis', name: '技術分析 Technical Analysis' },
  { href: '/candlestick-ai', name: '陰陽燭辨識 Candlestick AI' },
  { href: '/strategy-center', name: '策略中心 Strategy Center' },
  { href: '/forecast-frame', name: '預測框架 Forecast Frame' },
  { href: '/simulation-trade', name: '模擬交易 Simulation Trade' },
  { href: '/dashboard', name: '我的帳戶 Dashboard' },
  { href: '/learn', name: '學習中心 Learn' },
  { href: '/about', name: '關於與聯絡 About / Contact' },
];

export default function Navbar() {
  return (
    <nav className="w-64 h-screen bg-gray-800 text-white p-5 fixed">
      <h2 className="text-xl font-semibold mb-5">HSI Strategy</h2>
      <ul>
        {pages.map((page) => (
          <li key={page.href} className="mb-2">
            <Link href={page.href} className="hover:text-gray-300">
              {page.name}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
} 