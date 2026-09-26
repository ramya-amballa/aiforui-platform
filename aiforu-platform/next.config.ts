import type { NextConfig } from "next";

/**
 * True only on a Vercel Production deployment. Preview deployments,
 * local dev, and any other host all fall back to `false` so the
 * X-Robots-Tag header below defaults closed rather than open.
 */
const isProductionDeployment = process.env.VERCEL_ENV === "production";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  eslint: {
    dirs: ["src"],
  },
  async headers() {
    if (isProductionDeployment) return [];

    return [
      {
        source: "/:path*",
        headers: [{ key: "X-Robots-Tag", value: "noindex, nofollow" }],
      },
    ];
  },
  async redirects() {
    return [
      {
        source: "/downloads/case-01-customer-ai-assistant.pdf",
        destination: "/downloads/case-01-case-study-v3.pdf",
        permanent: true,
      },
      {
        source: "/downloads/case-01-evidence-pack-v2.pdf",
        destination: "/downloads/case-01-evidence-pack-v2-1.pdf",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
