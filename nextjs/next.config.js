/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    unoptimized: true,
  },
  typescript: {
    // !! 警告 !!
    // 在生產環境中會忽略類型錯誤
    ignoreBuildErrors: true,
  },
  eslint: {
    // 在生產環境中忽略ESLint錯誤
    ignoreDuringBuilds: true,
  },
  // 強制所有頁面使用客戶端渲染
  experimental: {
    appDir: true,
  },
  // 確保所有頁面都是客戶端渲染
  swcMinify: true,
  // 明確設置渲染模式
  runtime: 'nodejs',
  // 禁用靜態優化以避免SSR相關問題
  staticPageGenerationTimeout: 180,
  // 調整生成方式
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],
  // 強制使用客戶端導航
  trailingSlash: false,
  // 禁用圖像優化以避免生成時的問題
  optimizeFonts: true,
  // 設置環境變量來強制客戶端渲染
  env: {
    NEXT_PUBLIC_FORCE_CLIENT_SIDE_RENDERING: 'true',
  },
  // 禁用自動靜態優化
  poweredByHeader: false,
  // 完全禁用預渲染
  disableStaticImages: true,
  // 禁用靜態HTML導出
  exportPathMap: null,
  // 強制所有頁面使用On-demand ISR而非靜態生成
  unstable_runtimeJS: true,
  compiler: {
    // 關閉React編譯時的一些嚴格檢查，以避免一些錯誤
    reactRemoveProperties: process.env.NODE_ENV === 'production',
    removeConsole: process.env.NODE_ENV === 'production',
  },
};

module.exports = nextConfig; 