import Link from "next/link";
import { Container } from "@/components/ui/container";

interface BackLinkProps {
  href: string;
  label: string;
}

/**
 * Quiet wayfinding for the end of a detail/article page, deliberately
 * not a CTA band. A reader who came here to evaluate or verify
 * shouldn't be pushed toward "Start a Conversation" on every page.
 */
export function BackLink({ href, label }: BackLinkProps) {
  return (
    <div className="border-t border-border py-10">
      <Container size="narrow">
        <Link href={href} className="text-sm text-muted hover:text-accent">
          &larr; {label}
        </Link>
      </Container>
    </div>
  );
}
