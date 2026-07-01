import '../globals.css';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';

export default async function LocaleLayout({ children }: { children: React.ReactNode }) {
  const messages = await getMessages();
  return (
    <html>
      <body className="mx-auto max-w-5xl p-6">
        <NextIntlClientProvider messages={messages}>{children}</NextIntlClientProvider>
      </body>
    </html>
  );
}
