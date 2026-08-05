import type { Metadata } from "next";
import "./globals.css";
import { SearchProvider } from "@/components/SearchProvider";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "AI Governance Workbench",
  description: "The open knowledge graph for AI governance decisions.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <SearchProvider>
          <Header />
          <main className="mx-auto max-w-[1400px] px-4 py-8 sm:px-6">{children}</main>
          <footer className="no-print border-t border-ink-200 mt-16">
            <div className="mx-auto max-w-[1400px] px-4 py-6 text-xs text-ink-400 sm:px-6">
              AI Governance Workbench — a data-first, git-native knowledge graph for AI governance. The knowledge
              graph is the product; this Explorer is one view onto it.
            </div>
          </footer>
        </SearchProvider>
      </body>
    </html>
  );
}
