'use client';

import { useState } from 'react';
import type { OptimizationResult } from '@/lib/ai/schemas';
import { DiffTable } from './DiffTable';
import { InterviewList } from './InterviewList';

export function ResultTabs({ result }: { result: OptimizationResult }) {
  const [tab, setTab] = useState<'resume' | 'changes' | 'interview'>('resume');
  return (
    <div>
      <div className="mb-4 flex gap-2">
        <button onClick={() => setTab('resume')}>简历</button>
        <button onClick={() => setTab('changes')}>修改说明</button>
        <button onClick={() => setTab('interview')}>面试题</button>
      </div>
      {tab === 'resume' && <pre className="rounded border p-3 text-xs">{JSON.stringify(result.optimizedResume, null, 2)}</pre>}
      {tab === 'changes' && <DiffTable changes={result.changes} />}
      {tab === 'interview' && <InterviewList questions={result.interviewQuestions} />}
    </div>
  );
}
