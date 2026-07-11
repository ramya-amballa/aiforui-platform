import { cn } from "@/lib/utils";

interface PlaceholderProps {
  label: string;
  className?: string;
  aspect?: "square" | "video" | "portrait" | "auto";
}

const aspectMap: Record<NonNullable<PlaceholderProps["aspect"]>, string> = {
  square: "aspect-square",
  video: "aspect-video",
  portrait: "aspect-[3/4]",
  auto: "",
};

/**
 * Visual stand-in for imagery, portraits and diagrams that will be
 * supplied in Phase 2. Never use for copy — use inline `[Placeholder]`
 * text for that so content gaps stay searchable.
 */
export function Placeholder({ label, className, aspect = "auto" }: PlaceholderProps) {
  return (
    <div
      role="img"
      aria-label={label}
      className={cn(
        "flex items-center justify-center border border-dashed border-border bg-surface text-center text-eyebrow uppercase tracking-widest text-muted",
        aspectMap[aspect],
        className,
      )}
    >
      <span className="px-4">{label}</span>
    </div>
  );
}

export function TextPlaceholder({ label, className }: { label: string; className?: string }) {
  return <span className={cn("text-muted italic", className)}>[{label}]</span>;
}
