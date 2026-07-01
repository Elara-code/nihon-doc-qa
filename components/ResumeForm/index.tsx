'use client';

import { FormProvider, useForm } from 'react-hook-form';
import { BasicsSection } from './BasicsSection';
import type { ResumeInput } from '@/lib/ai/schemas';

export function ResumeForm({ onSubmit }: { onSubmit: (data: ResumeInput) => void }) {
  const methods = useForm<ResumeInput>({
    defaultValues: {
      basics: { name: '', email: '', phone: '', location: '', summary: '', links: [] },
      education: [], experience: [], skills: [], certifications: []
    }
  });

  return (
    <FormProvider {...methods}>
      <form className="space-y-4" onSubmit={methods.handleSubmit(onSubmit)}>
        <BasicsSection />
        <button className="rounded bg-black px-3 py-2 text-white" type="submit">Submit Resume</button>
      </form>
    </FormProvider>
  );
}
