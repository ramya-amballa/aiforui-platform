import type { Config } from "tailwindcss";

/**
 * Design tokens are sourced from CSS custom properties (see src/app/globals.css)
 * so that light/dark themes share a single Tailwind scale.
 */
const config: Config = {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: "1.25rem",
        sm: "2rem",
        lg: "3rem",
        xl: "4rem",
      },
    },
    extend: {
      screens: {
        /**
         * The primary nav needs more room than Tailwind's default `xl`
         * (1280px) once it's carrying 7 links plus the logo and CTA;
         * below this the header falls back to the hamburger menu
         * rather than wrapping link text onto multiple lines.
         */
        nav: "1400px",
      },
      colors: {
        paper: "hsl(var(--color-paper) / <alpha-value>)",
        ink: "hsl(var(--color-ink) / <alpha-value>)",
        surface: "hsl(var(--color-surface) / <alpha-value>)",
        border: "hsl(var(--color-border) / <alpha-value>)",
        muted: "hsl(var(--color-muted) / <alpha-value>)",
        accent: "hsl(var(--color-accent) / <alpha-value>)",
        "accent-muted": "hsl(var(--color-accent-muted) / <alpha-value>)",
        signal: "hsl(var(--color-signal) / <alpha-value>)",
        "brand-ink": "hsl(var(--color-brand-ink) / <alpha-value>)",
        "brand-paper": "hsl(var(--color-brand-paper) / <alpha-value>)",
        "brand-muted": "hsl(var(--color-brand-muted) / <alpha-value>)",
        "brand-gold": "hsl(var(--color-brand-gold) / <alpha-value>)",
        "brand-ink-quiet": "hsl(var(--color-brand-ink-quiet) / <alpha-value>)",
      },
      fontFamily: {
        serif: ["var(--font-editorial)", "Georgia", "serif"],
        sans: ["var(--font-body)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      fontSize: {
        "display-lg": ["clamp(2.75rem, 5vw, 5rem)", { lineHeight: "1.04", letterSpacing: "-0.02em" }],
        "display": ["clamp(2.25rem, 4vw, 3.75rem)", { lineHeight: "1.08", letterSpacing: "-0.02em" }],
        "headline": ["clamp(1.75rem, 2.6vw, 2.5rem)", { lineHeight: "1.15", letterSpacing: "-0.01em" }],
        "title": ["clamp(1.375rem, 1.8vw, 1.75rem)", { lineHeight: "1.25" }],
        "eyebrow": ["0.75rem", { lineHeight: "1.4", letterSpacing: "0.14em" }],
      },
      maxWidth: {
        prose: "68ch",
        shell: "88rem",
      },
      spacing: {
        "section-sm": "clamp(3rem, 6vw, 5rem)",
        section: "clamp(5rem, 9vw, 8rem)",
        "section-lg": "clamp(7rem, 12vw, 11rem)",
      },
      borderRadius: {
        xs: "2px",
        sm: "4px",
      },
      transitionDuration: {
        DEFAULT: "180ms",
      },
    },
  },
  plugins: [],
};

export default config;
