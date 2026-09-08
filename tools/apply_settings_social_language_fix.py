from pathlib import Path

# -------- HTML: working settings sub-panels --------
idx = Path('app/src/main/assets/index.html')
html = idx.read_text(encoding='utf-8')

settings_marker = '<div id="settingsSheet"'
if settings_marker not in html:
    raise SystemExit('settingsSheet missing')

# Add a clear back-to-home control in settings.
pos = html.find(settings_marker)
h2 = html.find('<h2>الإعدادات</h2>', pos)
if h2 == -1:
    raise SystemExit('Settings heading missing')
if 'id="settingsHomeBack"' not in html:
    html = html[:h2] + '<div class="settings-topbar"><button id="settingsHomeBack" class="settings-back" aria-label="العودة">‹</button><h2>الإعدادات</h2></div>' + html[h2+len('<h2>الإعدادات</h2>'):]

# Add functional privacy/chat/language panels.
if 'id="privacyPanel"' not in html:
    panels = '''
<div id="privacyPanel" class="settings-subpanel" hidden><div class="subpanel-card"><header><button data-settings-close>‹</button><h2>الخصوصية والحظر</h2></header><p class="subpanel-copy">اللاعبون المحظورون</p><div id="blockedUsersList" class="blocked-list"><div class="empty-state">لا يوجد لاعبون محظورون.</div></div></div></div>
<div id="chatSettingsPanel" class="settings-subpanel" hidden><div class="subpanel-card"><header><button data-settings-close>‹</button><h2>إعدادات المحادثة</h2></header><label class="setting-toggle">مؤشرات الكتابة <input id="chatTypingPref" type="checkbox" checked></label><label class="setting-toggle">معاينة آخر رسالة <input id="chatPreviewPref" type="checkbox" checked></label><p class="subpanel-copy">اضغط مطولًا على أي محادثة لتثبيتها أو كتمها أو حذفها من قائمتك.</p></div></div>
<div id="languagePanel" class="settings-subpanel" hidden><div class="subpanel-card"><header><button data-settings-close>‹</button><h2>اللغة</h2></header><button class="setting-action language-choice" data-lang-choice="ar">العربية</button><button class="setting-action language-choice" data-lang-choice="en">English</button></div></div>
<div id="chatActionSheet" class="chat-actions-modal" hidden><div class="modal-card"><h2 id="chatActionName">المحادثة</h2><button id="chatPinAction" class="setting-action">تثبيت المحادثة</button><button id="chatMuteAction" class="setting-action">كتم الإشعارات</button><button id="chatDeleteAction" class="setting-action danger-setting">حذف المحادثة</button><button id="chatActionCancel" class="setting-action">إلغاء</button></div></div>
'''
    html = html.replace('<script src="app.js"></script>', panels + '<script src="app.js"></script>', 1)

idx.write_text(html, encoding='utf-8')

# -------- CSS: responsive settings + subpanels + stable text scaling --------
css_path = Path('app/src/main/assets/social.css')
css = css_path.read_text(encoding='utf-8')
if '/* settings-social-language-fix */' not in css:
    css += r'''
/* settings-social-language-fix */
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
.settings-sheet{align-items:stretch!important;overflow:hidden}.settings-card.pro-settings{width:min(100%,760px)!important;height:100dvh!important;max-height:100dvh!important;margin:0 auto!important;border-radius:0!important;overflow-y:auto!important;overscroll-behavior:contain;padding:calc(env(safe-area-inset-top) + 14px) clamp(16px,4vw,32px) calc(env(safe-area-inset-bottom) + 28px)!important}
.settings-topbar{position:sticky;top:-14px;z-index:6;display:grid;grid-template-columns:48px 1fr 48px;align-items:center;min-height:62px;margin:0 0 10px;background:#0b0e10eF;backdrop-filter:blur(12px)}.settings-topbar h2{grid-column:2;text-align:center;margin:0;font-size:clamp(22px,5vw,30px)}.settings-back{grid-column:1;grid-row:1;width:44px;height:44px;border:1px solid #ffffff25;border-radius:50%;background:#101519;color:#fff;font-size:30px;line-height:1}.pro-settings>.close{display:none!important}.pro-settings .setting-action{min-height:54px;font-size:clamp(15px,4vw,19px)}.pro-settings .setting-toggle{min-height:68px;font-size:clamp(15px,4vw,19px)}.pro-settings .settings-section-label{font-size:clamp(12px,3.2vw,14px)}
.settings-subpanel{position:fixed;inset:0;z-index:110;background:#070a0c;color:#f4f4f4;overflow:auto}.settings-subpanel[hidden],.chat-actions-modal[hidden]{display:none!important}.subpanel-card{width:min(100%,760px);min-height:100dvh;margin:auto;padding:calc(env(safe-area-inset-top) + 12px) clamp(16px,4vw,32px) calc(env(safe-area-inset-bottom) + 28px)}.subpanel-card header{position:sticky;top:0;z-index:3;display:grid;grid-template-columns:48px 1fr 48px;align-items:center;background:#070a0cef;backdrop-filter:blur(10px);min-height:64px}.subpanel-card header button{grid-column:1;width:44px;height:44px;border:1px solid #ffffff25;border-radius:50%;background:#101519;color:#fff;font-size:30px}.subpanel-card header h2{grid-column:2;grid-row:1;text-align:center;margin:0;font-size:clamp(20px,5vw,28px)}.subpanel-copy{color:#929ba3;line-height:1.7;margin:18px 2px}.blocked-list{display:grid;gap:10px}.blocked-person{display:flex;align-items:center;gap:12px;padding:14px;border:1px solid #2d353b;border-radius:16px;background:#0e1316}.blocked-person .person-info{flex:1}.blocked-person button{width:auto!important;min-width:100px}.language-choice{margin-top:12px!important;text-align:center!important}
#chatsList{display:flex;flex-direction:column}.chat-row.chat-pinned{order:-1;border-color:#8d2931!important}.chat-row.chat-muted .person-info small:after{content:' · مكتومة';color:#747d84}.chat-row.chat-hidden-by-user{display:none!important}.chat-actions-modal{z-index:150!important}.chat-actions-modal .modal-card{padding-bottom:calc(env(safe-area-inset-bottom) + 22px)}
html[dir="ltr"] body{text-align:left}.ltr-auto{direction:ltr}
@media(max-width:360px){.settings-card.pro-settings,.subpanel-card{padding-inline:12px!important}.pro-settings .setting-action{min-height:50px;font-size:15px}.pro-settings .setting-toggle{min-height:60px;font-size:15px}}
'''
css_path.write_text(css, encoding='utf-8')

# -------- JavaScript: working controls, chat long press, blocked list, language --------
js_path = Path('app/src/main/assets/social.js')
js = js_path.read_text(encoding='utf-8')
if 'SETTINGS_SOCIAL_LANGUAGE_FIX' not in js:
    js += r'''
;(()=>{
const SETTINGS_SOCIAL_LANGUAGE_FIX=true,$=id=>document.getElementById(id);
const blocked=new Map();
const prefObj=()=>{try{return JSON.parse(localStorage.getItem('chat_row_prefs')||'{}')}catch{return{}}};
const savePref=o=>{try{localStorage.setItem('chat_row_prefs',JSON.stringify(o))}catch{}};
function closeSettingsToHome(){const s=$('settingsSheet');if(s)s.hidden=true;document.querySelectorAll('.settings-subpanel').forEach(x=>x.hidden=true);window.showHQ?.()}
$('settingsHomeBack')?.addEventListener('click',closeSettingsToHome);
function openSub(id){const p=$(id);if(p)p.hidden=false}
document.querySelectorAll('[data-settings-close]').forEach(b=>b.onclick=()=>b.closest('.settings-subpanel').hidden=true);
$('settingPrivacy')?.addEventListener('click',()=>{openSub('privacyPanel');try{NativeSocial?.loadBlockedUsers?.()}catch{}});
$('settingChat')?.addEventListener('click',()=>openSub('chatSettingsPanel'));
$('settingLanguage')?.addEventListener('click',()=>openSub('languagePanel'));

// Make the notification setting affect native Android notifications, not only the checkbox UI.
const notif=$('settingNotifications');if(notif){const sync=()=>{try{NativeSocial?.setNotificationsEnabled?.(!!notif.checked)}catch{}};notif.addEventListener('change',sync);setTimeout(sync,100)}

function simplePref(id,key){const e=$(id);if(!e)return;try{e.checked=localStorage.getItem(key)!=='0'}catch{}e.addEventListener('change',()=>{try{localStorage.setItem(key,e.checked?'1':'0')}catch{}})}
simplePref('chatTypingPref','chat_typing_pref');simplePref('chatPreviewPref','chat_preview_pref');

function renderBlocked(){const box=$('blockedUsersList');if(!box)return;if(!blocked.size){box.innerHTML='<div class="empty-state">لا يوجد لاعبون محظورون.</div>';return}box.innerHTML=[...blocked.values()].map(p=>`<div class="blocked-person"><div class="mini-avatar">${(p.name||'م')[0]}</div><div class="person-info"><b>${p.name||'محقق'}</b><small>${p.username?'@'+p.username:''}</small></div><button class="tiny-btn" data-unblock="${p.uid}">فك الحظر</button></div>`).join('')}
$('privacyPanel')?.addEventListener('click',e=>{const b=e.target.closest('[data-unblock]');if(!b)return;try{NativeSocial?.unblockUser?.(b.dataset.unblock)}catch{}});

// Wrap native results so blocked players are represented correctly everywhere.
const previousResult=window.onNativeSocialResult;
window.onNativeSocialResult=r=>{if(r?.action==='blockedList'&&r.ok){blocked.clear();(r.players||[]).forEach(p=>blocked.set(p.uid,p));renderBlocked();return}if(r?.action==='unblocked'&&r.ok){blocked.delete(r.uid);renderBlocked();try{NativeSocial?.loadSocial?.()}catch{}return}if(r?.action==='blocked'&&r.ok){setTimeout(()=>{try{NativeSocial?.loadBlockedUsers?.()}catch{}},50)}if(r?.action==='search'&&r.player&&blocked.has(r.player.uid))r.player.blocked=true;previousResult?.(r);if(r?.action==='search'&&r.player&&blocked.has(r.player.uid)){setTimeout(()=>{const row=$('searchResult')?.querySelector('.person-card');const actions=row?.querySelector('.row-actions');if(actions)actions.innerHTML=`<button class="tiny-btn" data-unblock="${r.player.uid}">فك الحظر</button>`},0)}if(r?.action==='load')setTimeout(decorateChats,0)};
setTimeout(()=>{try{NativeSocial?.loadBlockedUsers?.()}catch{}},250);

// Long-press conversation management: pin, mute and delete for this user only.
let longTimer=null,longRow=null,longUid='',longName='';
function currentChatText(row){return row?.querySelector('.person-info small')?.textContent?.replace(/ · مكتومة$/,'').trim()||''}
function openChatActions(row){longRow=row;longUid=row.dataset.chat||'';longName=row.dataset.name||row.querySelector('.person-info b')?.textContent||'المحادثة';$('chatActionName').textContent=longName;const p=prefObj()[longUid]||{};$('chatPinAction').textContent=p.pinned?'إلغاء تثبيت المحادثة':'تثبيت المحادثة';$('chatMuteAction').textContent=p.muted?'إلغاء كتم الإشعارات':'كتم الإشعارات';$('chatActionSheet').hidden=false}
function decorateChats(){const prefs=prefObj();$('chatsList')?.querySelectorAll('.chat-row').forEach(row=>{const id=row.dataset.chat,p=prefs[id]||{},text=currentChatText(row);row.classList.toggle('chat-pinned',!!p.pinned);row.classList.toggle('chat-muted',!!p.muted);if(p.hiddenLast&&p.hiddenLast===text)row.classList.add('chat-hidden-by-user');else{row.classList.remove('chat-hidden-by-user');if(p.hiddenLast&&p.hiddenLast!==text){delete p.hiddenLast;prefs[id]=p;savePref(prefs)}}})}
const chats=$('chatsList');if(chats){new MutationObserver(decorateChats).observe(chats,{childList:true,subtree:true});chats.addEventListener('pointerdown',e=>{const row=e.target.closest('.chat-row');if(!row)return;clearTimeout(longTimer);longTimer=setTimeout(()=>openChatActions(row),650)});['pointerup','pointercancel','pointermove'].forEach(ev=>chats.addEventListener(ev,()=>clearTimeout(longTimer)))}
$('chatActionCancel')?.addEventListener('click',()=>$('chatActionSheet').hidden=true);
$('chatActionSheet')?.addEventListener('click',e=>{if(e.target===$('chatActionSheet'))$('chatActionSheet').hidden=true});
$('chatPinAction')?.addEventListener('click',()=>{const all=prefObj(),p=all[longUid]||{};p.pinned=!p.pinned;all[longUid]=p;savePref(all);$('chatActionSheet').hidden=true;decorateChats()});
$('chatMuteAction')?.addEventListener('click',()=>{const all=prefObj(),p=all[longUid]||{};p.muted=!p.muted;all[longUid]=p;savePref(all);$('chatActionSheet').hidden=true;decorateChats()});
$('chatDeleteAction')?.addEventListener('click',async()=>{if(!longUid)return;const ok=await (window.appConfirm?.('حذف هذه المحادثة من قائمتك؟ ستعود إذا وصلت رسالة جديدة.',{title:'حذف المحادثة',ok:'حذف',danger:true})??Promise.resolve(true));if(!ok)return;const all=prefObj(),p=all[longUid]||{};p.hiddenLast=currentChatText(longRow);all[longUid]=p;savePref(all);$('chatActionSheet').hidden=true;decorateChats()});

// Arabic/English. On first run use device language, then preserve the player's manual choice.
const AR_EN={
'اللعب':'Play','التصنيف':'Ranking','المتجر':'Store','الملف':'Profile','قسم التحقيق':'Investigation Division','غرفة التحقيق':'Investigation Room','ابدأ التحقيق':'Start Investigation','مطابقة تلقائية مع 6 محققين آخرين':'Automatic match with 6 other investigators','ملف المحقق':'Investigator Profile','الأصدقاء':'Friends','الطلبات':'Requests','المحادثات':'Chats','قائمة الأصدقاء':'Friends List','بحث':'Search','الإعدادات':'Settings','اللعبة':'Game','الصوت والمؤثرات':'Sound & effects','الاهتزاز':'Vibration','إشعارات اللعبة':'Game notifications','التجربة':'Experience','المظهر':'Appearance','داكن':'Dark','اللغة':'Language','العربية':'Arabic','الخصوصية والحظر':'Privacy & blocked players','إعدادات المحادثة':'Chat settings','الدعم':'Support','المساعدة والإبلاغ':'Help & report','الإصدار والتحديث':'Version & update','الحساب والأمان':'Account & security','تسجيل الخروج':'Sign out','حذف الحساب نهائيًا':'Delete account permanently','اللاعبون المحظورون':'Blocked players','لا يوجد لاعبون محظورون.':'No blocked players.','فك الحظر':'Unblock','مؤشرات الكتابة':'Typing indicators','معاينة آخر رسالة':'Last-message preview','تثبيت المحادثة':'Pin chat','إلغاء تثبيت المحادثة':'Unpin chat','كتم الإشعارات':'Mute notifications','إلغاء كتم الإشعارات':'Unmute notifications','حذف المحادثة':'Delete chat','إلغاء':'Cancel','تصنيف المحققين':'Investigator Ranking','متجر المحقق':'Investigator Store','أفاتارات':'Avatars','إطارات':'Frames','بطاقات المحقق':'Investigator cards','تأثيرات وحركات':'Effects & animations','قريبًا':'Coming soon','الشارات':'Badges','الحساب':'Account','القضايا':'Cases','المحلولة':'Solved','الدقة':'Accuracy','المستوى':'Level','إضافة صديق':'Add friend','تم إرسال الطلب':'Request sent','حذف صديق':'Remove friend','مراسلة':'Message','حظر':'Block','قبول':'Accept','رفض':'Decline','طلبات الصداقة':'Friend requests','لا توجد طلبات حالياً.':'No requests right now.','لا توجد محادثات بعد.':'No chats yet.','اكتب رسالة…':'Type a message…','ابدأ أول رسالة.':'Send the first message.','محقق أول':'Senior Investigator','محقق':'Investigator','لوحة الإدارة':'Admin panel'};
const EN_AR=Object.fromEntries(Object.entries(AR_EN).map(([a,e])=>[e,a]));
function translateText(t,lang){const raw=t.nodeValue,trim=raw.trim();if(!trim)return;const map=lang==='en'?AR_EN:EN_AR;if(map[trim])t.nodeValue=raw.replace(trim,map[trim])}
function translateElement(root,lang){const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode())translateText(n,lang);root.querySelectorAll?.('[placeholder]').forEach(e=>{const v=e.getAttribute('placeholder');const map=lang==='en'?AR_EN:EN_AR;if(map[v])e.setAttribute('placeholder',map[v])})}
function setLang(lang){lang=lang==='en'?'en':'ar';localStorage.setItem('app_language',lang);document.documentElement.lang=lang;document.documentElement.dir=lang==='ar'?'rtl':'ltr';translateElement(document.body,lang);const label=$('settingLanguage')?.querySelector('span');if(label)label.textContent=lang==='ar'?'العربية':'English';$('languagePanel').hidden=true}
let chosen=localStorage.getItem('app_language');if(!chosen){chosen=(navigator.language||'').toLowerCase().startsWith('ar')?'ar':'en';localStorage.setItem('app_language',chosen)}setLang(chosen);
document.querySelectorAll('[data-lang-choice]').forEach(b=>b.addEventListener('click',()=>setLang(b.dataset.langChoice)));
new MutationObserver(ms=>{const lang=localStorage.getItem('app_language')||'ar';ms.forEach(m=>m.addedNodes.forEach(n=>{if(n.nodeType===3)translateText(n,lang);else if(n.nodeType===1)translateElement(n,lang)}))}).observe(document.body,{childList:true,subtree:true});
})();
'''
js_path.write_text(js, encoding='utf-8')

# -------- Native Android: notification switch, block list/unblock, stable WebView text scale --------
java_path = Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java')
java = java_path.read_text(encoding='utf-8')

if 'settings.setTextZoom(100);' not in java:
    anchor='        settings.setDefaultTextEncodingName("utf-8");\n'
    if anchor not in java: raise SystemExit('WebSettings anchor missing')
    java=java.replace(anchor,anchor+'        settings.setTextZoom(100);\n',1)

# Honor app-level notification preference.
if 'notifications_enabled' not in java:
    anchor='    private void showNativeNotification(String title,String text){\n        try{'
    if anchor not in java: raise SystemExit('Native notification helper missing')
    java=java.replace(anchor,anchor+'if(!getSharedPreferences("app_settings",MODE_PRIVATE).getBoolean("notifications_enabled",true))return;',1)

bridge='    public class SocialBridge {'
methods=r'''
        @JavascriptInterface public void setNotificationsEnabled(boolean enabled){runOnUiThread(()->getSharedPreferences("app_settings",MODE_PRIVATE).edit().putBoolean("notifications_enabled",enabled).apply());}
        @JavascriptInterface public void loadBlockedUsers(){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("blockedList",null);return;}ensureFirestore();firestore.collection("users").document(u.getUid()).collection("blocks").get().addOnSuccessListener(q->{List<Task<DocumentSnapshot>> tasks=new ArrayList<>();List<String> ids=new ArrayList<>();for(DocumentSnapshot d:q.getDocuments()){ids.add(d.getId());tasks.add(firestore.collection("users").document(d.getId()).get());}if(tasks.isEmpty()){try{JSONObject out=new JSONObject();out.put("ok",true);out.put("action","blockedList");out.put("players",new JSONArray());sendSocial(out);}catch(Exception ignored){}return;}Tasks.whenAllSuccess(tasks).addOnSuccessListener(all->{try{JSONArray arr=new JSONArray();for(int i=0;i<all.size();i++){DocumentSnapshot d=(DocumentSnapshot)all.get(i);JSONObject p=new JSONObject();p.put("uid",ids.get(i));p.put("name",str(d,"name","محقق"));p.put("username",str(d,"username",""));arr.put(p);}JSONObject out=new JSONObject();out.put("ok",true);out.put("action","blockedList");out.put("players",arr);sendSocial(out);}catch(Exception e){socialError("blockedList",e);}});}).addOnFailureListener(e->socialError("blockedList",e));});}
        @JavascriptInterface public void unblockUser(String uid){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("unblocked",null);return;}ensureFirestore();firestore.collection("users").document(u.getUid()).collection("blocks").document(uid).delete().addOnSuccessListener(v->{try{JSONObject out=new JSONObject();out.put("ok",true);out.put("action","unblocked");out.put("uid",uid);sendSocial(out);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("unblocked",e));});}
'''
if '@JavascriptInterface public void loadBlockedUsers()' not in java:
    if bridge not in java: raise SystemExit('SocialBridge anchor missing')
    java=java.replace(bridge,bridge+methods,1)

# A sender who blocked the target must not be allowed to send a new request either.
old='Task<DocumentSnapshot> blocked=firestore.collection("users").document(toUid).collection("blocks").document(u.getUid()).get();\n'
if old in java and 'blockedByMe=' not in java:
    new=old+'                Task<DocumentSnapshot> blockedByMe=firestore.collection("users").document(u.getUid()).collection("blocks").document(toUid).get();\n'
    java=java.replace(old,new,1)
    java=java.replace('Tasks.whenAllSuccess(friend,blocked).addOnSuccessListener(all->{if(((DocumentSnapshot)all.get(0)).exists())', 'Tasks.whenAllSuccess(friend,blocked,blockedByMe).addOnSuccessListener(all->{if(((DocumentSnapshot)all.get(0)).exists())',1)
    java=java.replace('if(((DocumentSnapshot)all.get(1)).exists()){socialError("friendSent",new Exception("لا يمكن إرسال طلب لهذا اللاعب."));return;}', 'if(((DocumentSnapshot)all.get(1)).exists()||((DocumentSnapshot)all.get(2)).exists()){socialError("friendSent",new Exception("لا يمكن إرسال طلب لهذا اللاعب."));return;}',1)

java_path.write_text(java, encoding='utf-8')
print('Applied settings, blocking, chat management and bilingual UI fixes')
