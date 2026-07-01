import type { ResumeInput } from '@/lib/ai/schemas';

export function buildResumeSections(resume: ResumeInput) {
  return [
    { title: 'Summary', lines: [resume.basics.summary] },
    ...resume.experience.map((exp) => ({ title: `${exp.title} @ ${exp.company}`, lines: exp.bullets })),
    ...resume.education.map((edu) => ({ title: `${edu.school} - ${edu.degree}`, lines: edu.highlights }))
  ];
}
