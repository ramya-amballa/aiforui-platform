import { cn } from "@/lib/utils";

interface BlueprintPanelProps {
  children: React.ReactNode;
  className?: string;
  tone?: "paper" | "ink";
}

/**
 * The site's enterprise-architecture "blueprint" treatment: a fine
 * grid plus corner brackets, built from the existing design tokens
 * (--color-border for the grid, --color-signal for the brackets), not
 * a new color system. Used for identity/brand surfaces (hero panels,
 * the founder mark, the About portfolio hero) rather than as general
 * page decoration, per the "every graphic must explain or demonstrate
 * OPERA" rule: this frames the practice's own content, it doesn't
 * replace it with generic illustration.
 *
 * `tone="ink"` inverts to a dark panel for higher-contrast identity
 * moments; `tone="paper"` (default) stays within the light page.
 */
export function BlueprintPanel({ children, className, tone = "paper" }: BlueprintPanelProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden border",
        tone === "paper" && "border-border bg-surface",
        tone === "ink" && "border-brand-ink bg-brand-ink",
        className,
      )}
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.35]"
        style={{
          backgroundImage:
            tone === "paper"
              ? "linear-gradient(to right, hsl(var(--color-border)) 1px, transparent 1px), linear-gradient(to bottom, hsl(var(--color-border)) 1px, transparent 1px)"
              : "linear-gradient(to right, hsl(var(--color-brand-paper) / 0.15) 1px, transparent 1px), linear-gradient(to bottom, hsl(var(--color-brand-paper) / 0.15) 1px, transparent 1px)",
          backgroundSize: "28px 28px",
        }}
      />
      {["left-0 top-0 border-l-2 border-t-2", "right-0 top-0 border-r-2 border-t-2", "left-0 bottom-0 border-b-2 border-l-2", "right-0 bottom-0 border-b-2 border-r-2"].map(
        (position) => (
          <span
            key={position}
            aria-hidden
            className={cn("absolute h-4 w-4", tone === "paper" ? "border-signal" : "border-brand-gold", position)}
          />
        ),
      )}
      <div className="relative">{children}</div>
    </div>
  );
}
