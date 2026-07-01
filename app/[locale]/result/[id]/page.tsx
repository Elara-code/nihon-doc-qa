'use client';

import { useEffect, useState } from 'react';
import { ResultTabs } from '@/components/ResultTabs';
import type { OptimizationResult } from '@/lib/ai/schemas';

export default function ResultPage({ params }: { params: { id: string } }) {
  const [result, setResult] = useState<OptimizationResult | null>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem(`result:${params.id}`);
    if (raw) setResult(JSON.parse(raw));
  }, [params.id]);

  if (!result) return <p>Loading...</p>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">结果页</h1>
      <ResultTabs result={result} />
    </div>
  );
}
