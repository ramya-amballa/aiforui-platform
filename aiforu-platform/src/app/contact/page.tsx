import type { Metadata } from "next";
import { ContactForm } from "@/components/contact/contact-form";
import { Container } from "@/components/ui/container";
import { Eyebrow } from "@/components/ui/eyebrow";
import { buildMetadata } from "@/lib/metadata";

export const metadata: Metadata = buildMetadata({
  title: "Contact",
  description: "Start a conversation about a specific AI governance, technology risk or third-party governance challenge.",
  path: "/contact",
});

export default function ContactPage() {
  return (
    <section className="py-section">
      <Container size="wide">
        <div className="grid grid-cols-1 gap-16 lg:grid-cols-12">
          <div className="lg:col-span-5">
            <Eyebrow>Start a Conversation</Eyebrow>
            <h1 className="mt-6 font-serif text-display text-ink balance">Let&apos;s discuss the problem, not a proposal.</h1>
            <p className="mt-6 max-w-md text-base leading-relaxed text-muted pretty">
              Share what you&apos;re working through: an AI governance decision, a technology risk gap, a
              third-party governance question, or something that does not fit neatly into a category yet.
            </p>

            <dl className="mt-12 space-y-6 border-t border-border pt-8">
              <div>
                <dt className="text-eyebrow uppercase tracking-widest text-muted">Response Time</dt>
                <dd className="mt-2 text-sm text-ink">Replies are sent directly, typically within a few business days.</dd>
              </div>
            </dl>
          </div>

          <div className="lg:col-span-6 lg:col-start-7">
            <ContactForm />
          </div>
        </div>
      </Container>
    </section>
  );
}
