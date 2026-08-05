"use client";

import Link from "next/link";
import { useState } from "react";
import { useSearchModal } from "./SearchProvider";

const NAV_LINKS = [
  { href: "/decisions/", label: "Decisions" },
  { href: "/incidents/", label: "Incidents" },
  { href: "/patterns/", label: "Patterns" },
  { href: "/controls/", label: "Controls" },
  { href: "/evidence/", label: "Evidence" },
  { href: "/board-questions/", label: "Board Questions" },
  { href: "/frameworks/", label: "Frameworks" },
  { href: "/graph/", label: "Graph" },
];

export function Header() {
  const { open } = useSearchModal();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-ink-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-[1400px] items-center gap-4 px-4 py-2.5 sm:px-6">
        <Link href="/" className="flex items-center gap-2 flex-shrink-0">
          <span className="flex h-6 w-6 items-center justify-center rounded bg-ink-900 text-[11px] font-bold text-white">
            AI
          </span>
          <span className="hidden text-sm font-semibold text-ink-900 sm:inline">Governance Workbench</span>
        </Link>

        <nav className="hidden flex-1 items-center gap-1 lg:flex">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded px-2.5 py-1.5 text-sm font-medium text-ink-600 hover:bg-ink-50 hover:text-ink-900"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => open()}
            className="hidden items-center gap-2 rounded border border-ink-200 bg-white px-2.5 py-1.5 text-sm text-ink-400 hover:border-ink-300 hover:text-ink-600 sm:flex"
          >
            <svg className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="none" stroke="currentColor">
              <circle cx="9" cy="9" r="6" strokeWidth="1.5" />
              <path d="M17 17l-4-4" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
            <span>Search</span>
            <kbd className="rounded border border-ink-200 bg-ink-50 px-1 text-[10px]">⌘K</kbd>
          </button>
          <button
            onClick={() => open()}
            aria-label="Search"
            className="flex h-8 w-8 items-center justify-center rounded border border-ink-200 text-ink-500 sm:hidden"
          >
            <svg className="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor">
              <circle cx="9" cy="9" r="6" strokeWidth="1.5" />
              <path d="M17 17l-4-4" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </button>
          <button
            onClick={() => setMobileOpen((v) => !v)}
            aria-label="Menu"
            className="flex h-8 w-8 items-center justify-center rounded border border-ink-200 text-ink-500 lg:hidden"
          >
            <svg className="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor">
              <path d="M3 5h14M3 10h14M3 15h14" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      </div>

      {mobileOpen && (
        <nav className="border-t border-ink-200 px-4 py-2 lg:hidden">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setMobileOpen(false)}
              className="block rounded px-2 py-2 text-sm font-medium text-ink-700 hover:bg-ink-50"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  );
}
