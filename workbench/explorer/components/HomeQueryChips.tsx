"use client";

import { useSearchModal } from "./SearchProvider";

const QUESTIONS = [
  "human oversight",
  "hiring",
  "hallucination",
  "GDPR",
  "facial recognition",
  "board question",
];

export function HomeQueryChips() {
  const { open } = useSearchModal();
  return (
    <div className="flex flex-wrap gap-2">
      {QUESTIONS.map((q) => (
        <button
          key={q}
          onClick={() => open(q)}
          className="rounded-full border border-ink-200 bg-white px-3 py-1.5 text-sm text-ink-600 hover:border-ink-400 hover:text-ink-900"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
