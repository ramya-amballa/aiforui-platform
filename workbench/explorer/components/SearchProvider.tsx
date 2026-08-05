"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { SearchModal } from "./SearchModal";

interface SearchContextValue {
  open: (initialQuery?: string) => void;
  close: () => void;
}

const SearchContext = createContext<SearchContextValue | null>(null);

export function useSearchModal(): SearchContextValue {
  const ctx = useContext(SearchContext);
  if (!ctx) throw new Error("useSearchModal must be used within SearchProvider");
  return ctx;
}

export function SearchProvider({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [initialQuery, setInitialQuery] = useState("");

  const open = useCallback((query?: string) => {
    setInitialQuery(query ?? "");
    setIsOpen(true);
  }, []);
  const close = useCallback(() => setIsOpen(false), []);

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      const isMod = e.metaKey || e.ctrlKey;
      if (isMod && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setIsOpen((v) => !v);
      }
      if (e.key === "Escape") setIsOpen(false);
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  return (
    <SearchContext.Provider value={{ open, close }}>
      {children}
      {isOpen && <SearchModal onClose={close} initialQuery={initialQuery} />}
    </SearchContext.Provider>
  );
}
