import { defineRouting } from 'next-intl/routing';
import { getRequestConfig } from 'next-intl/server';

export const routing = defineRouting({
  locales: ['zh', 'en'],
  defaultLocale: 'zh'
});

export default getRequestConfig(async ({ locale }) => ({
  locale,
  messages: (await import(`./messages/${locale}.json`)).default
}));
