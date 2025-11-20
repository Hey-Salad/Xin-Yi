import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: 'export', // Enable static export for Cloudflare Pages
  images: {
    unoptimized: true, // Required for static export
  },
  // Disable experimental features for CI compatibility
  experimental: {
    turbo: undefined,
  },
  env: {
    NEXT_PUBLIC_SUPABASE_URL: process.env.SUPABASE_URL,
    NEXT_PUBLIC_SUPABASE_KEY: process.env.SUPABASE_KEY,
  },
};

export default nextConfig;
