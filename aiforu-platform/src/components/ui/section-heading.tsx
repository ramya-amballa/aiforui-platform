import { cn } from "@/lib/utils";

interface SectionHeadingProps {
  eyebrow?: string;
  title: string;
  description?: string;
  align?: "left" | "center";
  className?: string;
}

export function SectionHeading({ eyebrow, title, description, align = "left", className }: SectionHeadingProps) {
  return (
    <div className={cn("max-w-2xl", align === "center" && "mx-auto text-center", className)}>
      {eyebrow ? (
        <p className="text-eyebrow uppercase tracking-widest text-accent">{eyebrow}</p>
      ) : null}
      <h2 className="mt-4 font-serif text-headline text-ink balance">{title}</h2>
      {description ? <p className="mt-4 text-base leading-relaxed text-muted pretty">{description}</p> : null}
    </div>
  );
}
