"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { primaryNav, secondaryCta, site } from "@/lib/constants";
import { cn } from "@/lib/utils";

export function Header() {
  const pathname = usePathname();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-paper/90 backdrop-blur">
      <Container size="wide">
        <div className="flex h-20 items-center justify-between">
          <Link
            href="/"
            className="shrink-0 whitespace-nowrap font-serif text-xl tracking-tight text-ink"
            onClick={() => setIsMenuOpen(false)}
          >
            {site.name}
          </Link>

          <nav aria-label="Primary" className="hidden items-center gap-8 nav:flex">
            {primaryNav.slice(1, -1).map((item) => {
              const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "text-sm tracking-wide text-muted transition-colors hover:text-ink",
                    isActive && "text-ink",
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="hidden items-center gap-4 nav:flex">
            <ThemeToggle />
            <Button href={secondaryCta.href} variant="secondary" size="sm">
              {secondaryCta.label}
            </Button>
          </div>

          <button
            type="button"
            className="inline-flex flex-col gap-1.5 p-2 nav:hidden"
            aria-label="Toggle navigation menu"
            aria-expanded={isMenuOpen}
            onClick={() => setIsMenuOpen((open) => !open)}
          >
            <span className={cn("block h-px w-6 bg-ink transition-transform", isMenuOpen && "translate-y-[3.5px] rotate-45")} />
            <span className={cn("block h-px w-6 bg-ink transition-transform", isMenuOpen && "-translate-y-[3.5px] -rotate-45")} />
          </button>
        </div>
      </Container>

      {isMenuOpen ? (
        <div className="border-t border-border nav:hidden">
          <Container size="wide">
            <nav aria-label="Mobile" className="flex flex-col gap-1 py-6">
              {primaryNav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setIsMenuOpen(false)}
                  className="py-3 text-base text-ink border-b border-border last:border-none"
                >
                  {item.label}
                </Link>
              ))}
              <div className="mt-4 flex items-center justify-between">
                <ThemeToggle />
              </div>
            </nav>
          </Container>
        </div>
      ) : null}
    </header>
  );
}
