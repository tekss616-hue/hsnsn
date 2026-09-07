import crypto from 'node:crypto';
import { InvestigationMemory } from './memory.js';
import { checkRoleMessage } from './role-guard.js';
import { buildCharacterContext } from './prompt-builder.js';
import { assignRoles, getCharacterForSession, getPlayerRole } from './role-manager.js';

export class CaseEngine {
  constructor({ caseData, roleConfig = {}, provider }) {
    this.caseData = caseData;
    this.roleConfig = roleConfig;
    this.provider = provider;
    this.memory = new InvestigationMemory();
  }

  createSession({ players = [], culpritMode = 'ai' } = {}) {
    const id = crypto.randomUUID();
    const now = Date.now();
    const durationMs = (this.caseData.durationMinutes || 30) * 60 * 1000;
    const roleState = assignRoles({
      players,
      caseData: this.caseData,
      roleConfig: this.roleConfig,
      culpritMode
    });

    const normalizedPlayers = Object.values(roleState.assignments).map((role) => ({
      id: role.playerId,
      name: role.playerName,
      publicRole: role.publicRole
    }));

    const session = {
      id,
      caseId: this.caseData.id,
      players: normalizedPlayers,
      roles: roleState.assignments,
      truth: roleState.sessionTruth,
      culpritMode: roleState.culpritMode,
      originalAiCulpritId: roleState.originalAiCulpritId,
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
      players: session.players,
      culpritPool: session.culpritMode === 'human' ? 'players' : 'characters',
      endsAt: session.endsAt,
      status: session.status
    };
  }

  getPrivateRole({ sessionId, playerId }) {
    const session = this.memory.get(sessionId);
    if (!session) throw new Error('session_not_found');
    const role = getPlayerRole(session, playerId);
    if (!role) throw new Error('player_not_found');
    return {
      caseId: session.caseId,
      sessionId: session.id,
      ...role
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
    if (!session.roles[playerId]) throw new Error('player_not_found');

    const guard = checkRoleMessage(text);
    if (!guard.allowed) {
      session.warnings[playerId] = (session.warnings[playerId] || 0) + 1;
      const reply = 'خلنا داخل القضية. إذا عندك سؤال عن الحادث أو الموجودين هنا، اسأله مباشرة.';
      this.memory.addMessage(sessionId, { speakerType: 'player', speakerId: playerId, targetId: characterId, text });
      this.memory.addMessage(sessionId, { speakerType: 'system', speakerId: 'role-guard', targetId: playerId, text: reply });
      return { reply, blocked: true, warnings: session.warnings[playerId] };
    }

    const character = getCharacterForSession(this.caseData, session, characterId);
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
    if (!session.roles[playerId]) throw new Error('player_not_found');

    const validAi = this.caseData.characters.some((item) => item.id === suspectId);
    const validPlayer = session.players.some((item) => item.id === suspectId);
    if (!validAi && !validPlayer) throw new Error('suspect_not_found');

    session.accusations[playerId] = suspectId;
    const correct = suspectId === session.truth.culpritId;
    return { accepted: true, correct };
  }
}
