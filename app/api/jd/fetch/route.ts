import { NextResponse } from 'next/server';
import { load } from 'cheerio';

export async function POST(req: Request) {
  const { url } = await req.json();
  const resp = await fetch(url, { headers: { 'user-agent': 'Mozilla/5.0 ResumeOptimizerBot/1.0' } });
  if (!resp.ok) {
    return NextResponse.json({ blocked: true, reason: resp.status }, { status: 200 });
  }
  const html = await resp.text();
  const $ = load(html);
  const text = $('main').text() || $('article').text() || $('body').text();
  const normalized = text.replace(/\s+/g, ' ').trim();
  if (normalized.length < 200 || /captcha|verify you are human/i.test(normalized)) {
    return NextResponse.json({ blocked: true });
  }
  return NextResponse.json({ blocked: false, text: normalized.slice(0, 15000) });
}
