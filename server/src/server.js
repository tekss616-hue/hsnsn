import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { CaseEngine } from './brain/case-engine.js';
import { MockProvider } from './providers/mock-provider.js';
import { OpenAIProvider } from './providers/openai-provider.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const casePath = path.resolve(__dirname, '../cases/midnight-hotel.json');
const caseData = JSON.parse(await readFile(casePath, 'utf8'));

const hasOpenAI = Boolean(process.env.OPENAI_API_KEY);
const provider = hasOpenAI
  ? new OpenAIProvider()
  : new MockProvider();

const providerName = hasOpenAI ? `openai:${process.env.OPENAI_MODEL || 'gpt-5.6-luna'}` : 'mock';
const engine = new CaseEngine({ caseData, provider });
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
        brain: 'investigation-v0.2',
        caseId: caseData.id,
        provider: providerName,
        liveAI: hasOpenAI
      });
    }

    if (req.method === 'POST' && req.url === '/api/session') {
      const body = await readJson(req);
      const session = engine.createSession({ players: body.players || [] });
      return send(res, 201, engine.getPublicSession(session.id));
    }

    if (req.method === 'POST' && req.url === '/api/chat') {
      const body = await readJson(req);
      const result = await engine.ask(body);
      return send(res, 200, result);
    }

    if (req.method === 'POST' && req.url === '/api/accuse') {
      const body = await readJson(req);
      const result = engine.accuse(body);
      return send(res, 200, result);
    }

    return send(res, 404, { error: 'not_found' });
  } catch (error) {
    const code = String(error.message || error);
    const status = code.includes('not_found') ? 404 : code === 'time_expired' ? 410 : 400;
    return send(res, status, { error: code });
  }
});

server.listen(PORT, () => {
  console.log(`Investigation brain running on http://localhost:${PORT} using ${providerName}`);
});
