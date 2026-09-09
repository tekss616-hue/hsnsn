import http from 'node:http';
import { cert, getApps, initializeApp } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';
import { getFirestore } from 'firebase-admin/firestore';
import { getMessaging } from 'firebase-admin/messaging';
import { ADMIN_EMAIL, isAdminEmail } from './admin-config.js';
import { hasOpenAIKey, loadOpenAIKey, saveOpenAIKey } from './secret-store.js';
import { chatWithNader, startNaderSession, testOpenAIKey } from './nader-preview.js';

function initializeFirebaseAdmin(){
  if(getApps().length)return;
  const raw=String(process.env.FIREBASE_SERVICE_ACCOUNT_JSON||'').trim();
  if(!raw){ initializeApp(); return; }
  let s;
  try{s=JSON.parse(raw)}catch{throw new Error('FIREBASE_SERVICE_ACCOUNT_JSON_invalid_json')}
  if(!s.project_id||!s.client_email||!s.private_key)throw new Error('FIREBASE_SERVICE_ACCOUNT_JSON_missing_fields');
  initializeApp({credential:cert({projectId:s.project_id,clientEmail:s.client_email,privateKey:String(s.private_key).replace(/\\n/g,'\n')})});
}
initializeFirebaseAdmin();

const PORT=Number(process.env.PORT||8787);
function send(res,status,body){res.writeHead(status,{'content-type':'application/json; charset=utf-8','access-control-allow-origin':'*','access-control-allow-headers':'content-type, authorization','access-control-allow-methods':'GET,POST,OPTIONS','cache-control':'no-store'});res.end(status===204?'':JSON.stringify(body));}
async function readJson(req){const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>64*1024)throw new Error('request_too_large');chunks.push(chunk)}const raw=Buffer.concat(chunks).toString('utf8');return raw?JSON.parse(raw):{};}
async function requireUser(req){const auth=String(req.headers.authorization||'');if(!auth.startsWith('Bearer '))throw new Error('auth_required');return getAuth().verifyIdToken(auth.slice(7).trim(),true);}
async function requireAdmin(req){const d=await requireUser(req);if(!isAdminEmail(d.email))throw new Error('admin_forbidden');return d;}
function statusFor(code){if(code==='auth_required'||code.includes('Firebase ID token')||code.includes('auth/id-token'))return 401;if(code==='admin_forbidden')return 403;if(code.includes('not_found'))return 404;return 400;}

const server=http.createServer(async(req,res)=>{
  if(req.method==='OPTIONS')return send(res,204,{});
  try{
    if(req.method==='GET'&&req.url==='/api/health')return send(res,200,{ok:true,server:'hsnsn-clean-v1',liveAI:await hasOpenAIKey(),nader:true});

    if(req.method==='POST'&&req.url==='/api/social/friend-push'){
      const from=await requireUser(req),body=await readJson(req),toUid=String(body.toUid||'');
      if(!toUid||toUid===from.uid)throw new Error('invalid_recipient');
      const db=getFirestore();const request=await db.collection('friendRequests').doc(`${from.uid}_${toUid}`).get();
      if(!request.exists||request.get('status')!=='pending'||request.get('fromUid')!==from.uid)throw new Error('friend_request_not_found');
      const [target,sender]=await Promise.all([db.collection('users').doc(toUid).get(),db.collection('users').doc(from.uid).get()]);
      const token=target.get('fcmToken');if(!token)return send(res,200,{ok:true,delivered:false});
      const name=sender.get('name')||from.name||'لاعب';
      await getMessaging().send({token,notification:{title:'طلب صداقة جديد',body:`${name} أرسل لك طلب صداقة`},data:{type:'friend_request',fromUid:from.uid}});
      return send(res,200,{ok:true,delivered:true});
    }

    if(req.method==='POST'&&req.url==='/api/social/friend-accepted-push'){
      const accepter=await requireUser(req),body=await readJson(req),toUid=String(body.toUid||'');
      if(!toUid||toUid===accepter.uid)throw new Error('invalid_recipient');
      const db=getFirestore();const request=await db.collection('friendRequests').doc(`${toUid}_${accepter.uid}`).get();
      if(!request.exists||request.get('status')!=='accepted'||request.get('fromUid')!==toUid||request.get('toUid')!==accepter.uid)throw new Error('friend_acceptance_not_found');
      const [target,acceptingUser]=await Promise.all([db.collection('users').doc(toUid).get(),db.collection('users').doc(accepter.uid).get()]);
      const token=target.get('fcmToken');if(!token)return send(res,200,{ok:true,delivered:false});
      const name=acceptingUser.get('name')||accepter.name||'لاعب';
      await getMessaging().send({token,notification:{title:'تم قبول طلب الصداقة',body:`${name} وافق على طلب صداقتك`},data:{type:'friend_accepted',fromUid:accepter.uid}});
      return send(res,200,{ok:true,delivered:true});
    }

    if(req.method==='GET'&&req.url==='/api/admin/ai/status'){
      const a=await requireAdmin(req);return send(res,200,{ok:true,admin:a.email,configured:await hasOpenAIKey(),model:process.env.OPENAI_MODEL||'gpt-5.6-luna',storage:process.env.OPENAI_API_KEY?'environment-secret':'encrypted-server-secret'});
    }
    if(req.method==='POST'&&req.url==='/api/admin/ai/key'){
      const a=await requireAdmin(req),b=await readJson(req);await saveOpenAIKey(b.apiKey);console.log(`OpenAI key updated by ${a.email||ADMIN_EMAIL}; key material not logged`);return send(res,200,{ok:true,configured:true});
    }
    if(req.method==='POST'&&req.url==='/api/admin/ai/test'){
      await requireAdmin(req);const key=await loadOpenAIKey();if(!key)throw new Error('OPENAI_API_KEY_missing');return send(res,200,await testOpenAIKey(key));
    }
    if(req.method==='POST'&&req.url==='/api/admin/nader/session'){
      const a=await requireAdmin(req),b=await readJson(req),key=await loadOpenAIKey();if(!key)throw new Error('OPENAI_API_KEY_missing');return send(res,201,await startNaderSession({uid:a.uid,playerName:b.playerName||'اللاعب',apiKey:key}));
    }
    if(req.method==='POST'&&req.url==='/api/admin/nader/chat'){
      const a=await requireAdmin(req),b=await readJson(req),key=await loadOpenAIKey();if(!key)throw new Error('OPENAI_API_KEY_missing');return send(res,200,await chatWithNader({uid:a.uid,sessionId:b.sessionId,text:b.text,apiKey:key}));
    }

    return send(res,404,{error:'not_found'});
  }catch(error){
    const code=String(error?.message||error);console.error('request_error',code.replace(/sk-[A-Za-z0-9_\-]+/g,'[REDACTED]'));
    return send(res,statusFor(code),{error:code.startsWith('openai_error:')?'openai_connection_failed':code});
  }
});

server.listen(PORT,()=>console.log(`Clean HSNSN server running on port ${PORT}`));
