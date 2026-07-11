import Link from "next/link";
import { Container } from "@/components/ui/container";

interface BreadcrumbsProps {
  items: { label: string; href: string }[];
}

export function Breadcrumbs({ items }: BreadcrumbsProps) {
  return (
    <nav aria-label="Breadcrumb" className="border-b border-border py-4">
      <Container size="wide">
        <ol className="flex flex-wrap items-center gap-2 text-xs text-muted">
          {items.map((item, index) => (
            <li key={item.href} className="flex items-center gap-2">
              {index > 0 ? <span aria-hidden>/</span> : null}
              {index === items.length - 1 ? (
                <span aria-current="page" className="text-ink">
                  {item.label}
                </span>
              ) : (
                <Link href={item.href} className="hover:text-ink">
                  {item.label}
                </Link>
              )}
            </li>
          ))}
        </ol>
      </Container>
    </nav>
  );
}
