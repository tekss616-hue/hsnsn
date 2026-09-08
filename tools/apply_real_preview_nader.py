from pathlib import Path

jsf=Path('app/src/main/assets/social.js')
js=jsf.read_text(encoding='utf-8')

# Remove fake local world population and canned Nader behavior from the generated world runtime.
js=js.replace("const baseCounts={beach:2,palace:1,garden:1,hospital:1,police:0,market:1,restaurant:1,hotel:0,harbor:1};","const baseCounts={beach:0,palace:0,garden:0,hospital:0,police:0,market:0,restaurant:0,hotel:0,harbor:0};")
js=js.replace("let preview=false,current='beach',naderPlace='beach',naderTyping=false,returnState=[],keyboardBottom=0;","let preview=false,current='beach',naderPlace='beach',naderTyping=false,returnState=[],keyboardBottom=0,naderSession='',naderStarting=null;")

start=js.find('function naderReplyFor(text)')
end=js.find('function moveNader()',start)
if start<0 or end<0: raise SystemExit('fake Nader block not found')
real=r'''function worldAiRequest(path,method='POST',body={}){return new Promise((resolve,reject)=>{const base=String(localStorage.getItem('hsnsn_ai_server_url')||'').trim().replace(/\/+$/,'');if(!base){reject(new Error('خادم نادر غير مضبوط'));return}const id='world_nader_'+Date.now()+'_'+Math.random().toString(36).slice(2);if(typeof window.HSNSNAiRequest==='function'){window.HSNSNAiRequest(path,method,body).then(resolve,reject);return}if(typeof NativeAuth==='undefined'||typeof NativeAuth.adminAiRequest!=='function'){reject(new Error('اتصال نادر الحقيقي غير متاح'));return}window.__worldNaderPending=window.__worldNaderPending||new Map();window.__worldNaderPending.set(id,{resolve,reject});NativeAuth.adminAiRequest(id,base,path,method,JSON.stringify(body||{}))})}
const previousNativeAiResult=window.onNativeAdminAiResult;
window.onNativeAdminAiResult=p=>{const map=window.__worldNaderPending,q=map?.get(String(p?.requestId||''));if(q){map.delete(String(p.requestId));let data={};try{data=JSON.parse(p.body||'{}')}catch{};p.ok?q.resolve(data):q.reject(new Error(data.error||p.message||('HTTP '+(p.status||0))));return}if(typeof previousNativeAiResult==='function')previousNativeAiResult(p)};
async function ensureRealNader(){if(naderSession)return naderSession;if(naderStarting)return naderStarting;naderStarting=worldAiRequest('/api/admin/nader/session','POST',{playerName:profileName()}).then(d=>{naderSession=d.sessionId||'';if(!naderSession)throw new Error('لم تبدأ جلسة نادر');if(d.message)addMsg(current,'نادر',d.message,false,true);render();return naderSession}).finally(()=>{naderStarting=null});return naderStarting}
async function naderSpeak(text){if(naderPlace!==current)return;naderTyping=true;render();try{await ensureRealNader();const d=await worldAiRequest('/api/admin/nader/chat','POST',{sessionId:naderSession,text});naderTyping=false;if(d.message)addMsg(current,'نادر',d.message,false,true);render()}catch(e){naderTyping=false;addSystem(current,'نادر غير متصل حالياً');render()}}
async function maybeNaderGreets(){if(naderPlace!==current)return;ensure(current);if(messages[current].some(x=>x.nader))return;naderTyping=true;render();try{await ensureRealNader()}catch(e){naderTyping=false;addSystem(current,'نادر غير متصل حالياً');render()}}
'''
js=js[:start]+real+js[end:]

# In preview, do not fabricate player avatars/counts. Only real Nader may appear.
js=js.replace("function countAt(k){return (baseCounts[k]||0)+(naderPlace===k?1:0)}","function countAt(k){return (preview?0:(baseCounts[k]||0))+(naderPlace===k?1:0)}")
js=js.replace("for(let i=0;i<Math.min(baseCounts[current]||0,4);i++){const x=document.createElement('span');x.className='world-avatar';x.textContent=String(i+1);av.appendChild(x)}","if(!preview)for(let i=0;i<Math.min(baseCounts[current]||0,4);i++){const x=document.createElement('span');x.className='world-avatar';x.textContent=String(i+1);av.appendChild(x)}")

# No fake autonomous movement in admin preview. Nader stays where the real preview session is being tested.
js=js.replace("setInterval(()=>{if(!$('worldGame')?.hidden&&Math.random()<.34)moveNader()},45000);","setInterval(()=>{if(!$('worldGame')?.hidden&&!preview&&Math.random()<.34)moveNader()},45000);")

if 'function naderReplyFor' in js: raise SystemExit('canned Nader replies still present')
js += "\n;(()=>{const REAL_PREVIEW_NADER_V1=true;})();\n"
jsf.write_text(js,encoding='utf-8')
print('Admin preview now contains no fabricated players or canned Nader; real server Nader only')
