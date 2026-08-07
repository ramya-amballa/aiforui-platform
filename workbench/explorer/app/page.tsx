import Link from "next/link";
import type { Metadata } from "next";
import { EntityCard } from "@/components/EntityCard";
import { HomeQueryChips } from "@/components/HomeQueryChips";
import { graph } from "@/lib/data";
import { ENTITY_TYPES } from "@/lib/types";

export const metadata: Metadata = {
  alternates: { canonical: "/" },
};

export default function HomePage() {
  const totalObjects = graph.nodes.length;
  const totalRelationships = graph.nodes.reduce((sum, n) => sum + n.relationships_out.length, 0);
  const totalIncidents = graph.counts.incident;

  return (
    <div>
      <section className="border-b border-ink-200 pb-10">
        <div className="max-w-3xl">
          <h1 className="text-3xl font-semibold tracking-tight text-ink-900 sm:text-4xl">AI Governance Workbench</h1>
          <p className="mt-3 text-lg text-ink-600">The open knowledge graph for AI governance decisions.</p>
          <p className="prose-body mt-4 max-w-2xl">
            A practitioner reference built from real, independently-verified incidents, mapped to the governance
            decisions, design patterns, framework controls, evidence, and board questions that follow from them.
            Every relationship is typed and carries an explicit reason. Nothing here is AI-generated speculation —
            it is a curated, citable dataset with an interactive way to explore it.
          </p>
          <p className="mt-4 text-sm text-ink-500">
            Every canonical object is version-controlled, human-reviewed, and validated against deterministic
            quality standards before publication.{" "}
            <Link href="/standards/" className="text-accent-600 hover:underline">
              See our standards →
            </Link>
          </p>

          <div className="mt-6">
            <HomeQueryChips />
          </div>
        </div>

        <dl className="mt-8 grid grid-cols-3 gap-6 sm:max-w-md">
          <div>
            <dt className="field-label">Canonical objects</dt>
            <dd className="mt-1 text-2xl font-semibold tabular-nums text-ink-900">{totalObjects}</dd>
          </div>
          <div>
            <dt className="field-label">Incidents</dt>
            <dd className="mt-1 text-2xl font-semibold tabular-nums text-ink-900">{totalIncidents}</dd>
          </div>
          <div>
            <dt className="field-label">Relationships</dt>
            <dd className="mt-1 text-2xl font-semibold tabular-nums text-ink-900">{totalRelationships}</dd>
          </div>
        </dl>
      </section>

      <section className="mt-10">
        <h2 className="section-heading">Browse the graph</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {ENTITY_TYPES.map((type) => (
            <EntityCard key={type} type={type} count={graph.counts[type]} />
          ))}
        </div>
      </section>
    </div>
  );
}
