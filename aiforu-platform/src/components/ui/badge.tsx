import { cn } from "@/lib/utils";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  tone?: "neutral" | "accent";
}

export function Badge({ tone = "neutral", className, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-xs border px-2.5 py-1 text-eyebrow uppercase tracking-widest",
        tone === "neutral" && "border-border text-muted",
        tone === "accent" && "border-accent/30 bg-accent/5 text-accent",
        className,
      )}
      {...props}
    />
  );
}
