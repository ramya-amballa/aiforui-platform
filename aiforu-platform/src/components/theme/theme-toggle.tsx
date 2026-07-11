"use client";

import { useTheme } from "@/components/theme/theme-provider";

const OPTIONS: { value: "light" | "dark" | "system"; label: string }[] = [
  { value: "light", label: "Light" },
  { value: "dark", label: "Dark" },
  { value: "system", label: "System" },
];

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  const cycleTheme = () => {
    const currentIndex = OPTIONS.findIndex((option) => option.value === theme);
    const next = OPTIONS[(currentIndex + 1) % OPTIONS.length];
    if (next) setTheme(next.value);
  };

  return (
    <button
      type="button"
      onClick={cycleTheme}
      aria-label={`Theme: ${theme}. Activate to change theme.`}
      className="inline-flex items-center gap-2 rounded-xs border border-border px-3 py-1.5 text-eyebrow uppercase tracking-widest text-muted transition-colors hover:border-accent hover:text-ink"
    >
      <span aria-hidden className="block h-1.5 w-1.5 rounded-full bg-accent" />
      {theme}
    </button>
  );
}
