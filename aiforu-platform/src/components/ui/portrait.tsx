import { cn } from "@/lib/utils";

interface PortraitProps {
  name: string;
  className?: string;
}

/**
 * Neutral fallback for a person's portrait when no photograph is
 * available yet: a monogram on the site's standard panel treatment,
 * not placeholder wording. Swap for a real <Image> once a photo
 * exists; the aria-label stays correct either way.
 */
export function Portrait({ name, className }: PortraitProps) {
  const initials = name
    .split(" ")
    .map((part) => part[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <div
      role="img"
      aria-label={name}
      className={cn("flex aspect-[3/4] items-center justify-center border border-border bg-surface", className)}
    >
      <span aria-hidden className="font-serif text-6xl text-muted">
        {initials}
      </span>
    </div>
  );
}
