import { BrowseView } from "@/components/BrowseView";
import { PageHeader } from "@/components/PageHeader";
import { nodesByType } from "@/lib/data";
import { ENTITY_LABEL_PLURAL, ENTITY_DESCRIPTION } from "@/lib/types";

export const metadata = { title: "Board Questions — AI Governance Workbench" };

export default function BoardQuestionsPage() {
  const nodes = nodesByType("board_question");
  return (
    <div>
      <PageHeader title={ENTITY_LABEL_PLURAL.board_question} description={ENTITY_DESCRIPTION.board_question} count={nodes.length} />
      <BrowseView type="board_question" nodes={nodes} />
    </div>
  );
}
