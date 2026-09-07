function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

export class GameMaster {
  constructor({ directorConfig = {} } = {}) {
    this.config = directorConfig;
  }

  createState({ createdAt, endsAt, players = [] }) {
    return {
      phase: 'investigation', createdAt, endsAt,
      releasedClueIds: [], releasedAnnouncementIds: [], events: [],
      accusationsLocked: false, closedAt: null, results: null,
      contradictionLog: [],
      playerStats: Object.fromEntries(players.map((player) => [player.id, { questions: 0, uniqueTargets: [], blockedMessages: 0 }]))
    };
  }

  pushEvent(session, event) {
    const state = session.gameMaster;
    const entry = { id: `gm-${state.events.length + 1}`, at: Date.now(), ...event };
    state.events.push(entry);
    if (state.events.length > 100) state.events.splice(0, state.events.length - 100);
    return entry;
  }

  sync(session) {
    const now = Date.now();
    const state = session.gameMaster;
    if (!state) return;
    const elapsedSeconds = Math.max(0, Math.floor((now - session.createdAt) / 1000));

    for (const clue of this.config.clues || []) {
      if (elapsedSeconds >= Number(clue.releaseAfterSeconds || 0) && !state.releasedClueIds.includes(clue.id)) {
        state.releasedClueIds.push(clue.id);
        this.pushEvent(session, { type: 'clue', title: clue.title, text: clue.text, clueId: clue.id });
      }
    }

    for (const item of this.config.announcements || []) {
      const trigger = Number(item.releaseAfterSeconds || 0);
      if (elapsedSeconds >= trigger && !state.releasedAnnouncementIds.includes(item.id)) {
        state.releasedAnnouncementIds.push(item.id);
        this.pushEvent(session, { type: item.type || 'announcement', title: item.title || 'مدير القضية', text: item.text });
      }
    }

    if (now >= session.endsAt && session.status === 'active' && state.phase === 'investigation') {
      state.phase = 'accusation';
      state.accusationsLocked = false;
      this.pushEvent(session, { type: 'phase', title: 'انتهى وقت التحقيق', text: 'أغلق التحقيق. ثبّت اتهامك النهائي الآن؛ لن تظهر الحقيقة حتى نهاية الجولة.' });
    }
  }

  getReleasedClues(session) {
    this.sync(session);
    const ids = new Set(session.gameMaster?.releasedClueIds || []);
    return (this.config.clues || []).filter((clue) => ids.has(clue.id)).map(({ id, title, text, type }) => ({ id, title, text, type }));
  }

  getEvents(session, { after = 0 } = {}) {
    this.sync(session);
    return (session.gameMaster?.events || []).filter((event) => event.at > Number(after || 0));
  }

  noteQuestion(session, { playerId, characterId, blocked = false }) {
    const stats = session.gameMaster?.playerStats?.[playerId];
    if (!stats) return;
    stats.questions += 1;
    if (characterId && !stats.uniqueTargets.includes(characterId)) stats.uniqueTargets.push(characterId);
    if (blocked) stats.blockedMessages += 1;
  }

  recordContradiction(session, item) {
    const entry = { id: `contradiction-${session.gameMaster.contradictionLog.length + 1}`, at: Date.now(), ...item };
    session.gameMaster.contradictionLog.push(entry);
    session.contradictions.push(entry);
    this.pushEvent(session, { type: 'contradiction', title: 'تناقض في التحقيق', text: item.publicText || 'تم رصد تناقض جديد في إحدى الشهادات.', contradictionId: entry.id });
    return entry;
  }

  adminBroadcast(session, { title = 'مدير القضية', text, type = 'admin' }) {
    if (!text) throw new Error('announcement_text_required');
    return this.pushEvent(session, { type, title, text });
  }

  canFinalize(session) {
    const playerIds = session.players.map((player) => player.id);
    const allAccused = playerIds.length > 0 && playerIds.every((id) => Boolean(session.accusations[id]));
    return Date.now() >= session.endsAt || allAccused;
  }

  finalize(session) {
    if (session.gameMaster?.results) return session.gameMaster.results;
    if (!this.canFinalize(session)) throw new Error('round_still_active');
    session.status = 'finished'; session.gameMaster.phase = 'finished'; session.gameMaster.accusationsLocked = true; session.gameMaster.closedAt = Date.now();

    const players = session.players.map((player) => {
      const role = session.roles[player.id]; const accusation = session.accusations[player.id] || null;
      const correct = accusation === session.truth.culpritId;
      const stats = session.gameMaster.playerStats[player.id] || { questions: 0, uniqueTargets: [], blockedMessages: 0 };
      const warningCount = session.warnings[player.id] || 0;
      const investigationScore = clamp(Math.min(stats.questions, 12) * 1.5 + Math.min(stats.uniqueTargets.length, 6) * 2, 0, 30);
      const disciplineScore = clamp(10 - warningCount * 2 - stats.blockedMessages, 0, 10);
      const verdictScore = correct ? 60 : 0;
      return { playerId: player.id, playerName: player.name, alignment: role?.alignment || 'investigator', accusation, correct,
        score: Math.round(verdictScore + investigationScore + disciplineScore), investigationScore: Math.round(investigationScore), disciplineScore,
        questions: stats.questions, uniqueTargets: stats.uniqueTargets.length };
    });

    players.sort((a, b) => b.score - a.score);
    const investigatorResults = players.filter((item) => item.alignment !== 'culprit');
    const qualifyingCount = Math.max(1, Math.ceil(investigatorResults.length * Number(this.config.qualifyingFraction || 0.5)));
    const qualifiedIds = new Set(investigatorResults.slice(0, qualifyingCount).filter((item) => item.correct).map((item) => item.playerId));
    if (session.truth.culpritType === 'player') {
      const culpritResult = players.find((item) => item.playerId === session.truth.culpritId);
      if (culpritResult) culpritResult.culpritEscaped = investigatorResults.filter((item) => item.correct).length === 0;
    }
    for (const item of players) item.qualified = qualifiedIds.has(item.playerId);
    session.gameMaster.results = {
      culprit: { type: session.truth.culpritType, id: session.truth.culpritId, name: session.truth.culpritName || null, motive: session.truth.motive, method: session.truth.method, timeline: session.truth.timeline || [] },
      leaderboard: players, qualificationRule: 'Correct verdict required; qualifying investigators are ranked by deterministic investigation and discipline score.', closedAt: session.gameMaster.closedAt
    };
    this.pushEvent(session, { type: 'result', title: 'أغلقت القضية', text: 'تم اعتماد الاتهامات وحساب النتائج. ظهرت الحقيقة الآن.' });
    return session.gameMaster.results;
  }

  getPublicState(session) {
    this.sync(session);
    return { phase: session.gameMaster.phase, status: session.status, endsAt: session.endsAt, releasedClues: this.getReleasedClues(session),
      recentEvents: (session.gameMaster.events || []).slice(-10), accusationCount: Object.keys(session.accusations || {}).length, playerCount: session.players.length,
      allPlayersAccused: session.players.length > 0 && session.players.every((player) => Boolean(session.accusations[player.id])) };
  }
}
