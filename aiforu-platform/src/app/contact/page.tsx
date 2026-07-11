import type { Metadata } from "next";
import { ContactForm } from "@/components/contact/contact-form";
import { Container } from "@/components/ui/container";
import { Eyebrow } from "@/components/ui/eyebrow";
import { buildMetadata } from "@/lib/metadata";

export const metadata: Metadata = buildMetadata({
  title: "Contact",
  description: "[Contact — Meta Description Placeholder]",
  path: "/contact",
});

export default function ContactPage() {
  return (
    <section className="py-section">
      <Container size="wide">
        <div className="grid grid-cols-1 gap-16 lg:grid-cols-12">
          <div className="lg:col-span-5">
            <Eyebrow>Start a Conversation</Eyebrow>
            <h1 className="mt-6 font-serif text-display text-ink balance">[Contact Page Title Placeholder]</h1>
            <p className="mt-6 max-w-md text-base leading-relaxed text-muted pretty">
              [Contact — Introductory Description Placeholder]
            </p>

            <dl className="mt-12 space-y-6 border-t border-border pt-8">
              <div>
                <dt className="text-eyebrow uppercase tracking-widest text-muted">Direct</dt>
                <dd className="mt-2 text-sm text-ink">[Direct Email Placeholder]</dd>
              </div>
              <div>
                <dt className="text-eyebrow uppercase tracking-widest text-muted">LinkedIn</dt>
                <dd className="mt-2 text-sm text-ink">[LinkedIn Profile Placeholder]</dd>
              </div>
              <div>
                <dt className="text-eyebrow uppercase tracking-widest text-muted">Response Time</dt>
                <dd className="mt-2 text-sm text-ink">[Response Time Placeholder]</dd>
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
