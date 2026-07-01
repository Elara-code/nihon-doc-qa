import { NextResponse } from 'next/server';
import React from 'react';
import { pdf } from '@react-pdf/renderer';
import { resumeInputSchema } from '@/lib/ai/schemas';
import { ResumePdf } from '@/lib/docs/pdf';

export async function POST(req: Request) {
  const body = await req.json();
  const resume = resumeInputSchema.parse(body.resume);
  const stream = await pdf(React.createElement(ResumePdf, { resume })).toBuffer();
  return new NextResponse(stream, {
    headers: { 'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename="optimized-resume.pdf"' }
  });
}
