import Link from "next/link";
import { BlueprintPanel } from "@/components/sections/blueprint-panel";
import { Container } from "@/components/ui/container";

/**
 * The homepage's ADGL band: the flagship-methodology entry point,
 * placed immediately below the Hero and before any services or OPERA
 * content so a visitor deploying AI understands within seconds who to
 * talk to before production. Reuses BlueprintPanel's ink tone (the
 * same dark, gold-accented panel used once before on the About page)
 * rather than introducing a new visual treatment, so this reads as
 * "impossible to miss" through weight and contrast alone, not through
 * a new colour, gradient or SaaS-style banner.
 */
export function AdglBand() {
  return (
    <section className="border-b border-border py-section-sm">
      <Container size="wide">
        <BlueprintPanel tone="ink" className="p-8 sm:p-10 lg:p-14">
          <p className="text-eyebrow uppercase tracking-[0.25em] text-brand-gold">AI Deployment Governance</p>
          <div className="mt-4 h-px w-16 bg-brand-gold" />

          <h2 className="mt-8 font-serif text-headline text-brand-paper balance">Deploying AI?</h2>
          <p className="mt-3 font-serif text-title text-brand-paper/90 balance">
            Govern it before it reaches production.
          </p>

          <p className="mt-8 max-w-2xl text-base leading-relaxed text-brand-muted pretty">
            The AI Deployment Governance Lifecycle (ADGL) is AI for U&amp;I&rsquo;s practical methodology for
            governing AI deployments, from business request through production readiness and ongoing
            operational governance.
          </p>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-brand-muted pretty">
            Whether you&rsquo;re deploying Microsoft Copilot, ChatGPT Enterprise, RAG applications, customer
            support assistants or Agentic AI, ADGL provides the governance blueprint before deployment.
          </p>

          <div className="mt-10 flex flex-wrap items-center gap-x-8 gap-y-4 border-t border-brand-paper/10 pt-8">
            <Link
              href="/adgl"
              className="inline-flex items-center justify-center gap-2 rounded-xs bg-brand-gold px-7 py-4 text-base font-medium tracking-wide text-brand-ink transition-colors duration-DEFAULT hover:bg-brand-paper"
            >
              Explore ADGL
            </Link>
            <Link
              href="/downloads/adgl-methodology.pdf"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-brand-paper underline underline-offset-4 decoration-brand-paper/30 hover:text-brand-gold hover:decoration-brand-gold"
            >
              Download Methodology (PDF) &rarr;
            </Link>
          </div>
        </BlueprintPanel>
      </Container>
    </section>
  );
}
