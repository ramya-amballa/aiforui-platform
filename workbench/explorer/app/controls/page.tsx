import { BrowseView } from "@/components/BrowseView";
import { PageHeader } from "@/components/PageHeader";
import { nodesByType } from "@/lib/data";
import { ENTITY_LABEL_PLURAL, ENTITY_DESCRIPTION } from "@/lib/types";

export const metadata = {
  title: "Framework Controls",
  description: ENTITY_DESCRIPTION.control,
  alternates: { canonical: "/controls/" },
};

export default function ControlsPage() {
  const nodes = nodesByType("control");
  return (
    <div>
      <PageHeader title={ENTITY_LABEL_PLURAL.control} description={ENTITY_DESCRIPTION.control} count={nodes.length} />
      <BrowseView type="control" nodes={nodes} />
    </div>
  );
}
