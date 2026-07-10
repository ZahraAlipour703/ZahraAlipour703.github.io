/**
 * Site-wide configuration — the single source of truth for SEO.
 *
 * Consumed by the metadata generator, `robots.ts`, `sitemap.ts`, and the
 * JSON-LD structured-data helper. Update the placeholder values per project.
 */
import { publicEnv } from "@/env";

export const siteConfig = {
  name: "Zahra Alipour | Computer Vision Engineer & AI Researcher",
  description:
    "Portfolio of Zahra Alipour — Computer Vision Engineer and AI Researcher working on deep learning, foundation vision models, and multimodal AI.",
  /**
   * Public origin, no trailing slash. Drives canonical URLs, OG tags, the
   * sitemap, and JSON-LD. Set `NEXT_PUBLIC_SITE_URL` in production.
   */
  url: publicEnv.NEXT_PUBLIC_SITE_URL ?? "https://zahraalipour703.github.io",
  /** Default Open Graph / Twitter share image (path under `public/`). */
  ogImage: "/open-graph.png",
  twitterHandle: "@zahraalipour703",
  author: "Zahra Alipour",
  /** Browser theme-color (address bar / PWA). */
  themeColor: "#0a0e14",
} as const;
