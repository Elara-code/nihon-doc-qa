import { NextResponse } from 'next/server';
import { resumeInputSchema } from '@/lib/ai/schemas';
import { renderDocx } from '@/lib/docs/docx';

export async function POST(req: Request) {
  const body = await req.json();
  const resume = resumeInputSchema.parse(body.resume);
  const doc = await renderDocx(resume);
  return new NextResponse(doc, {
    headers: {
      'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'Content-Disposition': 'attachment; filename="optimized-resume.docx"'
    }
  });
}
