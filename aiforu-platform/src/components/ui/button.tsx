import Link from "next/link";
import { cn } from "@/lib/utils";

type ButtonVariant = "primary" | "secondary" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

const baseStyles =
  "inline-flex items-center justify-center gap-2 whitespace-nowrap font-sans font-medium tracking-wide transition-colors duration-DEFAULT disabled:pointer-events-none disabled:opacity-50 rounded-xs";

const variantStyles: Record<ButtonVariant, string> = {
  primary: "bg-ink text-paper hover:bg-accent",
  secondary: "border border-ink text-ink hover:border-accent hover:text-accent",
  ghost: "text-ink underline underline-offset-4 decoration-border hover:decoration-accent hover:text-accent",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "text-sm px-4 py-2",
  md: "text-sm px-5 py-3",
  lg: "text-base px-7 py-4",
};

interface CommonProps {
  variant?: ButtonVariant;
  size?: ButtonSize;
  className?: string;
  children: React.ReactNode;
}

type ButtonAsButton = CommonProps &
  Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, keyof CommonProps> & {
    href?: undefined;
  };

type ButtonAsLink = CommonProps &
  Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, keyof CommonProps> & {
    href: string;
  };

type ButtonProps = ButtonAsButton | ButtonAsLink;

/**
 * Renders an <a> via next/link when `href` is provided, otherwise a <button>.
 * Ghost variant is reserved for low-emphasis inline actions ("Read the brief").
 */
export function Button({ variant = "primary", size = "md", className, children, ...props }: ButtonProps) {
  const classes = cn(baseStyles, variantStyles[variant], sizeStyles[size], className);

  if ("href" in props && props.href) {
    const { href, ...anchorProps } = props;
    return (
      <Link href={href} className={classes} {...anchorProps}>
        {children}
      </Link>
    );
  }

  const buttonProps = props as React.ButtonHTMLAttributes<HTMLButtonElement>;
  return (
    <button className={classes} {...buttonProps}>
      {children}
    </button>
  );
}
