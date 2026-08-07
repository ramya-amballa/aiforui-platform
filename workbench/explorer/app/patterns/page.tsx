import { BrowseView } from "@/components/BrowseView";
import { PageHeader } from "@/components/PageHeader";
import { nodesByType } from "@/lib/data";
import { ENTITY_LABEL_PLURAL, ENTITY_DESCRIPTION } from "@/lib/types";

export const metadata = {
  title: "Design Patterns",
  description: ENTITY_DESCRIPTION.pattern,
  alternates: { canonical: "/patterns/" },
};

export default function PatternsPage() {
  const nodes = nodesByType("pattern");
  return (
    <div>
      <PageHeader title={ENTITY_LABEL_PLURAL.pattern} description={ENTITY_DESCRIPTION.pattern} count={nodes.length} />
      <BrowseView type="pattern" nodes={nodes} />
    </div>
  );
}
