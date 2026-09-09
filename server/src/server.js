import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { cert, getApps, initializeApp } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';
import { getFirestore } from 'firebase-admin/firestore';
import { getMessaging } from 'firebase-admin/messaging';
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

function initializeFirebaseAdmin(){if(getApps().length)return;const raw=String(process.env.FIREBASE_SERVICE_ACCOUNT_JSON||'').trim();if(!raw){initializeApp();return;}let s;try{s=JSON.parse(raw)}catch{throw new Error('FIREBASE_SERVICE_ACCOUNT_JSON_invalid_json')}if(!s.project_id||!s.client_email||!s.private_key)throw new Error('FIREBASE_SERVICE_ACCOUNT_JSON_missing_fields');initializeApp({credential:cert({projectId:s.project_id,clientEmail:s.client_email,privateKey:String(s.private_key).replace(/\\n/g,'\n')})});}
initializeFirebaseAdmin();
const envHasOpenAI=Boolean(process.env.OPENAI_API_KEY);const provider=envHasOpenAI?new OpenAIProvider():new MockProvider();const providerName=envHasOpenAI?`openai:${process.env.OPENAI_MODEL||'gpt-5.6-luna'}`:'mock';const engine=new CaseEngine({caseData,roleConfig,directorConfig,provider});const PORT=Number(process.env.PORT||8787);
function send(res,status,body){res.writeHead(status,{'content-type':'application/json; charset=utf-8','access-control-allow-origin':'*','access-control-allow-headers':'content-type, authorization','access-control-allow-methods':'GET,POST,OPTIONS','cache-control':'no-store'});res.end(status===204?'':JSON.stringify(body));}
async function readJson(req){const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>64*1024)throw new Error('request_too_large');chunks.push(chunk)}const raw=Buffer.concat(chunks).toString('utf8');return raw?JSON.parse(raw):{};}
async function requireUser(req){const auth=String(req.headers.authorization||'');if(!auth.startsWith('Bearer '))throw new Error('auth_required');return getAuth().verifyIdToken(auth.slice(7).trim(),true);}
async function requireAdmin(req){const d=await requireUser(req);if(!isAdminEmail(d.email))throw new Error('admin_forbidden');return d;}
function adminStatus(c){return c==='auth_required'?401:c==='admin_forbidden'?403:400;}
const server=http.createServer(async(req,res)=>{if(req.method==='OPTIONS')return send(res,204,{});try{
if(req.method==='GET'&&req.url==='/api/health')return send(res,200,{ok:true,brain:'roleplay-v1',provider:providerName,liveAI:envHasOpenAI||await hasOpenAIKey(),roleEngine:true,naderPreview:true});
if(req.method==='POST'&&req.url==='/api/social/friend-push'){const from=await requireUser(req),body=await readJson(req),toUid=String(body.toUid||'');if(!toUid||toUid===from.uid)throw new Error('invalid_recipient');const db=getFirestore();const request=await db.collection('friendRequests').doc(`${from.uid}_${toUid}`).get();if(!request.exists||request.get('status')!=='pending'||request.get('fromUid')!==from.uid)throw new Error('friend_request_not_found');const [target,sender]=await Promise.all([db.collection('users').doc(toUid).get(),db.collection('users').doc(from.uid).get()]);const token=target.get('fcmToken');if(!token)return send(res,200,{ok:true,delivered:false});const name=sender.get('name')||from.name||'لاعب';await getMessaging().send({token,notification:{title:'طلب صداقة جديد',body:`${name} أرسل لك طلب صداقة`},data:{type:'friend_request',fromUid:from.uid}});return send(res,200,{ok:true,delivered:true});}
if(req.method==='POST'&&req.url==='/api/social/friend-accepted-push'){const accepter=await requireUser(req),body=await readJson(req),toUid=String(body.toUid||'');if(!toUid||toUid===accepter.uid)throw new Error('invalid_recipient');const db=getFirestore();const request=await db.collection('friendRequests').doc(`${toUid}_${accepter.uid}`).get();if(!request.exists||request.get('status')!=='accepted'||request.get('fromUid')!==toUid||request.get('toUid')!==accepter.uid)throw new Error('friend_acceptance_not_found');const [target,acceptingUser]=await Promise.all([db.collection('users').doc(toUid).get(),db.collection('users').doc(accepter.uid).get()]);const token=target.get('fcmToken');if(!token)return send(res,200,{ok:true,delivered:false});const name=acceptingUser.get('name')||accepter.name||'لاعب';await getMessaging().send({token,notification:{title:'تم قبول طلب الصداقة',body:`${name} وافق على طلب صداقتك`},data:{type:'friend_accepted',fromUid:accepter.uid}});return send(res,200,{ok:true,delivered:true});}
if(req.method==='GET'&&req.url==='/api/admin/ai/status'){const a=await requireAdmin(req);return send(res,200,{ok:true,admin:a.email,configured:await hasOpenAIKey(),model:process.env.OPENAI_MODEL||'gpt-5.6-luna',storage:process.env.OPENAI_API_KEY?'environment-secret':'encrypted-server-secret'});}
if(req.method==='POST'&&req.url==='/api/admin/ai/key'){const a=await requireAdmin(req),b=await readJson(req);await saveOpenAIKey(b.apiKey);console.log(`OpenAI key updated by ${a.email||ADMIN_EMAIL}; key material not logged`);return send(res,200,{ok:true,configured:true});}
if(req.method==='POST'&&req.url==='/api/admin/ai/test'){await requireAdmin(req);const k=await loadOpenAIKey();if(!k)throw new Error('OPENAI_API_KEY_missing');return send(res,200,await testOpenAIKey(k));}
if(req.method==='POST'&&req.url==='/api/admin/nader/session'){const a=await requireAdmin(req),b=await readJson(req),k=await loadOpenAIKey();if(!k)throw new Error('OPENAI_API_KEY_missing');return send(res,201,await startNaderPreview({uid:a.uid,playerName:b.playerName||'الادمن',apiKey:k}));}
if(req.method==='POST'&&req.url==='/api/admin/nader/chat'){const a=await requireAdmin(req),b=await readJson(req),k=await loadOpenAIKey();if(!k)throw new Error('OPENAI_API_KEY_missing');return send(res,200,await chatWithNader({uid:a.uid,sessionId:b.sessionId,text:b.text,apiKey:k}));}
if(req.method==='POST'&&req.url==='/api/session'){const b=await readJson(req),s=engine.createSession({players:b.players||[],culpritMode:b.culpritMode||'ai'});return send(res,201,engine.getPublicSession(s.id));}
if(req.method==='POST'&&req.url==='/api/my-role')return send(res,200,engine.getPrivateRole(await readJson(req)));if(req.method==='POST'&&req.url==='/api/round-state')return send(res,200,engine.getRoundState(await readJson(req)));if(req.method==='POST'&&req.url==='/api/game-master/feed')return send(res,200,engine.getGameMasterFeed(await readJson(req)));if(req.method==='POST'&&req.url==='/api/chat')return send(res,200,await engine.ask(await readJson(req)));if(req.method==='POST'&&req.url==='/api/accuse')return send(res,200,engine.accuse(await readJson(req)));if(req.method==='POST'&&req.url==='/api/contradiction')return send(res,201,engine.recordContradiction(await readJson(req)));if(req.method==='POST'&&req.url==='/api/finalize')return send(res,200,engine.finalizeRound(await readJson(req)));return send(res,404,{error:'not_found'});
}catch(error){const code=String(error?.message||error),status=code.includes('not_found')?404:code==='time_expired'?410:code==='round_still_active'?409:code==='auth_required'?401:code.startsWith('admin_')?adminStatus(code):code.includes('Firebase ID token')||code.includes('auth/id-token')?401:400;console.error('request_error',code.replace(/sk-[A-Za-z0-9_\-]+/g,'[REDACTED]'));return send(res,status,{error:code.startsWith('openai_error:')?'openai_connection_failed':code});}});
server.listen(PORT,()=>console.log(`Roleplay brain running on port ${PORT} using ${providerName}`));
