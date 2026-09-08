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

# Build admin shell first because the world preview button lives there.
admin_batch=Path('tools/apply_admin_first_batch.py')
if not admin_batch.exists(): raise SystemExit('apply_admin_first_batch.py missing')
exec(compile(admin_batch.read_text(encoding='utf-8'),str(admin_batch),'exec'),{})

# Build and initialize the social world BEFORE any AI scripts. This guarantees
# window.HSNSNWorld exists even if a later AI panel script has a runtime issue.
world_batch=Path('tools/apply_world_first_batch.py')
if not world_batch.exists(): raise SystemExit('apply_world_first_batch.py missing')
exec(compile(world_batch.read_text(encoding='utf-8'),str(world_batch),'exec'),{})

# Replace the legacy investigation preview binding with the world preview binding.
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

# AI scripts are appended only after the world is already initialized.
nader_ai=Path('tools/apply_nader_ai_admin.py')
if not nader_ai.exists(): raise SystemExit('apply_nader_ai_admin.py missing')
exec(compile(nader_ai.read_text(encoding='utf-8'),str(nader_ai),'exec'),{})

ai_server=Path('tools/apply_ai_server_url.py')
if not ai_server.exists(): raise SystemExit('apply_ai_server_url.py missing')
exec(compile(ai_server.read_text(encoding='utf-8'),str(ai_server),'exec'),{})
