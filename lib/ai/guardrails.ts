import type { ResumeInput } from './schemas';

const tokenRegex = /[A-Za-z][A-Za-z0-9+.#-]*|\d+(?:[.,]\d+)?%?/g;

function collectTokens(lines: string[]): Set<string> {
  return new Set((lines.join(' ').match(tokenRegex) ?? []).map((t) => t.toLowerCase()));
}

export function detectHallucination(source: string[], rewritten: string[], knownSkills: string[] = []) {
  const sourceTokens = collectTokens([...source, ...knownSkills]);
  const rewrittenTokens = collectTokens(rewritten);
  const unknown = [...rewrittenTokens].filter((t) => !sourceTokens.has(t));
  return {
    risk: unknown.length > 0,
    unknown
  };
}

export function validateResumeRewrite(input: ResumeInput, output: ResumeInput) {
  const skillUnion = input.skills.flatMap((s) => s.items);
  const flags: Array<{ expId: string; unknown: string[] }> = [];
  output.experience.forEach((exp) => {
    const source = input.experience.find((item) => item.id === exp.id);
    if (!source) return;
    const result = detectHallucination(source.bullets, exp.bullets, skillUnion);
    if (result.risk) flags.push({ expId: exp.id, unknown: result.unknown });
  });
  return flags;
}
