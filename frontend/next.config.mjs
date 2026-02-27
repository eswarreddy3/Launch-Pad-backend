const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Proxy /api/v1/* → Django backend
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${API_URL}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
