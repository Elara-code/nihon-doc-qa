'use client';

import { useState } from 'react';

export function JDInput({ onChange }: { onChange: (value: string) => void }) {
  const [value, setValue] = useState('');
  return (
    <div className="space-y-2">
      <textarea
        className="min-h-40 w-full border p-2"
        placeholder="Paste JD text or URL"
        value={value}
        onChange={(e) => {
          setValue(e.target.value);
          onChange(e.target.value);
        }}
      />
    </div>
  );
}
