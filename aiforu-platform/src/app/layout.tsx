import type { Metadata } from "next";
import { Fraunces, Inter, IBM_Plex_Mono } from "next/font/google";
import { SiteShell } from "@/components/layout/site-shell";
import { ThemeProvider, themeInitScript } from "@/components/theme/theme-provider";
import { buildMetadata } from "@/lib/metadata";
import { site } from "@/lib/constants";
import "./globals.css";

const editorial = Fraunces({
  subsets: ["latin"],
  variable: "--font-editorial",
  display: "swap",
});

const body = Inter({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  ...buildMetadata({ title: `${site.name}: Independent Advisory in AI and Technology Governance`, path: "/" }),
  metadataBase: new URL(site.url),
  title: {
    default: `${site.name}: Independent Advisory in AI and Technology Governance`,
    template: `%s | ${site.name}`,
  },
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body className={`${editorial.variable} ${body.variable} ${mono.variable} font-sans`}>
        <ThemeProvider>
          <SiteShell>{children}</SiteShell>
        </ThemeProvider>
      </body>
    </html>
  );
}
