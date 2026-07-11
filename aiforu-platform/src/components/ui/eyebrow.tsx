import { cn } from "@/lib/utils";

export function Eyebrow({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <p className={cn("flex items-center gap-2 text-eyebrow uppercase tracking-widest text-accent", className)}>
      <span aria-hidden className="block h-px w-6 bg-accent" />
      {children}
    </p>
  );
}
