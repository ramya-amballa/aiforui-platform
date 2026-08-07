import { BrowseView } from "@/components/BrowseView";
import { PageHeader } from "@/components/PageHeader";
import { nodesByType } from "@/lib/data";
import { ENTITY_LABEL_PLURAL, ENTITY_DESCRIPTION } from "@/lib/types";

export const metadata = {
  title: "Evidence Types",
  description: ENTITY_DESCRIPTION.evidence,
  alternates: { canonical: "/evidence/" },
};

export default function EvidencePage() {
  const nodes = nodesByType("evidence");
  return (
    <div>
      <PageHeader title={ENTITY_LABEL_PLURAL.evidence} description={ENTITY_DESCRIPTION.evidence} count={nodes.length} />
      <BrowseView type="evidence" nodes={nodes} />
    </div>
  );
}
