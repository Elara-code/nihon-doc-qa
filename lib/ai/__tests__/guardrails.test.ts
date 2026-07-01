import { describe, expect, it } from 'vitest';
import { detectHallucination } from '@/lib/ai/guardrails';

describe('guardrails', () => {
  it('rejects newly introduced metrics', () => {
    const result = detectHallucination(
      ['Built internal admin dashboard for support team'],
      ['Built internal admin dashboard and improved conversion by 45%']
    );
    expect(result.risk).toBe(true);
  });

  it('rejects unsupported technology inventions', () => {
    const result = detectHallucination(
      ['Developed ETL jobs in Python'],
      ['Developed ETL jobs in Python and Rust'],
      ['Python']
    );
    expect(result.unknown).toContain('rust');
  });
});
