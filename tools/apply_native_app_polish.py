from pathlib import Path

# Add an in-app dialog so WebView never exposes file:// browser confirmations.
index=Path('app/src/main/assets/index.html')
s=index.read_text()
if 'id="appDialog"' not in s:
    modal='''\n<div id="appDialog" class="app-dialog" hidden aria-hidden="true"><div class="app-dialog-card" role="dialog" aria-modal="true" aria-labelledby="appDialogTitle"><div class="app-dialog-mark">◈</div><h3 id="appDialogTitle">تأكيد</h3><p id="appDialogMessage"></p><div class="app-dialog-actions"><button id="appDialogCancel" class="app-dialog-btn secondary">إلغاء</button><button id="appDialogOk" class="app-dialog-btn primary-dialog">تأكيد</button></div></div></div>\n'''
    s=s.replace('<script src="app.js"></script>',modal+'<script src="app.js"></script>',1)
index.write_text(s)

app=Path('app/src/main/assets/app.js')
s=app.read_text()
if 'function showAppDialog(' not in s:
    anchor="const store={get:(k,d=null)=>{try{return JSON.parse(localStorage.getItem(k))??d}catch{return d}},set:(k,v)=>localStorage.setItem(k,JSON.stringify(v)),del:k=>localStorage.removeItem(k)};"
    dialog=r'''\nlet appDialogResolve=null;\nfunction closeAppDialog(value){const d=$('appDialog');if(d){d.hidden=true;d.setAttribute('aria-hidden','true')}const r=appDialogResolve;appDialogResolve=null;if(r)r(value)}\nfunction showAppDialog(message,{title='تأكيد',ok='تأكيد',cancel='إلغاء',danger=false,notice=false}={}){const d=$('appDialog');if(!d)return Promise.resolve(false);$('appDialogTitle').textContent=title;$('appDialogMessage').textContent=message;const okBtn=$('appDialogOk'),cancelBtn=$('appDialogCancel');okBtn.textContent=ok;cancelBtn.textContent=cancel;cancelBtn.hidden=notice;okBtn.classList.toggle('danger-dialog',danger);d.hidden=false;d.setAttribute('aria-hidden','false');return new Promise(resolve=>{appDialogResolve=resolve})}\nwindow.appConfirm=(message,opts={})=>showAppDialog(message,opts);window.appNotice=(message,opts={})=>showAppDialog(message,{...opts,notice:true,ok:opts.ok||'حسنًا'});\n$('appDialogCancel').onclick=()=>closeAppDialog(false);$('appDialogOk').onclick=()=>closeAppDialog(true);$('appDialog').addEventListener('click',e=>{if(e.target===$('appDialog'))closeAppDialog(false)});\n'''
    s=s.replace(anchor,anchor+dialog,1)
s=s.replace("if(r?.action==='delete'){alert(friendlyAuthError(r?.message));return}","if(r?.action==='delete'){window.appNotice?.(friendlyAuthError(r?.message),{title:'تعذر حذف الحساب'});return}")
s=s.replace("if(r.action==='delete')alert('تم حذف الحساب.');return","if(r.action==='delete')window.appNotice?.('تم حذف الحساب بنجاح.',{title:'الحساب'});return")
s=s.replace("$('settingsLogout').onclick=()=>{if(confirm('تسجيل الخروج من الحساب؟'))NativeAuth?.signOut?.()};$('settingsDelete').onclick=()=>{if(!confirm('سيتم حذف حسابك نهائيًا ولا يمكن التراجع. هل أنت متأكد؟'))return;if(!confirm('تأكيد أخير: حذف الحساب نهائيًا؟'))return;NativeAuth?.deleteAccount?.()};","$('settingsLogout').onclick=async()=>{if(await window.appConfirm('هل تريد تسجيل الخروج من الحساب؟',{title:'تسجيل الخروج',ok:'تسجيل الخروج'}))NativeAuth?.signOut?.()};$('settingsDelete').onclick=async()=>{if(await window.appConfirm('سيتم حذف حسابك نهائيًا ولا يمكن التراجع عن هذه العملية.',{title:'حذف الحساب',ok:'حذف نهائيًا',danger:true}))NativeAuth?.deleteAccount?.()};")
# Returning Google accounts that already own a profile go straight in; legacy duplicate usernames are asked to choose a new one once.
s=s.replace("if(r.action==='google'){if(r.hasProfile&&r.name){store.set('investigator_name',r.name);if(r.username)store.set('investigator_username',r.username);showHQ(r.name)}else showGoogleSetup(r);return}","if(r.action==='google'){if(r.hasProfile&&r.name){store.set('investigator_name',r.name);if(r.username)store.set('investigator_username',r.username);showHQ(r.name)}else{showGoogleSetup(r);if(r.profileConflict)setTimeout(()=>error.textContent='اسم المستخدم السابق مرتبط بحساب آخر. اختر اسم مستخدم جديدًا وفريدًا.',40)}return}")
app.write_text(s)

social=Path('app/src/main/assets/social.js')
s=social.read_text()
s=s.replace("let currentPeer=null,lastSearch=null;const state=", "let currentPeer=null,lastSearch=null,searchBusy=false,searchTimer=null,activeSearch='';const state=",1)
if 'function setSearchBusy(' not in s:
    anchor="function native(){return typeof NativeSocial!=='undefined'}"
    helper=r'''function setSearchBusy(on){searchBusy=on;const b=$('friendSearchBtn');if(!b)return;b.disabled=on;b.classList.toggle('searching',on);b.innerHTML=on?'<span class="search-spinner" aria-hidden="true"></span><span>بحث</span>':'بحث'}function finishSearch(){clearTimeout(searchTimer);searchTimer=null;setSearchBusy(false)}'''
    s=s.replace(anchor,anchor+helper,1)
s=s.replace("window.onNativeSocialResult=r=>{if(!r)return;if(!r.ok){toast(r.message||'تعذر تحديث البيانات');return}","window.onNativeSocialResult=r=>{if(!r)return;if(!r.ok){if(r.action==='search')finishSearch();toast(r.message||'تعذر تحديث البيانات');return}")
s=s.replace("case'search':lastSearch=r.player||null;$('searchResult').innerHTML=lastSearch?personHtml(lastSearch):'<div class=\"empty-state\">لم نجد محققًا مطابقًا.</div>';break;","case'search':if(r.query&&activeSearch&&r.query!==activeSearch)break;finishSearch();lastSearch=r.player||null;$('searchResult').innerHTML=lastSearch?personHtml(lastSearch):'<div class=\"empty-state\">لم نجد محققًا مطابقًا.</div>';break;")
s=s.replace("$('friendSearchBtn').onclick=()=>{const q=$('friendSearch').value.trim();if(q.length<2)return toast('اكتب اسم المستخدم أو اسم المحقق');if(!native())return toast('الخدمة غير متاحة');$('searchResult').innerHTML='<div class=\"empty-state\">جارٍ البحث…</div>';NativeSocial.searchPlayer(q)};","$('friendSearchBtn').onclick=()=>{const q=$('friendSearch').value.trim();if(q.length<2)return toast('اكتب اسم المستخدم أو اسم المحقق');if(!native())return toast('الخدمة غير متاحة');if(searchBusy)return;activeSearch=q.replace(/^@/,'').toLowerCase();setSearchBusy(true);clearTimeout(searchTimer);searchTimer=setTimeout(()=>{finishSearch();toast('استغرق البحث وقتًا أطول من المتوقع. حاول مرة أخرى.')},5000);NativeSocial.searchPlayer(q)};")
s=s.replace("else if(b.dataset.block){if(confirm('حظر هذا اللاعب؟'))NativeSocial.blockUser(b.dataset.block)}", "else if(b.dataset.block){window.appConfirm?.('هل تريد حظر هذا اللاعب؟',{title:'حظر لاعب',ok:'حظر',danger:true}).then(ok=>{if(ok)NativeSocial.blockUser(b.dataset.block)})}")
s=s.replace("const logout=$('profileLogout');if(logout)logout.onclick=()=>{if(confirm('تسجيل الخروج من الحساب؟'))NativeAuth?.signOut?.()};const del=$('profileDelete');if(del)del.onclick=()=>{if(!confirm('سيتم حذف حسابك نهائيًا ولا يمكن التراجع. هل أنت متأكد؟'))return;if(!confirm('تأكيد أخير: حذف الحساب نهائيًا؟'))return;NativeAuth?.deleteAccount?.()};","const logout=$('profileLogout');if(logout)logout.onclick=async()=>{if(await window.appConfirm('هل تريد تسجيل الخروج من الحساب؟',{title:'تسجيل الخروج',ok:'تسجيل الخروج'}))NativeAuth?.signOut?.()};const del=$('profileDelete');if(del)del.onclick=async()=>{if(await window.appConfirm('سيتم حذف حسابك نهائيًا ولا يمكن التراجع عن هذه العملية.',{title:'حذف الحساب',ok:'حذف نهائيًا',danger:true}))NativeAuth?.deleteAccount?.()};")
social.write_text(s)

styles=Path('app/src/main/assets/styles.css')
s=styles.read_text()
polish=r'''\n/* Native-app interaction polish */\nhtml,body,body *{-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}\ninput,textarea,[contenteditable="true"]{-webkit-user-select:text;user-select:text;-webkit-touch-callout:default}\n.app-dialog{position:fixed;z-index:120;inset:0;background:rgba(0,0,0,.72);display:grid;place-items:center;padding:22px;backdrop-filter:blur(8px)}\n.app-dialog[hidden]{display:none}\n.app-dialog-card{width:min(92vw,420px);padding:24px 20px 18px;border:1px solid rgba(255,255,255,.14);border-radius:20px;background:linear-gradient(180deg,#121619,#090b0d);box-shadow:0 24px 70px #000;color:#f2f2f2;text-align:center;direction:rtl}\n.app-dialog-mark{width:48px;height:48px;margin:0 auto 12px;display:grid;place-items:center;border:1px solid #ffffff24;border-radius:50%;font-size:22px;color:#c9d0d4;background:#0b0f12}\n.app-dialog-card h3{margin:0 0 10px;font-size:21px}.app-dialog-card p{margin:0;color:#b8bec2;line-height:1.75;font-size:14px;white-space:pre-line}\n.app-dialog-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:22px}.app-dialog-btn{min-height:48px;border-radius:12px;border:1px solid #ffffff1c;font-weight:800}.app-dialog-btn.secondary{background:#15191c;color:#ddd}.app-dialog-btn.primary-dialog{background:#7b2027;color:#fff;border-color:#9c3038}.app-dialog-btn.danger-dialog{background:#811d26;border-color:#b13b45}.app-dialog-btn[hidden]{display:none}.app-dialog-btn[hidden]+.app-dialog-btn{grid-column:1/-1}\n#socialName,#socialUsername{display:block;width:100%;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}#socialUsername{direction:ltr;text-align:right;margin-top:2px}\n'''
if 'Native-app interaction polish' not in s:s+=polish
styles.write_text(s)

socialcss=Path('app/src/main/assets/social.css')
s=socialcss.read_text()
searchcss=r'''\n.social-action.searching{opacity:.82;pointer-events:none;display:flex;align-items:center;justify-content:center;gap:8px}.search-spinner{width:15px;height:15px;border:2px solid currentColor;border-left-color:transparent;border-radius:50%;animation:searchSpin .65s linear infinite}@keyframes searchSpin{to{transform:rotate(360deg)}}\n'''
if 'search-spinner' not in s:s+=searchcss
socialcss.write_text(s)
print('Applied native app polish')
