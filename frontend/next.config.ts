import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // Proxy API calls to the FastAPI backend during local dev, so the
    // browser can call same-origin `/api/v1/...` instead of hardcoding
    // http://localhost:8000 everywhere. In production, set
    // NEXT_PUBLIC_API_URL and this proxy is not used.
    return [
      {
        source: "/api/v1/:path*",
        destination: "http://localhost:8000/api/v1/:path*",
      },
    ];
  },
};

export default nextConfig;
