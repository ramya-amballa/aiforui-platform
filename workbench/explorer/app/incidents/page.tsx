import { BrowseView } from "@/components/BrowseView";
import { PageHeader } from "@/components/PageHeader";
import { nodesByType } from "@/lib/data";
import { ENTITY_LABEL_PLURAL, ENTITY_DESCRIPTION } from "@/lib/types";

export const metadata = { title: "Incidents — AI Governance Workbench" };

export default function IncidentsPage() {
  const nodes = nodesByType("incident");
  return (
    <div>
      <PageHeader title={ENTITY_LABEL_PLURAL.incident} description={ENTITY_DESCRIPTION.incident} count={nodes.length} />
      <BrowseView type="incident" nodes={nodes} />
    </div>
  );
}
