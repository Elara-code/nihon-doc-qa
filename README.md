# JD-Driven Resume Optimizer & Interview Prep

A Next.js 15 MVP that optimizes one resume against one target JD and generates JD-aligned interview prep.

## Features (v1)
- Structured resume input form (no file parsing in v1)
- JD input via paste / URL fetch / synthesized role-city profile
- AI pipeline (JD structurize, gap analysis, rewrite, diff explain, interview question generation)
- Hallucination guardrails (prompt + code-level token checks)
- Export optimized resume as DOCX / PDF
- Chinese / English locale support

## Tech Stack
- Next.js 15 + TypeScript + App Router
- Tailwind CSS
- react-hook-form + zod
- Anthropic SDK
- docx + @react-pdf/renderer
- next-intl

## Run
```bash
npm install
npm run dev
```

Set:
```bash
export ANTHROPIC_API_KEY=your_key
```

## Key Paths
- `lib/ai/schemas.ts`: shared contracts
- `lib/ai/pipeline.ts`: pipeline orchestrator
- `lib/ai/guardrails.ts`: anti-hallucination checks
- `app/api/optimize/route.ts`: main orchestration endpoint
- `app/api/export/*`: document exports

## Fixtures
See `fixtures/` for sample resumes and JDs for local demos.
