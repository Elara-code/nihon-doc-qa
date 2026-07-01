'use client';

import { useFormContext } from 'react-hook-form';

export function BasicsSection() {
  const { register } = useFormContext();
  return (
    <div className="grid gap-2">
      <input className="border p-2" placeholder="Name" {...register('basics.name')} />
      <input className="border p-2" placeholder="Email" {...register('basics.email')} />
      <textarea className="border p-2" placeholder="Summary" {...register('basics.summary')} />
    </div>
  );
}
