export class MockProvider {
  async reply(context) {
    const c = context.character;
    const msg = String(context.playerMessage || '').trim();

    if (!msg) return `${c.name}: اسألني عن شيء له علاقة بالقضية.`;

    const lower = msg.toLowerCase();
    if (lower.includes('وين كنت') || lower.includes('أين كنت')) {
      return `${c.name}: ${c.alibi || 'كنت في مكاني المعتاد، وما عندي شيء أضيفه الآن.'}`;
    }

    if (lower.includes('تعرف') || lower.includes('شفت') || lower.includes('رأيت')) {
      const fact = Array.isArray(c.knownFacts) && c.knownFacts.length ? c.knownFacts[0] : null;
      return `${c.name}: ${fact || 'ما شفت شيء أقدر أؤكده.'}`;
    }

    if (c.liePlan?.coverStory) {
      return `${c.name}: ${c.liePlan.coverStory}`;
    }

    return `${c.name}: كلامك واضح، لكن أبي أعرف ليه مركز علي أنا بالذات؟`;
  }
}
