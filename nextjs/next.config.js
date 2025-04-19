/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    unoptimized: true
  },
  distDir: '.next',
  typescript: {
    // !! 警告 !!
    // 在生產環境中會忽略類型錯誤
    ignoreBuildErrors: true,
  },
  eslint: {
    // 在生產環境中忽略ESLint錯誤
    ignoreDuringBuilds: true,
  }
};

module.exports = nextConfig; 