import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          50: "#f7f8f9",
          100: "#eceef1",
          200: "#d7dbe1",
          300: "#b7bfc9",
          400: "#8f99a8",
          500: "#6b7686",
          600: "#4f596b",
          700: "#3c4557",
          800: "#262d3c",
          900: "#171c27",
          950: "#0c0f16",
        },
        accent: {
          50: "#eff5ff",
          100: "#dce8ff",
          200: "#b9d0ff",
          300: "#8badff",
          400: "#5c85f5",
          500: "#3a63d8",
          600: "#2c4bb0",
          700: "#243c8c",
          800: "#1e3170",
          900: "#1a2a5c",
        },
      },
      fontFamily: {
        sans: ["-apple-system", "BlinkMacSystemFont", "Segoe UI", "Helvetica Neue", "Arial", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "monospace"],
      },
      fontSize: {
        xs: ["0.75rem", { lineHeight: "1.1rem" }],
        sm: ["0.8125rem", { lineHeight: "1.25rem" }],
        base: ["0.9375rem", { lineHeight: "1.5rem" }],
      },
    },
  },
  plugins: [],
};

export default config;
