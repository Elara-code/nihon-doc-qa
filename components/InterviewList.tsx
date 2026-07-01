'use client';

import { useState } from 'react';
import type { OptimizationResult } from '@/lib/ai/schemas';

export function InterviewList({ questions }: { questions: OptimizationResult['interviewQuestions'] }) {
  const [answers, setAnswers] = useState<Record<string, string>>({});

  return (
    <div className="space-y-3">
      {questions.map((q) => (
        <div key={q.id} className="rounded border p-3">
          <p className="font-medium">{q.question}</p>
          <button
            className="text-sm text-blue-700"
            onClick={async () => {
              const res = await fetch('/api/interview/answer', { method: 'POST', body: JSON.stringify({ question: q.question }) });
              const data = await res.json();
              setAnswers((prev) => ({ ...prev, [q.id]: data.referenceAnswer }));
            }}
          >查看参考答案</button>
          {answers[q.id] ? <p className="mt-2 text-sm">{answers[q.id]}</p> : null}
        </div>
      ))}
    </div>
  );
}
