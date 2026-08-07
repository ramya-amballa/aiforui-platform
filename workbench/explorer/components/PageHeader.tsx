export function PageHeader({ title, description, count }: { title: string; description: string; count: number }) {
  return (
    <div className="mb-6 border-b border-ink-200 pb-5">
      <div className="flex items-baseline gap-2">
        <h1 className="text-2xl font-semibold text-ink-900">{title}</h1>
        <span className="text-sm text-ink-400">({count})</span>
      </div>
      <p className="prose-body mt-1.5 max-w-2xl">{description}</p>
    </div>
  );
}
