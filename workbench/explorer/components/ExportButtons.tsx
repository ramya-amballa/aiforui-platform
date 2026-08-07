"use client";

import type { GraphNode } from "@/lib/types";
import { downloadMarkdown } from "@/lib/markdown";

export function ExportButtons({ node }: { node: GraphNode }) {
  return (
    <div className="no-print flex items-center gap-2">
      <button onClick={() => downloadMarkdown(node)} className="btn">
        <svg className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="none" stroke="currentColor">
          <path d="M10 3v10m0 0l-4-4m4 4l4-4M4 16.5h12" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        Export Markdown
      </button>
      <button onClick={() => window.print()} className="btn">
        <svg className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="none" stroke="currentColor">
          <path
            d="M5 8V3h10v5M5 15H3.5A1.5 1.5 0 012 13.5v-4A1.5 1.5 0 013.5 8h13A1.5 1.5 0 0118 9.5v4a1.5 1.5 0 01-1.5 1.5H15m-10 0v3.5h10V15m-10 0h10"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        Print / PDF
      </button>
    </div>
  );
}
