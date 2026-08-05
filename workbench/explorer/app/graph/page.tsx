import { GraphView } from "@/components/GraphView";
import { PageHeader } from "@/components/PageHeader";
import { graph } from "@/lib/data";

export const metadata = {
  title: "Graph",
  description: "A supplemental, full-graph visualization of every canonical object and relationship in the AI Governance Workbench.",
  alternates: { canonical: "/graph/" },
};

export default function GraphPage() {
  return (
    <div>
      <PageHeader
        title="Graph"
        description="A supplemental view of the full knowledge graph. Search is the primary way to find something specific; this is for seeing how everything connects."
        count={graph.nodes.length}
      />
      <GraphView />
    </div>
  );
}
