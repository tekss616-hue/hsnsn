import crypto from 'node:crypto';

function shuffle(items) {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = crypto.randomInt(i + 1);
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function normalizePlayer(player, index) {
  if (typeof player === 'string') return { id: player, name: player };
  return {
    id: player?.id || `player-${index + 1}`,
    name: player?.name || `المحقق ${index + 1}`,
    email: player?.email || null
  };
}

export function assignRoles({ players = [], caseData, roleConfig = {}, culpritMode = 'ai' }) {
  const normalized = players.map(normalizePlayer);
  const mode = culpritMode === 'random'
    ? (normalized.length > 0 && crypto.randomInt(2) === 1 ? 'human' : 'ai')
    : culpritMode;

  if (!['ai', 'human'].includes(mode)) throw new Error('invalid_culprit_mode');
  if (mode === 'human' && normalized.length < 2) throw new Error('human_culprit_requires_two_players');

  const templates = roleConfig.innocentRoles || [];
  const shuffledTemplates = shuffle(templates);
  const shuffledPlayers = shuffle(normalized);
  const humanCulprit = mode === 'human' ? shuffledPlayers[0] : null;
  const culpritCard = roleConfig.humanCulpritRole || null;

  const assignments = {};
  let templateIndex = 0;

  for (const player of normalized) {
    if (humanCulprit && player.id === humanCulprit.id) {
      assignments[player.id] = {
        playerId: player.id,
        playerName: player.name,
        alignment: 'culprit',
        roleName: culpritCard?.roleName || 'شخص داخل القضية',
        publicRole: culpritCard?.publicRole || culpritCard?.roleName || 'شخص داخل القضية',
        privateBriefing: culpritCard?.privateBriefing || 'أنت المسؤول عن الحادث. حافظ على قصتك ولا تعترف بلا سبب مقنع داخل التحقيق.',
        knownFacts: culpritCard?.knownFacts || [],
        secrets: culpritCard?.secrets || [],
        coverStory: culpritCard?.coverStory || null,
        objectives: culpritCard?.objectives || ['تجنب كشف الحقيقة', 'حافظ على اتساق أقوالك']
      };
      continue;
    }

    const template = shuffledTemplates.length
      ? shuffledTemplates[templateIndex++ % shuffledTemplates.length]
      : null;

    assignments[player.id] = {
      playerId: player.id,
      playerName: player.name,
      alignment: 'investigator',
      roleName: template?.roleName || 'شاهد',
      publicRole: template?.publicRole || template?.roleName || 'شاهد',
      privateBriefing: template?.privateBriefing || 'أنت بريء، لكنك تعرف جزءًا فقط من الحقيقة. شارك ما تراه مناسبًا أثناء التحقيق.',
      knownFacts: template?.knownFacts || [],
      secrets: template?.secrets || [],
      objectives: template?.objectives || ['ساعد في كشف الحقيقة', 'لا تخترع معلومات لم تُعط لك']
    };
  }

  const sessionTruth = mode === 'human'
    ? {
        culpritType: 'player',
        culpritId: humanCulprit.id,
        culpritName: humanCulprit.name,
        motive: culpritCard?.motive || roleConfig.humanTruth?.motive || 'معلومة سرية خاصة بالقضية.',
        method: culpritCard?.method || roleConfig.humanTruth?.method || 'تفاصيل سرية محفوظة في السيرفر.',
        timeline: culpritCard?.timeline || roleConfig.humanTruth?.timeline || []
      }
    : {
        culpritType: 'ai',
        culpritId: caseData.truth.culpritId,
        motive: caseData.truth.motive,
        method: caseData.truth.method,
        timeline: caseData.truth.timeline || []
      };

  return {
    culpritMode: mode,
    assignments,
    sessionTruth,
    originalAiCulpritId: caseData.truth.culpritId
  };
}

export function getPlayerRole(session, playerId) {
  return session?.roles?.[playerId] || null;
}

export function getCharacterForSession(caseData, session, characterId) {
  const character = caseData.characters.find((item) => item.id === characterId);
  if (!character) return null;

  if (session?.truth?.culpritType !== 'player' || character.id !== session.originalAiCulpritId) {
    return character;
  }

  return {
    ...character,
    secrets: (character.secrets || []).filter((secret) => !/المسؤول عن الجريمة|أخفى مفتاح|زوّر سجلات/i.test(secret)),
    liePlan: null,
    goals: ['أجب فقط بما تعرفه', 'احمِ أسرارك غير المرتبطة بالجريمة', 'لا تعترف بجريمة لم ترتكبها']
  };
}
