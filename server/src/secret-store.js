import { createCipheriv, createDecipheriv, createHash, randomBytes } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

const DATA_DIR = process.env.SECRET_DATA_DIR || path.resolve(process.cwd(), '.data');
const SECRET_FILE = path.join(DATA_DIR, 'openai-api-key.enc.json');

function masterKey() {
  const raw = String(process.env.SERVER_MASTER_KEY || '');
  if (!raw) throw new Error('SERVER_MASTER_KEY_missing');
  return createHash('sha256').update(raw, 'utf8').digest();
}

export async function saveOpenAIKey(apiKey) {
  const value = String(apiKey || '').trim();
  if (!value.startsWith('sk-') || value.length < 20) throw new Error('invalid_openai_api_key');
  const iv = randomBytes(12);
  const cipher = createCipheriv('aes-256-gcm', masterKey(), iv);
  const ciphertext = Buffer.concat([cipher.update(value, 'utf8'), cipher.final()]);
  const tag = cipher.getAuthTag();
  await mkdir(DATA_DIR, { recursive: true, mode: 0o700 });
  await writeFile(SECRET_FILE, JSON.stringify({
    v: 1,
    alg: 'aes-256-gcm',
    iv: iv.toString('base64'),
    tag: tag.toString('base64'),
    ciphertext: ciphertext.toString('base64'),
    updatedAt: new Date().toISOString()
  }), { encoding: 'utf8', mode: 0o600 });
  return true;
}

export async function loadOpenAIKey() {
  if (process.env.OPENAI_API_KEY) return String(process.env.OPENAI_API_KEY).trim();
  let payload;
  try { payload = JSON.parse(await readFile(SECRET_FILE, 'utf8')); }
  catch (error) {
    if (error?.code === 'ENOENT') return '';
    throw error;
  }
  const iv = Buffer.from(payload.iv, 'base64');
  const tag = Buffer.from(payload.tag, 'base64');
  const ciphertext = Buffer.from(payload.ciphertext, 'base64');
  const decipher = createDecipheriv('aes-256-gcm', masterKey(), iv);
  decipher.setAuthTag(tag);
  return Buffer.concat([decipher.update(ciphertext), decipher.final()]).toString('utf8').trim();
}

export async function hasOpenAIKey() {
  try { return Boolean(await loadOpenAIKey()); }
  catch { return false; }
}
