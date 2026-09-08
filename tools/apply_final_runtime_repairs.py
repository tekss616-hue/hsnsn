from pathlib import Path

jsf=Path('app/src/main/assets/social.js')
cssf=Path('app/src/main/assets/social.css')
js=jsf.read_text(encoding='utf-8')
css=cssf.read_text(encoding='utf-8')

# 1) Expose the already-working admin AI request runtime AFTER it is defined.
needle="function request(path,method='POST',body={}){return new Promise((resolve,reject)=>{const base=serverUrl();"
if needle not in js:
    raise SystemExit('admin AI request runtime missing')
expose="window.HSNSNAiRequest=(path,method='POST',body={})=>{const el=$('adminAiServer');if(el&&!String(el.value||'').trim()){try{el.value=localStorage.getItem(serverKey)||''}catch{}}return request(path,method,body)};"
anchor="window.onNativeAdminAiResult=p=>{const q=pending.get(String(p?.requestId||''));"
if expose not in js:
    pos=js.find(anchor)
    if pos<0: raise SystemExit('admin AI result handler missing')
    js=js[:pos]+expose+'\n'+js[pos:]

# 2) World Nader must use the shared admin runtime instead of installing a callback
# before the admin runtime later overwrites it. This was the cause of hanging replies.
start=js.find("function worldAiRequest(path,method='POST',body={})")
end=js.find('async function ensureRealNader()',start)
if start<0 or end<0:
    raise SystemExit('world Nader request block missing')
shared=r'''function worldAiRequest(path,method='POST',body={}){
  if(typeof window.HSNSNAiRequest!=='function')return Promise.reject(new Error('اتصال نادر الحقيقي غير جاهز'));
  return Promise.race([
    window.HSNSNAiRequest(path,method,body),
    new Promise((_,reject)=>setTimeout(()=>reject(new Error('انتهت مهلة اتصال نادر')),35000))
  ]);
}
'''
js=js[:start]+shared+js[end:]

# 3) There is no real server typing event yet. Do not show a fake typing state.
old="async function naderSpeak(text){if(naderPlace!==current)return;try{await ensureRealNader();const d=await worldAiRequest('/api/admin/nader/chat','POST',{sessionId:naderSession,text});if(d.message){naderTyping=true;render();requestAnimationFrame(()=>requestAnimationFrame(()=>{naderTyping=false;addMsg(current,'نادر',d.message,false,true);render()}))}}catch(e){naderTyping=false;addSystem(current,'تعذر اتصال نادر الحقيقي');render()}}"
new="async function naderSpeak(text){if(naderPlace!==current)return;try{await ensureRealNader();const d=await worldAiRequest('/api/admin/nader/chat','POST',{sessionId:naderSession,text});naderTyping=false;if(d.message)addMsg(current,'نادر',d.message,false,true);render()}catch(e){naderTyping=false;addSystem(current,'تعذر اتصال نادر الحقيقي: '+String(e?.message||e));render()}}"
if old in js:
    js=js.replace(old,new,1)
elif new not in js:
    raise SystemExit('Nader speak function did not match expected runtime')

# 4) Main navigation active state: bind at document level in capture phase at the
# final build stage. The active tab is the section actually selected, not always play.
nav_runtime=r'''
;(()=>{
const FINAL_MAIN_NAV_ACTIVE_V2=true;
function nav(){return document.querySelector('.hq-nav')}
function setActive(target){const n=nav();if(!n)return;[...n.querySelectorAll('button')].forEach(b=>b.classList.toggle('active',b===target))}
function byName(name){return nav()?.querySelector(`[data-main="${name}"]`)||null}
function syncFromVisible(){
  const social=document.getElementById('social'),ranking=document.getElementById('rankingView'),store=document.getElementById('gameStore'),hq=document.getElementById('hq');
  if(social&&!social.hidden)return setActive(document.getElementById('openProfileTab'));
  if(ranking&&!ranking.hidden)return setActive(document.getElementById('rankingTab'));
  if(store&&!store.hidden)return setActive(document.getElementById('storeTab'));
  if(hq&&!hq.hidden)return setActive(byName('play'));
}
document.addEventListener('click',e=>{
  const b=e.target.closest?.('.hq-nav button');
  if(b){setActive(b);setTimeout(syncFromVisible,0);setTimeout(syncFromVisible,80);return}
  if(e.target.closest?.('.game-overlay-back,#socialBack'))setTimeout(syncFromVisible,0);
},true);
['hq','social','rankingView','gameStore'].forEach(id=>{const el=document.getElementById(id);if(el)new MutationObserver(syncFromVisible).observe(el,{attributes:true,attributeFilter:['hidden','style','class']})});
setTimeout(syncFromVisible,0);
})();
'''
if 'FINAL_MAIN_NAV_ACTIVE_V2' not in js:
    js += nav_runtime

if '/* final-main-nav-active-v2 */' not in css:
    css += '''\n/* final-main-nav-active-v2 */
.hq-nav button{color:#747474!important;opacity:1!important;font-weight:400!important}
.hq-nav button.active{color:#fff!important;opacity:1!important;font-weight:700!important}
'''

# Build-time guards against the two regressions.
if 'installWorldNaderResultBridge()' in js:
    raise SystemExit('stale world Nader callback bridge still present')
if 'window.HSNSNAiRequest' not in js or 'FINAL_MAIN_NAV_ACTIVE_V2' not in js:
    raise SystemExit('final runtime repairs incomplete')

jsf.write_text(js,encoding='utf-8')
cssf.write_text(css,encoding='utf-8')
print('Applied final Nader bridge and true main navigation active-state repairs')
