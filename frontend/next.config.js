/** @type {import('next').NextConfig} */
const nextConfig = {
  // 禁用遥测和版本检查
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  // 图片配置 - 允许加载外部图片
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  // API 代理 - 使用 127.0.0.1 而不是 localhost 避免 IPv6 问题
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8001/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig
