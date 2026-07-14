import Link from "next/link";
import { Container } from "@/components/ui/container";
import { formatDate } from "@/lib/utils";
import type { CurrentPrioritiesSnapshot } from "@/types";

/**
 * A "now page" style block, signalling an active practice without a
 * news feed or promotional framing. `snapshot.updatedAt` is rendered
 * plainly so the section is self-policing: it looks stale if it is.
 */
export function CurrentPrioritiesSection({ snapshot }: { snapshot: CurrentPrioritiesSnapshot }) {
  return (
    <section className="border-t border-border py-section-sm">
      <Container size="wide">
        <div className="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-md">
            <p className="text-eyebrow uppercase tracking-widest text-accent">Current Advisory Priorities</p>
            <p className="mt-3 text-sm text-muted">
              Updated {formatDate(`${snapshot.updatedAt}-01`)}
            </p>
          </div>
          <ul className="grid flex-1 grid-cols-1 gap-x-8 gap-y-4 sm:grid-cols-2">
            {snapshot.items.map((item) => (
              <li key={item.label} className="flex items-baseline gap-3 border-b border-border pb-4 text-sm text-ink">
                <span aria-hidden className="block h-1 w-1 shrink-0 rounded-full bg-accent" />
                {item.domainSlug ? (
                  <Link href={`/governance-domains/${item.domainSlug}`} className="hover:text-accent">
                    {item.label}
                  </Link>
                ) : (
                  <span>{item.label}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      </Container>
    </section>
  );
}
