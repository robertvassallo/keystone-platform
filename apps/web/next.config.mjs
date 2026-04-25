/**
 * Next.js configuration.
 *
 * Security headers per docs/01_architecture/security.md. Tighten the CSP once
 * we know the asset origins (Stripe, Sentry, etc.) the first features need.
 */

const INTERNAL_API_URL =
  process.env.INTERNAL_API_URL ?? "http://localhost:8000";

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,

  // Proxy /api/* to Django so the browser sees same-origin (sessions +
  // CSRF cookies travel without CORS gymnastics). In production this is
  // handled at the load balancer / reverse proxy layer.
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${INTERNAL_API_URL}/api/:path*`,
      },
    ];
  },

  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline'",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: https:",
              "connect-src 'self' http://localhost:8000",
              "font-src 'self' data:",
              "frame-ancestors 'none'",
            ].join("; "),
          },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
