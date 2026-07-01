import Anthropic from '@anthropic-ai/sdk';

export const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

export async function jsonCompletion<T>({ model, system, user }: { model: string; system: string; user: string }) {
  const message = await anthropic.messages.create({
    model,
    max_tokens: 4096,
    temperature: 0.3,
    system: [{ type: 'text', text: system, cache_control: { type: 'ephemeral' } }],
    messages: [{ role: 'user', content: user }]
  });
  const text = message.content.find((c) => c.type === 'text');
  return JSON.parse(text?.text ?? '{}') as T;
}
