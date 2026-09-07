export class InvestigationMemory {
  constructor() {
    this.sessions = new Map();
  }

  create(session) {
    this.sessions.set(session.id, session);
    return session;
  }

  get(id) {
    return this.sessions.get(id) || null;
  }

  addMessage(sessionId, message) {
    const session = this.get(sessionId);
    if (!session) return null;
    session.transcript.push({ ...message, at: Date.now() });
    return session;
  }

  addContradiction(sessionId, item) {
    const session = this.get(sessionId);
    if (!session) return null;
    session.contradictions.push({ ...item, at: Date.now() });
    return session;
  }
}
