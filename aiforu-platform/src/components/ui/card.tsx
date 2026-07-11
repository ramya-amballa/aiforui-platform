import Link from "next/link";
import { cn } from "@/lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  href?: string;
  variant?: "bordered" | "flat";
}

/**
 * Base card primitive. Domain-specific cards (AdvisoryEngagementCard,
 * GovernanceDomainCard, ArticleCard, ResourceCard) compose this rather
 * than duplicating border/padding/hover treatment.
 */
export function Card({ href, variant = "bordered", className, children, ...props }: CardProps) {
  const classes = cn(
    "group relative flex h-full flex-col p-6 sm:p-8 transition-colors duration-DEFAULT",
    variant === "bordered" && "border border-border hover:border-accent",
    variant === "flat" && "bg-surface",
    className,
  );

  if (href) {
    return (
      <Link href={href} className={classes}>
        {children}
      </Link>
    );
  }

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
}

export function CardEyebrow({ className, ...props }: React.HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn("text-eyebrow uppercase tracking-widest text-muted", className)}
      {...props}
    />
  );
}

export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={cn("mt-3 font-serif text-title text-ink group-hover:text-accent", className)}
      {...props}
    />
  );
}

export function CardDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("mt-3 text-sm leading-relaxed text-muted", className)} {...props} />;
}

export function CardFooter({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("mt-6 pt-6 border-t border-border", className)} {...props} />;
}
