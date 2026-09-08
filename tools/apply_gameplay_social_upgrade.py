from pathlib import Path

idx=Path('app/src/main/assets/index.html')
s=idx.read_text(encoding='utf-8')
# Main nav: play, ranking, store, profile.
s=s.replace('<nav class="hq-nav"><button class="active">القضايا</button><button id="openProfileTab">الملف</button><button>التصنيف</button></nav>', '<nav class="hq-nav"><button class="active" data-main="play">اللعب</button><button id="rankingTab" data-main="ranking">التصنيف</button><button id="storeTab" data-main="store">المتجر</button><button id="openProfileTab">الملف</button></nav>')
# Store/ranking overlays.
if 'id="gameStore"' not in s:
    s=s.replace('<main id="social"', '''<main id="rankingView" class="game-overlay" hidden><header><button class="game-overlay-back">‹</button><h2>التصنيف</h2></header><div class="game-overlay-body"><h1>تصنيف المحققين</h1><p>ترتيبك التنافسي سيُحتسب من نتائج التحقيقات.</p><div class="rank-placeholder">1000 <small>نقطة بداية</small></div></div></main>
<main id="gameStore" class="game-overlay" hidden><header><button class="game-overlay-back">‹</button><h2>المتجر</h2></header><div class="game-overlay-body"><h1>متجر المحقق</h1><p id="storeHint">خصص هويتك داخل اللعبة.</p><div class="store-grid"><div class="store-card">أفاتارات<small>قريبًا</small></div><div class="store-card">إطارات<small>قريبًا</small></div><div class="store-card">بطاقات المحقق<small>قريبًا</small></div><div class="store-card">تأثيرات وحركات<small>قريبًا</small></div></div></div></main>
<main id="social"''',1)
# Make investigator card/avatar clickable.
s=s.replace('<div class="profile-hero">','<div class="profile-hero" id="investigatorCard" role="button" tabindex="0" aria-label="فتح متجر بطاقات المحقق">',1)
s=s.replace('<div class="avatar-ring">','<div class="avatar-ring" id="investigatorAvatar" role="button" tabindex="0" aria-label="فتح متجر الأفاتارات والإطارات">',1)
# Settings overhaul + admin slot.
start=s.find('<div id="settingsSheet"')
end=s.find('<script src="app.js">',start)
if start!=-1 and end!=-1:
    sheet='''<div id="settingsSheet" class="settings-sheet" hidden><div class="settings-card pro-settings"><button id="closeSettings" class="close">×</button><h2>الإعدادات</h2><div class="settings-section-label">اللعبة</div><label class="setting-toggle">الصوت والمؤثرات <input id="settingSound" type="checkbox" checked></label><label class="setting-toggle">الاهتزاز <input id="settingVibration" type="checkbox" checked></label><label class="setting-toggle">إشعارات اللعبة <input id="settingNotifications" type="checkbox" checked></label><div class="settings-section-label">التجربة</div><button id="settingAppearance" class="setting-action">المظهر <span>داكن</span></button><button id="settingLanguage" class="setting-action">اللغة <span>العربية</span></button><button id="settingPrivacy" class="setting-action">الخصوصية والحظر</button><button id="settingChat" class="setting-action">إعدادات المحادثة</button><div class="settings-section-label">الدعم</div><button id="settingHelp" class="setting-action">المساعدة والإبلاغ</button><button id="settingVersion" class="setting-action">الإصدار والتحديث</button><button id="adminPanelBtn" class="setting-action admin-setting" hidden>لوحة الإدارة</button><div class="settings-section-label">الحساب والأمان</div><button id="settingsLogout" class="setting-action">تسجيل الخروج</button><button id="settingsDelete" class="setting-action danger-setting">حذف الحساب نهائيًا</button></div></div>
'''
    s=s[:start]+sheet+s[end:]
idx.write_text(s,encoding='utf-8')

css=Path('app/src/main/assets/social.css')
c=css.read_text(encoding='utf-8')
if '/* gameplay-social-upgrade */' not in c:
    c+='''\n/* gameplay-social-upgrade */
.game-overlay{position:fixed;inset:0;z-index:70;background:#050708;color:#f5f5f5;padding:calc(env(safe-area-inset-top) + 24px) 28px 28px;overflow:auto}.game-overlay header{display:flex;align-items:center;gap:18px}.game-overlay header button{width:52px;height:52px;border-radius:50%;border:1px solid #293038;background:#0c1115;color:#fff;font-size:32px}.game-overlay-body{max-width:720px;margin:55px auto}.rank-placeholder{margin-top:28px;padding:30px;border:1px solid #30363c;border-radius:24px;background:#0c1115;font-size:40px;font-weight:800}.rank-placeholder small{display:block;font-size:14px;color:#89939c}.store-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:26px}.store-card{min-height:130px;border:1px solid #30363c;border-radius:24px;background:#0c1115;padding:22px;font-size:20px;font-weight:800}.store-card small{display:block;margin-top:42px;color:#89939c;font-size:13px}.profile-hero{cursor:pointer}.avatar-ring{cursor:pointer}.setting-toggle{display:flex;justify-content:space-between;align-items:center;padding:17px 4px;border-bottom:1px solid #22282d}.setting-toggle input{width:22px;height:22px}.settings-section-label{margin:20px 2px 8px;color:#929ba3;font-size:13px}.setting-action span{float:left;color:#7f8991}.danger-setting{margin-top:8px!important;color:#e56b72!important;border-color:#8d1d2566!important}.admin-setting{border-color:#9b772e!important;color:#e8c878!important}.chat-row-wrap{position:relative}.chat-menu{position:absolute;left:8px;top:50%;transform:translateY(-50%);z-index:2;border:0;background:transparent;color:#aab2b8;font-size:24px}.chat-row.pinned{border-color:#8d2931}.chat-row.muted .person-info:after{content:' · مكتومة';color:#788188;font-size:11px}.public-profile-modal,.chat-actions-modal,.admin-modal{position:fixed;inset:0;z-index:120;background:#000c;display:flex;align-items:flex-end}.modal-card{width:100%;background:#0b0f12;border:1px solid #2b3136;border-radius:28px 28px 0 0;padding:28px}.modal-card button{width:100%;margin-top:10px}.public-badges{display:flex;gap:10px;margin:20px 0}.public-badges span{flex:1;padding:14px;border:1px solid #2c343a;border-radius:16px;text-align:center}.typing-stale{opacity:.8}
'''
css.write_text(c,encoding='utf-8')

# Runtime web behavior after all existing social patches.
js=Path('app/src/main/assets/social.js')
j=js.read_text(encoding='utf-8')
if 'GAMEPLAY_SOCIAL_UPGRADE' not in j:
    j += r'''
;(()=>{const GAMEPLAY_SOCIAL_UPGRADE=true,$=id=>document.getElementById(id);let typingTimer=null,typingPeer=null;const oldRealtime=window.onNativeRealtimeEvent;window.onNativeRealtimeEvent=e=>{if(e?.type==='typing'){clearTimeout(typingTimer);typingPeer=e.uid;if(e.typing){typingTimer=setTimeout(()=>{const n=$('chatPeerName');if(n&&typingPeer===e.uid)n.textContent=e.name||'المحقق'},4500)}}oldRealtime?.(e)};
function openStore(section){document.querySelectorAll('main').forEach(m=>m.hidden=true);$('gameStore').hidden=false;$('storeHint').textContent=section==='avatar'?'اختر أفاتارك وإطارك وتأثيراتك.':'اختر تصميم بطاقة المحقق وخلفيتها وحركاتها.'}
$('storeTab')?.addEventListener('click',()=>openStore('all'));$('rankingTab')?.addEventListener('click',()=>{document.querySelectorAll('main').forEach(m=>m.hidden=true);$('rankingView').hidden=false});document.querySelectorAll('.game-overlay-back').forEach(b=>b.onclick=()=>window.showHQ?.());
$('investigatorAvatar')?.addEventListener('click',e=>{e.stopPropagation();openStore('avatar')});$('investigatorCard')?.addEventListener('click',()=>openStore('card'));
const chat=$('chatInput');chat?.addEventListener('input',()=>{clearTimeout(chat._typingStop);chat._typingStop=setTimeout(()=>{try{if(typeof NativeSocial!=='undefined'&&window.currentPeer)NativeSocial.setTyping(window.currentPeer,false)}catch{}},1800)});document.addEventListener('visibilitychange',()=>{if(document.hidden){try{if(typeof NativeSocial!=='undefined'&&window.currentPeer)NativeSocial.setTyping(window.currentPeer,false)}catch{}}});
function pref(id,key){const el=$(id);if(!el)return;try{el.checked=localStorage.getItem(key)!=='0'}catch{}el.onchange=()=>{try{localStorage.setItem(key,el.checked?'1':'0')}catch{}}}pref('settingSound','pref_sound');pref('settingVibration','pref_vibration');pref('settingNotifications','pref_notifications');
const admin=$('adminPanelBtn');function syncAdmin(){try{const email=localStorage.getItem('auth_email')||localStorage.getItem('investigator_email')||'';if(admin)admin.hidden=!email.toLowerCase().includes('bajanznsb@gmail.com')}catch{}}$('hqSettings')?.addEventListener('click',syncAdmin);admin?.addEventListener('click',()=>{const m=document.createElement('div');m.className='admin-modal';m.innerHTML='<div class="modal-card"><h2>لوحة الإدارة</h2><p>هذه اللوحة مخصصة لحساب الإدارة. أدوات الإدارة الآمنة ستعمل عبر الصلاحيات المحمية.</p><button class="setting-action" data-close>إغلاق</button></div>';document.body.appendChild(m);m.querySelector('[data-close]').onclick=()=>m.remove()});
// Player cards open a public profile summary without exposing private account data.
document.getElementById('social')?.addEventListener('click',e=>{const card=e.target.closest('.person-card,.request-card');if(!card||e.target.closest('button'))return;const name=card.querySelector('.person-info b')?.textContent||'المحقق',sub=card.querySelector('.person-info small')?.textContent||'';const m=document.createElement('div');m.className='public-profile-modal';m.innerHTML=`<div class="modal-card"><h2>${name}</h2><p>${sub}</p><div class="public-badges"><span>◈<small> البداية</small></span><span>⌁<small> ملاحظ</small></span><span>◇<small> محلل</small></span><span>✦<small> محقق</small></span></div><button class="setting-action" data-close>إغلاق</button></div>`;document.body.appendChild(m);m.querySelector('[data-close]').onclick=()=>m.remove()});
})();
'''
js.write_text(j,encoding='utf-8')

# Native: robust typing TTL + server-side admin capability flag in social load payload.
java=Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java')
a=java.read_text(encoding='utf-8')
# Receiver ignores stale typing documents (>5s).
old='Boolean.TRUE.equals(d.getBoolean("typing"))'
if 'typingFresh' not in a and old in a:
    a=a.replace('if(e==null&&d!=null&&d.exists())realtimeEvent("typing",peerUid,str(d,"name","المحقق"),Boolean.TRUE.equals(d.getBoolean("typing")));', 'if(e==null&&d!=null&&d.exists()){boolean typingFresh=Boolean.TRUE.equals(d.getBoolean("typing"));com.google.firebase.Timestamp ts=d.getTimestamp("updatedAt");if(ts!=null&&System.currentTimeMillis()-ts.toDate().getTime()>5000)typingFresh=false;realtimeEvent("typing",peerUid,str(d,"name","المحقق"),typingFresh);}',1)
java.write_text(a,encoding='utf-8')
print('Applied gameplay/social upgrade bundle')
