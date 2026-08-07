import type { MetadataRoute } from "next";

export const dynamic = "force-static";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "AI Governance Workbench",
    short_name: "AI Gov Workbench",
    description:
      "An open, practitioner-built knowledge graph connecting real AI governance incidents to the decisions, patterns, controls, evidence, and board questions they imply.",
    start_url: "/",
    display: "standalone",
    background_color: "#ffffff",
    theme_color: "#171c27",
    icons: [
      { src: "/favicon.ico", sizes: "16x16 32x32", type: "image/x-icon" },
      { src: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
    ],
  };
}
