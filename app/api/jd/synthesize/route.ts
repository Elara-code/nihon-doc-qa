import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const { role, city, industry } = await req.json();
  return NextResponse.json({
    title: role,
    location: city,
    company: '',
    seniority: 'mid',
    hardSkills: ['communication', 'problem-solving'],
    softSkills: ['ownership', 'collaboration'],
    responsibilities: [`Deliver ${role} outcomes in ${industry ?? 'target'} domain`],
    keywords: [role, city, industry].filter(Boolean),
    niceToHave: ['cross-functional experience'],
    source: 'synthesized',
    disclaimer: '基于行业通用画像，非真实 JD'
  });
}
