import { Footer } from "@/components/layout/footer";
import { Header } from "@/components/layout/header";

export function SiteShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:bg-ink focus:px-4 focus:py-2 focus:text-paper"
      >
        Skip to content
      </a>
      <Header />
      <main id="main-content">{children}</main>
      <Footer />
    </>
  );
}
