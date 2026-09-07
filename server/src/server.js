import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { CaseEngine } from './brain/case-engine.js';
import { MockProvider } from './providers/mock-provider.js';
import { OpenAIProvider } from './providers/openai-provider.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const casePath = path.resolve(__dirname, '../cases/midnight-hotel.json');
const rolePath = path.resolve(__dirname, '../cases/midnight-hotel-player-roles.json');
const directorPath = path.resolve(__dirname, '../cases/midnight-hotel-director.json');
const caseData = JSON.parse(await readFile(casePath, 'utf8'));
const roleConfig = JSON.parse(await readFile(rolePath, 'utf8'));
const directorConfig = JSON.parse(await readFile(directorPath, 'utf8'));

const hasOpenAI = Boolean(process.env.OPENAI_API_KEY);
const provider = hasOpenAI ? new OpenAIProvider() : new MockProvider();
const providerName = hasOpenAI ? `openai:${process.env.OPENAI_MODEL || 'gpt-5.6-luna'}` : 'mock';
const engine = new CaseEngine({ caseData, roleConfig, directorConfig, provider });
const PORT = Number(process.env.PORT || 8787);

function send(res, status, body) {
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'access-control-allow-origin': '*',
    'access-control-allow-headers': 'content-type',
    'access-control-allow-methods': 'GET,POST,OPTIONS'
  });
  res.end(JSON.stringify(body));
}

async function readJson(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString('utf8');
  return raw ? JSON.parse(raw) : {};
}

const server = http.createServer(async (req, res) => {
  if (req.method === 'OPTIONS') return send(res, 204, {});

  try {
    if (req.method === 'GET' && req.url === '/api/health') {
      return send(res, 200, {
        ok: true,
        brain: 'investigation-v0.5',
        caseId: caseData.id,
        provider: providerName,
        liveAI: hasOpenAI,
        roleEngine: true,
        gameMaster: true,
        liveDirector: true,
        stagedClues: directorConfig.clues?.length || 0,
        timedAnnouncements: directorConfig.announcements?.length || 0,
        culpritModes: ['ai', 'human', 'random']
      });
    }

    if (req.method === 'POST' && req.url === '/api/session') {
      const body = await readJson(req);
      const session = engine.createSession({ players: body.players || [], culpritMode: body.culpritMode || 'ai' });
      return send(res, 201, engine.getPublicSession(session.id));
    }

    if (req.method === 'POST' && req.url === '/api/my-role') return send(res, 200, engine.getPrivateRole(await readJson(req)));
    if (req.method === 'POST' && req.url === '/api/round-state') return send(res, 200, engine.getRoundState(await readJson(req)));
    if (req.method === 'POST' && req.url === '/api/game-master/feed') return send(res, 200, engine.getGameMasterFeed(await readJson(req)));
    if (req.method === 'POST' && req.url === '/api/chat') return send(res, 200, await engine.ask(await readJson(req)));
    if (req.method === 'POST' && req.url === '/api/accuse') return send(res, 200, engine.accuse(await readJson(req)));
    if (req.method === 'POST' && req.url === '/api/contradiction') return send(res, 201, engine.recordContradiction(await readJson(req)));
    if (req.method === 'POST' && req.url === '/api/finalize') return send(res, 200, engine.finalizeRound(await readJson(req)));

    return send(res, 404, { error: 'not_found' });
  } catch (error) {
    const code = String(error.message || error);
    const status = code.includes('not_found') ? 404
      : code === 'time_expired' ? 410
      : code === 'round_still_active' ? 409
      : 400;
    return send(res, status, { error: code });
  }
});

server.listen(PORT, () => {
  console.log(`Investigation brain running on http://localhost:${PORT} using ${providerName}`);
});
