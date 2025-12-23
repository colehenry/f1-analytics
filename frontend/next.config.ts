import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "www.formula1.com",
        pathname: "/content/dam/fom-website/**",
      },
      {
        protocol: "https",
        hostname: "media.formula1.com",
        pathname: "/**",
      },
    ],
  },
};

export default nextConfig;
