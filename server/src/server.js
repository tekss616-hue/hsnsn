import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { cert, getApps, initializeApp } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';
import { CaseEngine } from './brain/case-engine.js';
import { MockProvider } from './providers/mock-provider.js';
import { OpenAIProvider } from './providers/openai-provider.js';
import { ADMIN_EMAIL, isAdminEmail } from './admin-config.js';
import { hasOpenAIKey, loadOpenAIKey, saveOpenAIKey } from './secret-store.js';
import { chatWithNader, startNaderPreview, testOpenAIKey } from './nader-preview.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const casePath = path.resolve(__dirname, '../cases/midnight-hotel.json');
const rolePath = path.resolve(__dirname, '../cases/midnight-hotel-player-roles.json');
const directorPath = path.resolve(__dirname, '../cases/midnight-hotel-director.json');
const caseData = JSON.parse(await readFile(casePath, 'utf8'));
const roleConfig = JSON.parse(await readFile(rolePath, 'utf8'));
const directorConfig = JSON.parse(await readFile(directorPath, 'utf8'));

function initializeFirebaseAdmin() {
  if (getApps().length) return;
  const raw = String(process.env.FIREBASE_SERVICE_ACCOUNT_JSON || '').trim();
  if (!raw) {
    initializeApp();
    return;
  }
  let serviceAccount;
  try {
    serviceAccount = JSON.parse(raw);
  } catch {
    throw new Error('FIREBASE_SERVICE_ACCOUNT_JSON_invalid_json');
  }
  if (!serviceAccount.project_id || !serviceAccount.client_email || !serviceAccount.private_key) {
    throw new Error('FIREBASE_SERVICE_ACCOUNT_JSON_missing_fields');
  }
  initializeApp({
    credential: cert({
      projectId: serviceAccount.project_id,
      clientEmail: serviceAccount.client_email,
      privateKey: String(serviceAccount.private_key).replace(/\\n/g, '\n')
    })
  });
}

initializeFirebaseAdmin();

const envHasOpenAI = Boolean(process.env.OPENAI_API_KEY);
const provider = envHasOpenAI ? new OpenAIProvider() : new MockProvider();
const providerName = envHasOpenAI ? `openai:${process.env.OPENAI_MODEL || 'gpt-5.6-luna'}` : 'mock';
const engine = new CaseEngine({ caseData, roleConfig, directorConfig, provider });
const PORT = Number(process.env.PORT || 8787);

function send(res, status, body) {
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'access-control-allow-origin': '*',
    'access-control-allow-headers': 'content-type, authorization',
    'access-control-allow-methods': 'GET,POST,OPTIONS',
    'cache-control': 'no-store'
  });
  res.end(status === 204 ? '' : JSON.stringify(body));
}

async function readJson(req) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > 64 * 1024) throw new Error('request_too_large');
    chunks.push(chunk);
  }
  const raw = Buffer.concat(chunks).toString('utf8');
  return raw ? JSON.parse(raw) : {};
}

async function requireAdmin(req) {
  const auth = String(req.headers.authorization || '');
  if (!auth.startsWith('Bearer ')) throw new Error('admin_auth_required');
  const token = auth.slice(7).trim();
  const decoded = await getAuth().verifyIdToken(token, true);
  if (!isAdminEmail(decoded.email)) throw new Error('admin_forbidden');
  return decoded;
}

function adminStatus(errorCode) {
  return errorCode === 'admin_auth_required' ? 401 : errorCode === 'admin_forbidden' ? 403 : 400;
}

const server = http.createServer(async (req, res) => {
  if (req.method === 'OPTIONS') return send(res, 204, {});

  try {
    if (req.method === 'GET' && req.url === '/api/health') {
      return send(res, 200, {
        ok: true,
        brain: 'investigation-v0.6',
        caseId: caseData.id,
        provider: providerName,
        liveAI: envHasOpenAI || await hasOpenAIKey(),
        roleEngine: true,
        gameMaster: true,
        liveDirector: true,
        naderPreview: true,
        stagedClues: directorConfig.clues?.length || 0,
        timedAnnouncements: directorConfig.announcements?.length || 0,
        culpritModes: ['ai', 'human', 'random']
      });
    }

    if (req.method === 'GET' && req.url === '/api/admin/ai/status') {
      const admin = await requireAdmin(req);
      return send(res, 200, {
        ok: true,
        admin: admin.email,
        configured: await hasOpenAIKey(),
        model: process.env.OPENAI_MODEL || 'gpt-5.6-luna',
        storage: process.env.OPENAI_API_KEY ? 'environment-secret' : 'encrypted-server-secret'
      });
    }

    if (req.method === 'POST' && req.url === '/api/admin/ai/key') {
      const admin = await requireAdmin(req);
      const body = await readJson(req);
      await saveOpenAIKey(body.apiKey);
      console.log(`OpenAI key updated by ${admin.email || ADMIN_EMAIL}; key material not logged`);
      return send(res, 200, { ok: true, configured: true });
    }

    if (req.method === 'POST' && req.url === '/api/admin/ai/test') {
      await requireAdmin(req);
      const apiKey = await loadOpenAIKey();
      if (!apiKey) throw new Error('OPENAI_API_KEY_missing');
      const result = await testOpenAIKey(apiKey);
      return send(res, 200, result);
    }

    if (req.method === 'POST' && req.url === '/api/admin/nader/session') {
      const admin = await requireAdmin(req);
      const body = await readJson(req);
      const apiKey = await loadOpenAIKey();
      if (!apiKey) throw new Error('OPENAI_API_KEY_missing');
      return send(res, 201, await startNaderPreview({ uid: admin.uid, playerName: body.playerName || 'الادمن', apiKey }));
    }

    if (req.method === 'POST' && req.url === '/api/admin/nader/chat') {
      const admin = await requireAdmin(req);
      const body = await readJson(req);
      const apiKey = await loadOpenAIKey();
      if (!apiKey) throw new Error('OPENAI_API_KEY_missing');
      return send(res, 200, await chatWithNader({ uid: admin.uid, sessionId: body.sessionId, text: body.text, apiKey }));
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
    const code = String(error?.message || error);
    const status = code.includes('not_found') ? 404
      : code === 'time_expired' ? 410
      : code === 'round_still_active' ? 409
      : code.startsWith('admin_') ? adminStatus(code)
      : code.includes('Firebase ID token') || code.includes('auth/id-token') ? 401
      : 400;
    console.error('request_error', code.replace(/sk-[A-Za-z0-9_\-]+/g, '[REDACTED]'));
    return send(res, status, { error: code.startsWith('openai_error:') ? 'openai_connection_failed' : code });
  }
});

server.listen(PORT, () => {
  console.log(`Investigation brain running on port ${PORT} using ${providerName}`);
});
