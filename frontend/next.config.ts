import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'www.formula1.com',
        pathname: '/content/dam/fom-website/**',
      },
    ],
  },
};

export default nextConfig;
