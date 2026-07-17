import type { Metadata } from "next";
import { PageHero } from "@/components/sections/page-hero";
import { Container } from "@/components/ui/container";
import { buildMetadata } from "@/lib/metadata";
import { site } from "@/lib/constants";

export const metadata: Metadata = buildMetadata({
  title: "Privacy Policy",
  description: "How AIforU&I collects, uses and protects information submitted through this website.",
  path: "/privacy-policy",
});

export default function PrivacyPolicyPage() {
  return (
    <>
      <PageHero eyebrow="Legal" title="Privacy Policy" description="Last updated July 2026." size="compact" />
      <section className="py-section">
        <Container size="narrow" className="space-y-10">
          <div className="space-y-4">
            <h2 className="font-serif text-title text-ink">What this covers</h2>
            <p className="text-base leading-relaxed text-muted pretty">
              This policy explains how {site.name}, the advisory practice of {site.advisorName}, handles
              information collected through {site.url}. It applies to this website only, not to information
              shared separately during an advisory engagement, which is governed by the terms agreed for that
              engagement.
            </p>
          </div>

          <div className="space-y-4">
            <h2 className="font-serif text-title text-ink">Information collected</h2>
            <ul className="space-y-3 text-base leading-relaxed text-muted pretty">
              <li>
                <strong className="text-ink">Contact form.</strong> When you submit the contact form, your
                name, email address, and any organisation, role or message you provide are sent by email to{" "}
                {site.advisorName}. This information is not stored in a database on this site; it exists only
                in that email exchange, so it can be deleted by deleting the email.
              </li>
              <li>
                <strong className="text-ink">Theme preference.</strong> If you switch between light and dark
                mode, that choice is saved in your browser&apos;s local storage. It is not transmitted
                anywhere and cannot identify you.
              </li>
              <li>
                <strong className="text-ink">Hosting logs.</strong> Like most websites, this site is hosted on
                infrastructure (Vercel) that keeps standard server logs, such as IP address, browser type and
                request timestamps, for security and reliability purposes. These logs are not used for
                advertising or combined with other data to build a profile of you.
              </li>
            </ul>
          </div>

          <div className="space-y-4">
            <h2 className="font-serif text-title text-ink">What is not collected</h2>
            <p className="text-base leading-relaxed text-muted pretty">
              This site does not use advertising cookies, third-party tracking scripts or analytics that
              profile individual visitors. It does not sell or share visitor information with third parties.
            </p>
          </div>

          <div className="space-y-4">
            <h2 className="font-serif text-title text-ink">Your choices</h2>
            <p className="text-base leading-relaxed text-muted pretty">
              You can decline to submit the contact form and browse the site without providing any personal
              information. To request that a previous email exchange be deleted, contact {site.advisorName} directly
              using the details on the Contact page.
            </p>
          </div>

          <div className="space-y-4">
            <h2 className="font-serif text-title text-ink">Changes to this policy</h2>
            <p className="text-base leading-relaxed text-muted pretty">
              This policy may be updated as the site changes. The date at the top of this page reflects the
              most recent update.
            </p>
          </div>
        </Container>
      </section>
    </>
  );
}
