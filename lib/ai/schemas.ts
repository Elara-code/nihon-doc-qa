import { z } from 'zod';

export const resumeInputSchema = z.object({
  basics: z.object({
    name: z.string(),
    email: z.string().email(),
    phone: z.string(),
    location: z.string(),
    summary: z.string(),
    links: z.array(z.string().url()).default([])
  }),
  education: z.array(z.object({
    school: z.string(), degree: z.string(), major: z.string(), start: z.string(), end: z.string(),
    gpa: z.string().optional(), highlights: z.array(z.string()).default([])
  })),
  experience: z.array(z.object({
    id: z.string(), company: z.string(), title: z.string(), start: z.string(), end: z.string(),
    location: z.string(), bullets: z.array(z.string())
  })),
  skills: z.array(z.object({ category: z.string(), items: z.array(z.string()) })),
  certifications: z.array(z.object({ name: z.string(), issuer: z.string(), date: z.string(), id: z.string().optional() })),
  projects: z.array(z.object({ name: z.string(), role: z.string(), start: z.string(), end: z.string(), bullets: z.array(z.string()) })).optional(),
  languages: z.array(z.object({ language: z.string(), proficiency: z.string() })).optional()
});

export const jdProfileSchema = z.object({
  title: z.string(),
  company: z.string().optional(),
  location: z.string().optional(),
  seniority: z.string(),
  hardSkills: z.array(z.string()),
  softSkills: z.array(z.string()),
  yearsRequired: z.number().optional(),
  responsibilities: z.array(z.string()),
  keywords: z.array(z.string()),
  niceToHave: z.array(z.string()),
  source: z.enum(['user_pasted', 'url_fetched', 'synthesized'])
});

export const optimizationResultSchema = z.object({
  id: z.string(),
  language: z.enum(['zh', 'en']),
  optimizedResume: resumeInputSchema,
  changes: z.array(z.object({
    section: z.string(), bulletId: z.string().optional(), originalText: z.string(),
    newText: z.string(), reason: z.string(), sourceOfTruth: z.string()
  })),
  matchScore: z.object({
    before: z.number(), after: z.number(),
    byDimension: z.object({ skills: z.number(), experience: z.number(), keywords: z.number() })
  }),
  interviewQuestions: z.array(z.object({
    id: z.string(), category: z.enum(['technical', 'behavioral', 'resume-deep-dive', 'jd-fit']),
    question: z.string(),
    framework: z.object({
      starPoints: z.array(z.string()), keywords: z.array(z.string()), pitfalls: z.array(z.string()), bonus: z.array(z.string())
    }),
    referenceAnswer: z.string().optional()
  }))
});

export type ResumeInput = z.infer<typeof resumeInputSchema>;
export type JDProfile = z.infer<typeof jdProfileSchema>;
export type OptimizationResult = z.infer<typeof optimizationResultSchema>;
