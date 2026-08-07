import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { SearchProvider } from "@/components/SearchProvider";
import { Header } from "@/components/Header";

const SITE_URL = "https://workbench.aiforui.com";
const SITE_TITLE = "AI Governance Workbench";
const SITE_DESCRIPTION =
  "An open, practitioner-built knowledge graph connecting real AI governance incidents to the decisions, patterns, controls, evidence, and board questions they imply.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: SITE_TITLE,
    template: `%s — ${SITE_TITLE}`,
  },
  description: SITE_DESCRIPTION,
  applicationName: SITE_TITLE,
  authors: [{ name: "AI for U&I" }],
  keywords: [
    "AI governance",
    "AI risk management",
    "AI incidents",
    "NIST AI RMF",
    "EU AI Act",
    "AI governance framework",
    "board oversight of AI",
    "AI compliance",
  ],
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    url: SITE_URL,
    siteName: SITE_TITLE,
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: SITE_TITLE }],
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
    images: ["/og-image.png"],
  },
  icons: {
    icon: [
      { url: "/icon.svg", type: "image/svg+xml" },
      { url: "/favicon.ico", sizes: "any" },
    ],
    apple: "/apple-touch-icon.png",
  },
  manifest: "/manifest.webmanifest",
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <SearchProvider>
          <Header />
          <main className="mx-auto max-w-[1400px] px-4 py-8 sm:px-6">{children}</main>
          <footer className="no-print border-t border-ink-200 mt-16">
            <div className="mx-auto flex max-w-[1400px] flex-col gap-3 px-4 py-6 sm:flex-row sm:items-center sm:justify-between sm:px-6">
              <div className="max-w-2xl">
                <p className="text-xs text-ink-400">
                  AI Governance Workbench — a data-first, git-native knowledge graph for AI governance. The knowledge
                  graph is the product; this Explorer is one view onto it.
                </p>
                <nav aria-label="Trust and legal" className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs">
                  <Link href="/standards/" className="text-ink-500 hover:text-ink-800 hover:underline">
                    Our Standards
                  </Link>
                  <Link href="/sources/" className="text-ink-500 hover:text-ink-800 hover:underline">
                    Source Transparency
                  </Link>
                  <Link href="/corrections/" className="text-ink-500 hover:text-ink-800 hover:underline">
                    Corrections
                  </Link>
                  <Link href="/legal/" className="text-ink-500 hover:text-ink-800 hover:underline">
                    Legal Disclaimer
                  </Link>
                </nav>
              </div>
              <Link
                href="/standards/"
                className="inline-flex flex-shrink-0 items-center gap-1.5 self-start rounded border border-ink-200 bg-ink-50 px-2.5 py-1.5 text-xs font-medium text-ink-600 hover:border-ink-300 hover:bg-white"
              >
                <svg className="h-3.5 w-3.5 text-emerald-600" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.75">
                  <path d="M10 2.5l6 2.2v4.4c0 4-2.6 7.2-6 8.4-3.4-1.2-6-4.4-6-8.4V4.7l6-2.2z" strokeLinejoin="round" />
                  <path d="M7.3 10l1.9 1.9L12.9 8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                Quality Assured
              </Link>
            </div>
          </footer>
        </SearchProvider>
      </body>
    </html>
  );
}
