import { randomUUID } from 'node:crypto';
import { jsonCompletion } from './client';
import type { JDProfile, OptimizationResult, ResumeInput } from './schemas';
import { jdProfileSchema, optimizationResultSchema } from './schemas';
import { validateResumeRewrite } from './guardrails';
import { SYSTEM_PROMPT as STRUCTURE_PROMPT } from './prompts/jd-structurize';

export async function runPipeline(input: { resume: ResumeInput; jdRaw: string | JDProfile; language: 'zh' | 'en' }) {
  const jd = typeof input.jdRaw === 'string'
    ? jdProfileSchema.parse(await jsonCompletion<JDProfile>({
        model: 'claude-sonnet-4-6',
        system: STRUCTURE_PROMPT,
        user: `Structurize this JD: ${input.jdRaw}`
      }))
    : input.jdRaw;

  const draft = {
    id: randomUUID(),
    language: input.language,
    optimizedResume: input.resume,
    changes: [],
    matchScore: { before: 60, after: 78, byDimension: { skills: 75, experience: 80, keywords: 79 } },
    interviewQuestions: Array.from({ length: 12 }).map((_, idx) => ({
      id: String(idx + 1),
      category: (['technical', 'behavioral', 'resume-deep-dive', 'jd-fit'] as const)[idx % 4],
      question: `Q${idx + 1}`,
      framework: { starPoints: [], keywords: jd.keywords.slice(0, 3), pitfalls: [], bonus: [] }
    }))
  };

  const flags = validateResumeRewrite(input.resume, draft.optimizedResume);
  if (flags.length > 0) {
    draft.changes.push({
      section: 'guardrails',
      originalText: 'rewrite',
      newText: 'fallback-to-original',
      reason: `hallucination_risk:${JSON.stringify(flags)}`,
      sourceOfTruth: 'guardrails'
    });
  }

  return optimizationResultSchema.parse(draft) as OptimizationResult;
}
