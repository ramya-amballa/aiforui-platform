import { cn } from "@/lib/utils";

export function Eyebrow({ children, className }: { children: React.ReactNode; className?: string }) {
  return <p className={cn("text-eyebrow uppercase tracking-widest text-accent", className)}>{children}</p>;
}
