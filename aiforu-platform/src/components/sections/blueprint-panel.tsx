import { cn } from "@/lib/utils";

interface BlueprintPanelProps {
  children: React.ReactNode;
  className?: string;
  tone?: "paper" | "ink";
}

/**
 * A plain bordered identity panel, used once on the site: the About
 * page's opening statement. Deliberately undecorated (no grid
 * texture, no corner brackets) so it reads as a quiet pause, not a
 * graphic competing with the words inside it.
 */
export function BlueprintPanel({ children, className, tone = "paper" }: BlueprintPanelProps) {
  return (
    <div
      className={cn(
        "border",
        tone === "paper" && "border-border bg-surface",
        tone === "ink" && "border-brand-ink bg-brand-ink",
        className,
      )}
    >
      {children}
    </div>
  );
}
