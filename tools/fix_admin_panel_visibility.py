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
// Settings can be opened from more than one runtime path, so verify against Firebase Auth every time it becomes visible.
document.addEventListener('click',e=>{if(e.target.closest?.('#hqSettings,[data-open-settings]'))setTimeout(syncAdminPanel,0)},true);
const sheet=$('settingsSheet');if(sheet)new MutationObserver(syncAdminPanel).observe(sheet,{attributes:true,attributeFilter:['hidden','class','style']});
setTimeout(syncAdminPanel,100);
})();
'''
jsf.write_text(js,encoding='utf-8')
print('Fixed admin panel visibility using authenticated Firebase account')

# Apply the first functional admin dashboard batch from the same build step.
admin_batch=Path('tools/apply_admin_first_batch.py')
if not admin_batch.exists():
    raise SystemExit('apply_admin_first_batch.py missing')
exec(compile(admin_batch.read_text(encoding='utf-8'),str(admin_batch),'exec'),{})
