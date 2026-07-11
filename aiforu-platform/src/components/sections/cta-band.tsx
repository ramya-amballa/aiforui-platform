import { Button } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { primaryCta, secondaryCta } from "@/lib/constants";

interface CtaBandProps {
  title?: string;
  description?: string;
}

/**
 * Closing conversion section used at the base of most pages, surfacing
 * both the primary and secondary calls to action.
 */
export function CtaBand({
  title = "[Closing CTA Title Placeholder]",
  description = "[Closing CTA Description Placeholder]",
}: CtaBandProps) {
  return (
    <section className="border-t border-border py-section-sm">
      <Container size="wide">
        <div className="flex flex-col items-start justify-between gap-8 lg:flex-row lg:items-end">
          <div className="max-w-xl">
            <h2 className="font-serif text-headline text-ink balance">{title}</h2>
            <p className="mt-4 text-base leading-relaxed text-muted">{description}</p>
          </div>
          <div className="flex flex-col gap-4 sm:flex-row">
            <Button href={primaryCta.href} variant="primary" size="lg">
              {primaryCta.label}
            </Button>
            <Button href={secondaryCta.href} variant="secondary" size="lg">
              {secondaryCta.label}
            </Button>
          </div>
        </div>
      </Container>
    </section>
  );
}
