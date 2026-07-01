import { Document, Packer, Paragraph, HeadingLevel } from 'docx';
import type { ResumeInput } from '@/lib/ai/schemas';
import { buildResumeSections } from './template';

export async function renderDocx(resume: ResumeInput) {
  const sections = buildResumeSections(resume).flatMap((s) => [
    new Paragraph({ text: s.title, heading: HeadingLevel.HEADING_2 }),
    ...s.lines.map((line) => new Paragraph(line))
  ]);

  const doc = new Document({ sections: [{ children: sections }] });
  return Packer.toBuffer(doc);
}
