import { BrowseView } from "@/components/BrowseView";
import { PageHeader } from "@/components/PageHeader";
import { nodesByType } from "@/lib/data";
import { ENTITY_LABEL_PLURAL, ENTITY_DESCRIPTION } from "@/lib/types";

export const metadata = { title: "Governance Decisions — AI Governance Workbench" };

export default function DecisionsPage() {
  const nodes = nodesByType("decision");
  return (
    <div>
      <PageHeader title={ENTITY_LABEL_PLURAL.decision} description={ENTITY_DESCRIPTION.decision} count={nodes.length} />
      <BrowseView type="decision" nodes={nodes} />
    </div>
  );
}
