/** @type {import('next').NextConfig} */
const path = require('path')

const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['media.api-sports.io'], // For team logos
  },
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
    }
    return config
  },
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL

    // Only add rewrites if API URL is defined
    if (!apiUrl) {
      return []
    }

    return [
      {
        source: '/api/:path*',
        destination: apiUrl + '/:path*',
      },
    ]
  },
}

module.exports = nextConfig
