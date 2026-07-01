import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const { question } = await req.json();
  return NextResponse.json({ referenceAnswer: `Use STAR and tie back to JD keywords. Prompt: ${question}` });
}
