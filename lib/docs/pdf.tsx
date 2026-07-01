import { Document, Page, StyleSheet, Text, View } from '@react-pdf/renderer';
import type { ResumeInput } from '@/lib/ai/schemas';
import { buildResumeSections } from './template';

const styles = StyleSheet.create({ page: { padding: 24 }, title: { fontSize: 14, marginBottom: 8 }, line: { fontSize: 10, marginBottom: 4 } });

export function ResumePdf({ resume }: { resume: ResumeInput }) {
  const sections = buildResumeSections(resume);
  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {sections.map((section) => (
          <View key={section.title}>
            <Text style={styles.title}>{section.title}</Text>
            {section.lines.map((line) => (
              <Text key={line} style={styles.line}>{line}</Text>
            ))}
          </View>
        ))}
      </Page>
    </Document>
  );
}
