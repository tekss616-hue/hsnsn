from pathlib import Path

idx=Path('app/src/main/assets/index.html'); html=idx.read_text(encoding='utf-8')
jsf=Path('app/src/main/assets/social.js'); js=jsf.read_text(encoding='utf-8')
cssf=Path('app/src/main/assets/social.css'); css=cssf.read_text(encoding='utf-8')

# Admin-only preview shell. Visibility is controlled at runtime by the already admin-gated panel button.
if 'id="adminPreviewMode"' not in html:
    html=html.replace('<script src="app.js"></script>', '''<main id="adminPreviewMode" class="admin-preview" hidden>
<header><button id="adminPreviewBack">‹</button><div><small>ADMIN ONLY</small><h2>وضع المعاينة</h2></div><span>بدون نقاط</span></header>
<section class="admin-preview-body"><div class="preview-note">معاينة محلية للقضية — لا تدخل المطابقة ولا تؤثر على التصنيف.</div><div class="preview-stage"><b id="adminPreviewStage">المرحلة 1 / 6</b><img id="adminPreviewImage" src="puzzle-1.svg" alt="صورة القضية"></div><div class="preview-controls"><button id="adminPreviewPrev">السابق</button><button id="adminPreviewNext">التالي</button></div></section>
</main>
<script src="app.js"></script>''',1)

if '/* remaining-round-fixes */' not in css:
    css += r'''
/* remaining-round-fixes */
.admin-preview{position:fixed;inset:0;z-index:180;background:#050708;color:#fff;overflow:auto}.admin-preview[hidden]{display:none!important}.admin-preview header{display:grid;grid-template-columns:52px 1fr auto;align-items:center;gap:12px;padding:calc(env(safe-area-inset-top) + 12px) 18px 14px;border-bottom:1px solid #ffffff16}.admin-preview header button{width:44px;height:44px;border-radius:50%;border:1px solid #ffffff22;background:#101519;color:#fff;font-size:30px}.admin-preview header small{color:#a67b7f}.admin-preview header h2{margin:2px 0}.admin-preview header span{font-size:12px;color:#9aa2a8}.admin-preview-body{max-width:720px;margin:auto;padding:24px}.preview-note{padding:14px;border:1px solid #7d283255;border-radius:14px;background:#51141d22;color:#c9b7b8}.preview-stage{margin-top:18px}.preview-stage b{display:block;margin-bottom:10px}.preview-stage img{display:block;width:100%;border-radius:20px;border:1px solid #ffffff18}.preview-controls{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px}.preview-controls button{min-height:52px;border:1px solid #ffffff20;border-radius:14px;background:#11161a;color:#fff;font-weight:800}
'''

if 'REMAINING_ROUND_FIXES' not in js:
    js += r'''
;(()=>{
const REMAINING_ROUND_FIXES=true,$=id=>document.getElementById(id);let previewStage=1;
const isAdmin=()=>{try{return (localStorage.getItem('auth_email')||localStorage.getItem('investigator_email')||'').trim().toLowerCase()==='bajanznsb@gmail.com'}catch{return false}};
function closeChatSheet(){const s=$('chatActionSheet');if(s)s.hidden=true}
// Close the long-press sheet immediately after every action click; confirmations may then appear separately.
['chatPinAction','chatMuteAction','chatDeleteAction','chatActionCancel'].forEach(id=>$(id)?.addEventListener('click',closeChatSheet,true));
// Make unblock from search use the same native operation as Settings > Privacy.
document.addEventListener('click',e=>{const b=e.target.closest?.('[data-unblock]');if(!b||b.closest('#privacyPanel'))return;e.preventDefault();e.stopImmediatePropagation();try{NativeSocial?.unblockUser?.(b.dataset.unblock)}catch{}},true);
// After unblocking anywhere, refresh both search/social state and blocked list.
const prevResult=window.onNativeSocialResult;window.onNativeSocialResult=r=>{prevResult?.(r);if(r?.action==='unblocked'&&r.ok){try{NativeSocial?.loadSocial?.();NativeSocial?.loadBlockedUsers?.()}catch{}}};
function renderPreview(){previewStage=Math.max(1,Math.min(6,previewStage));$('adminPreviewStage').textContent=`${document.documentElement.lang==='en'?'Stage':'المرحلة'} ${previewStage} / 6`;$('adminPreviewImage').src=`puzzle-${previewStage}.svg`}
function openPreview(){if(!isAdmin())return;document.querySelectorAll('main').forEach(m=>m.hidden=true);$('adminPreviewMode').hidden=false;previewStage=1;renderPreview()}
$('adminPreviewBack')?.addEventListener('click',()=>{ $('adminPreviewMode').hidden=true;window.showHQ?.()});$('adminPreviewPrev')?.addEventListener('click',()=>{previewStage--;renderPreview()});$('adminPreviewNext')?.addEventListener('click',()=>{previewStage++;renderPreview()});
// Add Preview Mode inside the admin panel only.
$('adminPanelBtn')?.addEventListener('click',()=>setTimeout(()=>{const modal=document.querySelector('.admin-modal .modal-card');if(!modal||modal.querySelector('[data-admin-preview]'))return;const b=document.createElement('button');b.className='setting-action';b.dataset.adminPreview='1';b.textContent=document.documentElement.lang==='en'?'Preview Mode':'وضع المعاينة';b.onclick=()=>{modal.closest('.admin-modal')?.remove();openPreview()};modal.insertBefore(b,modal.querySelector('[data-close]'))},0));
// Complete strings that remained Arabic in English mode, including game description and chat action UI.
const extra={
'سبعة محققين. ست صور. في كل صورة كلمة مفتاحية واحدة. اسأل النظام، ناقش من بقي في مرحلتك، وتقدم قبل الآخرين.':'Seven investigators. Six images. Each image hides one keyword. Ask the system, discuss with investigators still in your stage, and advance before the others.',
'رعد يكتب…':'Raad is typing…','يكتب…':'is typing…','حذف المحادثة':'Delete conversation','تثبيت المحادثة':'Pin conversation','إلغاء تثبيت المحادثة':'Unpin conversation','كتم الإشعارات':'Mute notifications','إلغاء كتم الإشعارات':'Unmute notifications','إلغاء':'Cancel','المحادثة':'Conversation','حذف هذه المحادثة من قائمتك؟ ستعود إذا وصلت رسالة جديدة.':'Delete this conversation from your list? It will return when a new message arrives.','حذف':'Delete','فك الحظر':'Unblock','قائمة الأصدقاء':'Friends List','أضف أصدقاء لتبدأ المحادثات الخاصة.':'Add friends to start private conversations.','للأصدقاء فقط':'Friends only','اكتب رسالة…':'Write a message…','ابحث باسم المستخدم أو اسم المحقق':'Search by username or investigator name','اسم_المستخدم@ أو اسم المحقق':'@username or investigator name','تم إرسال الطلب':'Request sent','محقق أول':'Junior Investigator','لوحة الإدارة':'Admin Panel','وضع المعاينة':'Preview Mode','السابق':'Previous','التالي':'Next','بدون نقاط':'No points'};
function translateExtras(){if(document.documentElement.lang!=='en')return;const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while(n=walker.nextNode()){const t=n.nodeValue.trim();if(extra[t])n.nodeValue=n.nodeValue.replace(t,extra[t])}document.querySelectorAll('input[placeholder]').forEach(x=>{if(extra[x.placeholder])x.placeholder=extra[x.placeholder]})}
new MutationObserver(()=>translateExtras()).observe(document.body,{childList:true,subtree:true});setTimeout(translateExtras,50);
})();
'''

idx.write_text(html,encoding='utf-8'); jsf.write_text(js,encoding='utf-8'); cssf.write_text(css,encoding='utf-8')
print('Applied remaining bilingual, unblock, chat-sheet and admin preview fixes')
