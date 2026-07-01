import { NextResponse } from 'next/server';
import { resumeInputSchema } from '@/lib/ai/schemas';
import { runPipeline } from '@/lib/ai/pipeline';

export async function POST(req: Request) {
  const body = await req.json();
  const resume = resumeInputSchema.parse(body.resume);
  const language = body.language === 'en' ? 'en' : 'zh';
  const result = await runPipeline({ resume, jdRaw: body.jdRaw, language });
  return NextResponse.json(result);
}
