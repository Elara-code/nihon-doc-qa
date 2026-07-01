'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ResumeForm } from '@/components/ResumeForm';
import { JDInput } from '@/components/JDInput';
import type { ResumeInput } from '@/lib/ai/schemas';

export default function OptimizePage() {
  const router = useRouter();
  const [jdRaw, setJdRaw] = useState('');

  const submit = async (resume: ResumeInput) => {
    const res = await fetch('/api/optimize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume, jdRaw, language: 'zh' })
    });
    const data = await res.json();
    sessionStorage.setItem(`result:${data.id}`, JSON.stringify(data));
    router.push(`/zh/result/${data.id}`);
  };

  return (
    <div className="space-y-6">
      <JDInput onChange={setJdRaw} />
      <ResumeForm onSubmit={submit} />
    </div>
  );
}
