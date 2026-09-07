import crypto from 'node:crypto';
import { InvestigationMemory } from './memory.js';
import { checkRoleMessage } from './role-guard.js';
import { buildCharacterContext } from './prompt-builder.js';

export class CaseEngine {
  constructor({ caseData, provider }) {
    this.caseData = caseData;
    this.provider = provider;
    this.memory = new InvestigationMemory();
  }

  createSession({ players = [] } = {}) {
    const id = crypto.randomUUID();
    const now = Date.now();
    const durationMs = (this.caseData.durationMinutes || 30) * 60 * 1000;
    const session = {
      id,
      caseId: this.caseData.id,
      players,
      createdAt: now,
      endsAt: now + durationMs,
      transcript: [],
      contradictions: [],
      warnings: {},
      accusations: {},
      status: 'active'
    };
    return this.memory.create(session);
  }

  getPublicSession(sessionId) {
    const session = this.memory.get(sessionId);
    if (!session) return null;
    return {
      id: session.id,
      caseId: session.caseId,
      title: this.caseData.title,
      briefing: this.caseData.briefing,
      publicFacts: this.caseData.publicFacts,
      suspects: this.caseData.characters.map(({ id, name, role, avatar }) => ({ id, name, role, avatar })),
      endsAt: session.endsAt,
      status: session.status
    };
  }

  async ask({ sessionId, playerId, characterId, text }) {
    const session = this.memory.get(sessionId);
    if (!session) throw new Error('session_not_found');
    if (session.status !== 'active') throw new Error('session_closed');
    if (Date.now() > session.endsAt) {
      session.status = 'finished';
      throw new Error('time_expired');
    }

    const guard = checkRoleMessage(text);
    if (!guard.allowed) {
      session.warnings[playerId] = (session.warnings[playerId] || 0) + 1;
      const reply = 'خلنا داخل القضية. إذا عندك سؤال عن الجريمة أو الموجودين هنا، اسأله مباشرة.';
      this.memory.addMessage(sessionId, { speakerType: 'player', speakerId: playerId, targetId: characterId, text });
      this.memory.addMessage(sessionId, { speakerType: 'system', speakerId: 'role-guard', targetId: playerId, text: reply });
      return { reply, blocked: true, warnings: session.warnings[playerId] };
    }

    const character = this.caseData.characters.find((item) => item.id === characterId);
    if (!character) throw new Error('character_not_found');

    this.memory.addMessage(sessionId, { speakerType: 'player', speakerId: playerId, targetId: characterId, text });
    const context = buildCharacterContext({ caseData: this.caseData, character, session, playerMessage: text });
    const reply = await this.provider.reply(context);
    this.memory.addMessage(sessionId, { speakerType: 'character', speakerId: characterId, targetId: playerId, text: reply });
    return { reply, blocked: false, warnings: session.warnings[playerId] || 0 };
  }

  accuse({ sessionId, playerId, suspectId }) {
    const session = this.memory.get(sessionId);
    if (!session) throw new Error('session_not_found');
    const valid = this.caseData.characters.some((item) => item.id === suspectId);
    if (!valid) throw new Error('suspect_not_found');

    session.accusations[playerId] = suspectId;
    const correct = suspectId === this.caseData.truth.culpritId;
    return { accepted: true, correct };
  }
}
