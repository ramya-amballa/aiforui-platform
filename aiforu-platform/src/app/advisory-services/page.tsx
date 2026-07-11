import type { Metadata } from "next";
import { CtaBand } from "@/components/sections/cta-band";
import { PageHero } from "@/components/sections/page-hero";
import { Container } from "@/components/ui/container";
import { Divider } from "@/components/ui/divider";
import { advisoryServices } from "@/content/advisory-services";
import { buildMetadata } from "@/lib/metadata";

export const metadata: Metadata = buildMetadata({
  title: "Advisory Services",
  description: "[Advisory Services — Meta Description Placeholder]",
  path: "/advisory-services",
});

export default function AdvisoryServicesPage() {
  return (
    <>
      <PageHero
        eyebrow="How We Work"
        title="Advisory Services"
        description="[Advisory Services — Page Description Placeholder]"
      />
      <section className="py-section-sm">
        <Container size="wide">
          <div className="divide-y divide-border border-t border-border">
            {advisoryServices.map((service, index) => (
              <div key={service.slug} className="grid grid-cols-1 gap-6 py-10 lg:grid-cols-12">
                <div className="lg:col-span-1">
                  <span className="font-serif text-sm text-accent">{String(index + 1).padStart(2, "0")}</span>
                </div>
                <div className="lg:col-span-4">
                  <h2 className="font-serif text-title text-ink">{service.name}</h2>
                </div>
                <div className="lg:col-span-4">
                  <p className="text-base leading-relaxed text-muted">{service.summary}</p>
                </div>
                <div className="lg:col-span-3">
                  <p className="text-eyebrow uppercase tracking-widest text-muted">Deliverables</p>
                  <ul className="mt-3 space-y-2">
                    {service.deliverables.map((item) => (
                      <li key={item} className="text-sm text-ink">
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </Container>
      </section>
      <Divider />
      <CtaBand />
    </>
  );
}
