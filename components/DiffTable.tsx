import type { OptimizationResult } from '@/lib/ai/schemas';

export function DiffTable({ changes }: { changes: OptimizationResult['changes'] }) {
  return (
    <div className="space-y-2">
      {changes.map((c, i) => (
        <div key={`${c.section}-${i}`} className="rounded border p-3">
          <p className="text-sm text-gray-600">{c.reason}</p>
          <p>{c.originalText}</p>
          <p className="font-semibold">{c.newText}</p>
        </div>
      ))}
    </div>
  );
}
