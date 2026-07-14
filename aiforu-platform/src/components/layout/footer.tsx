import Link from "next/link";
import { Container } from "@/components/ui/container";
import { footerNav, site } from "@/lib/constants";

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-border bg-paper">
      <Container size="wide">
        <div className="grid grid-cols-1 gap-12 py-section-sm sm:grid-cols-2 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <Link href="/" className="font-serif text-xl tracking-tight text-ink">
              {site.name}
            </Link>
            <p className="mt-4 max-w-sm text-sm leading-relaxed text-muted">
              Independent advisory practice of {site.advisorName}, built on the OPERA governance methodology.
            </p>
          </div>

          {footerNav.map((column) => (
            <div key={column.title}>
              <p className="text-eyebrow uppercase tracking-widest text-muted">{column.title}</p>
              <ul className="mt-4 space-y-3">
                {column.items.map((item) => (
                  <li key={item.href}>
                    <Link href={item.href} className="text-sm text-ink/80 hover:text-accent">
                      {item.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          <div>
            <p className="text-eyebrow uppercase tracking-widest text-muted">Connect</p>
            <ul className="mt-4 space-y-3">
              <li>
                <a href={`mailto:${site.email}`} className="text-sm text-ink/80 hover:text-accent">
                  {site.email}
                </a>
              </li>
              <li>
                <a href={site.linkedin} target="_blank" rel="noopener noreferrer" className="text-sm text-ink/80 hover:text-accent">
                  LinkedIn
                </a>
              </li>
              <li>
                <Link href="/contact" className="text-sm text-ink/80 hover:text-accent">
                  Start a Conversation
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <p className="text-eyebrow uppercase tracking-widest text-muted">Elsewhere</p>
            <ul className="mt-4 space-y-3">
              <li>
                <a href={site.substack} target="_blank" rel="noopener noreferrer" className="text-sm text-ink/80 hover:text-accent">
                  Substack
                </a>
              </li>
              <li>
                <a href={site.github} target="_blank" rel="noopener noreferrer" className="text-sm text-ink/80 hover:text-accent">
                  GitHub
                </a>
              </li>
              <li>
                <a href={site.gumroad} target="_blank" rel="noopener noreferrer" className="text-sm text-ink/80 hover:text-accent">
                  Gumroad
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="flex flex-col gap-4 border-t border-border py-8 text-xs text-muted sm:flex-row sm:items-center sm:justify-between">
          <p>
            &copy; {year} {site.name}. All rights reserved.
          </p>
          <div className="flex gap-6">
            <Link href="/privacy-policy" className="hover:text-ink">
              Privacy Policy
            </Link>
            <Link href="/terms" className="hover:text-ink">
              Terms
            </Link>
          </div>
        </div>
      </Container>
    </footer>
  );
}
