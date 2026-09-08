from pathlib import Path

java=Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java')
s=java.read_text(encoding='utf-8')
needle='        @JavascriptInterface public void warmAuth() { warmAuthComponents(); }'
insert='''        @JavascriptInterface public void warmAuth() { warmAuthComponents(); }\n        @JavascriptInterface public boolean isAdminAccount(){ FirebaseUser u=currentUser(); String email=u==null||u.getEmail()==null?"":u.getEmail().trim(); return "bajanznsb@gmail.com".equalsIgnoreCase(email); }'''
if 'isAdminAccount()' not in s:
    if needle not in s: raise SystemExit('AuthBridge warmAuth marker not found')
    s=s.replace(needle,insert,1)
java.write_text(s,encoding='utf-8')

jsf=Path('app/src/main/assets/social.js')
js=jsf.read_text(encoding='utf-8')
if 'ADMIN_PANEL_VISIBILITY_FIX' not in js:
    js += r'''
;(()=>{
const ADMIN_PANEL_VISIBILITY_FIX=true,$=id=>document.getElementById(id);
function adminAllowed(){
  try{if(typeof NativeAuth!=='undefined'&&typeof NativeAuth.isAdminAccount==='function')return !!NativeAuth.isAdminAccount()}catch{}
  try{const p=JSON.parse(localStorage.getItem('profile_cache')||'null');return String(p?.email||'').trim().toLowerCase()==='bajanznsb@gmail.com'}catch{return false}
}
function syncAdminPanel(){const b=$('adminPanelBtn');if(b)b.hidden=!adminAllowed()}
document.addEventListener('click',e=>{if(e.target.closest?.('#hqSettings,[data-open-settings]'))setTimeout(syncAdminPanel,0)},true);
const sheet=$('settingsSheet');if(sheet)new MutationObserver(syncAdminPanel).observe(sheet,{attributes:true,attributeFilter:['hidden','class','style']});
setTimeout(syncAdminPanel,100);
})();
'''
jsf.write_text(js,encoding='utf-8')
print('Fixed admin panel visibility using authenticated Firebase account')

admin_batch=Path('tools/apply_admin_first_batch.py')
if not admin_batch.exists(): raise SystemExit('apply_admin_first_batch.py missing')
exec(compile(admin_batch.read_text(encoding='utf-8'),str(admin_batch),'exec'),{})

world_batch=Path('tools/apply_world_first_batch.py')
if not world_batch.exists(): raise SystemExit('apply_world_first_batch.py missing')
exec(compile(world_batch.read_text(encoding='utf-8'),str(world_batch),'exec'),{})

jsf=Path('app/src/main/assets/social.js')
js=jsf.read_text(encoding='utf-8')
old="$('adminPreviewOpen')?.addEventListener('click',openPreviewDirect);"
new="$('adminPreviewOpen')?.addEventListener('click',e=>{e.preventDefault();window.HSNSNWorld.preview()});"
if old in js:
    js=js.replace(old,new,1)
else:
    raise SystemExit('legacy admin preview binding not found')
jsf.write_text(js,encoding='utf-8')
print('Bound admin preview directly to initialized social world')

nader_ai=Path('tools/apply_nader_ai_admin.py')
if not nader_ai.exists(): raise SystemExit('apply_nader_ai_admin.py missing')
exec(compile(nader_ai.read_text(encoding='utf-8'),str(nader_ai),'exec'),{})

ai_server=Path('tools/apply_ai_server_url.py')
if not ai_server.exists(): raise SystemExit('apply_ai_server_url.py missing')
exec(compile(ai_server.read_text(encoding='utf-8'),str(ai_server),'exec'),{})

# Regression recovery after the admin/world/AI bundle.
js=jsf.read_text(encoding='utf-8')
old_open="function openWorld(isPreview=false){preview=!!isPreview;current='beach';const g=$('worldGame');if(!g)return;isolate();g.hidden=false;document.body.style.overflow='hidden';ensure(current);if(!messages[current].length)addSystem(current,'وصلت إلى '+nameOf(current));render();maybeNaderGreets()}"
new_open="function openWorld(isPreview=false){preview=!!isPreview;current='beach';const g=$('worldGame');if(!g)return;if(!g.hidden){render();return}isolate();g.hidden=false;document.body.style.overflow='hidden';ensure(current);if(!messages[current].length)addSystem(current,'وصلت إلى '+nameOf(current));render();maybeNaderGreets()}"
if old_open in js: js=js.replace(old_open,new_open,1)
elif new_open not in js: raise SystemExit('world open function not found')
old_close="function closeWorld(){const g=$('worldGame');if(g)g.hidden=true;document.body.classList.remove('world-preview-active');document.body.style.overflow='';returnState.forEach(id=>{const e=$(id);if(e)e.hidden=false});returnState=[]}"
new_close="function closeWorld(){const g=$('worldGame');if(g)g.hidden=true;document.body.classList.remove('world-preview-active');document.body.style.overflow='';const saved=[...returnState];returnState=[];let restored=false;saved.forEach(id=>{const e=$(id);if(e){e.hidden=false;restored=true}});if(!restored){if(preview&&$('adminDashboard')){$('adminDashboard').hidden=false}else window.showHQ?.()}}"
if old_close in js: js=js.replace(old_close,new_close,1)
elif new_close not in js: raise SystemExit('world close function not found')
old_click="document.addEventListener('click',e=>{if(e.target.closest?.('#worldBack'))closeWorld();if(e.target.closest?.('#worldPlacesOpen')){$('worldPlaces').hidden=false;renderPlaces()}if(e.target.closest?.('#worldPlacesClose'))$('worldPlaces').hidden=true;if(e.target.closest?.('#adminPreviewOpen'))setTimeout(()=>openWorld(true),0)},true);"
new_click="document.addEventListener('click',e=>{if(e.target.closest?.('#worldBack'))closeWorld();if(e.target.closest?.('#worldPlacesOpen')){$('worldPlaces').hidden=false;renderPlaces()}if(e.target.closest?.('#worldPlacesClose'))$('worldPlaces').hidden=true},true);"
if old_click in js: js=js.replace(old_click,new_click,1)
elif new_click not in js: raise SystemExit('world click binding not found')

old_lp="const chats=$('chatsList');if(chats){new MutationObserver(decorateChats).observe(chats,{childList:true,subtree:true});chats.addEventListener('pointerdown',e=>{const row=e.target.closest('.chat-row');if(!row)return;clearTimeout(longTimer);longTimer=setTimeout(()=>openChatActions(row),650)});['pointerup','pointercancel','pointermove'].forEach(ev=>chats.addEventListener(ev,()=>clearTimeout(longTimer)))}"
new_lp="const chats=$('chatsList');if(chats){new MutationObserver(decorateChats).observe(chats,{childList:true,subtree:true});let holdX=0,holdY=0,holding=false;chats.addEventListener('pointerdown',e=>{const row=e.target.closest('.chat-row');if(!row)return;holding=true;holdX=e.clientX;holdY=e.clientY;clearTimeout(longTimer);longTimer=setTimeout(()=>{holding=false;openChatActions(row)},550)});chats.addEventListener('pointermove',e=>{if(!holding)return;if(Math.hypot(e.clientX-holdX,e.clientY-holdY)>14){holding=false;clearTimeout(longTimer)}});['pointerup','pointercancel'].forEach(ev=>chats.addEventListener(ev,()=>{holding=false;clearTimeout(longTimer)}));chats.addEventListener('contextmenu',e=>{const row=e.target.closest('.chat-row');if(!row)return;e.preventDefault();clearTimeout(longTimer);holding=false;openChatActions(row)})}"
if old_lp in js: js=js.replace(old_lp,new_lp,1)
elif new_lp not in js: raise SystemExit('chat long press binding not found')

if 'NADER_AI_ADMIN_V1' not in js: raise SystemExit('Nader AI admin runtime missing')
js += "\n;(()=>{const ROLEPLAY_REGRESSION_RECOVERY_V1=true;})();\n"
jsf.write_text(js,encoding='utf-8')
print('Recovered preview return, long-press chat actions, and admin AI controls')

# Prevent the workflow's legacy second world pass from truncating the AI runtime.
world_batch.write_text("print('World already applied by fix_admin_panel_visibility; preserving admin AI runtime')\n",encoding='utf-8')
