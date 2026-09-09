from pathlib import Path
import re

H=Path('app/src/main/assets/index.html')
J=Path('app/src/main/assets/social.js')
C=Path('app/src/main/assets/social.css')
A=Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java')
h=H.read_text(encoding='utf-8'); j=J.read_text(encoding='utf-8'); c=C.read_text(encoding='utf-8'); a=A.read_text(encoding='utf-8')

# 1) Do not recreate already-delivered FCM social notifications when the app opens.
# Keep Firestore notification docs for history/state, but only use them for in-app state refresh.
notes_pat=r'rtNotes=firestore\.collection\("users"\)\.document\(u\.getUid\(\)\)\.collection\("notifications"\)\.addSnapshotListener\(\(x,e\)->\{.*?\}\}\);'
notes_new='''rtNotes=firestore.collection("users").document(u.getUid()).collection("notifications").addSnapshotListener((x,e)->{if(e==null&&x!=null){for(com.google.firebase.firestore.DocumentChange change:x.getDocumentChanges()){if(change.getType()!=com.google.firebase.firestore.DocumentChange.Type.ADDED)continue;DocumentSnapshot d=change.getDocument();if(Boolean.TRUE.equals(d.getBoolean("read")))continue;String type=str(d,"type","");if("friend_accepted".equals(type)){realtimeEvent("friendAccepted",str(d,"fromUid",""),str(d,"fromName","لاعب"),false);}d.getReference().update("read",true);}}});'''
a,n=re.subn(notes_pat,notes_new,a,count=1,flags=re.S)
if n!=1: raise SystemExit('second batch: realtime notifications listener not found')

# 2) Push acceptance immediately to the original requester through the authenticated server.
anchor='        @JavascriptInterface public void sendFriendPush(String baseUrl,String toUid)'
if anchor not in a: raise SystemExit('second batch: friend push bridge not found')
if 'sendFriendAcceptedPush(String baseUrl' not in a:
    pos=a.index(anchor)
    end=a.index('\n\n',pos)
    method='''\n        @JavascriptInterface public void sendFriendAcceptedPush(String baseUrl,String toUid){runOnUiThread(()->{FirebaseUser me=currentUser();if(me==null||baseUrl==null||!baseUrl.startsWith("https://"))return;me.getIdToken(false).addOnSuccessListener(tok->new Thread(()->{try{java.net.URL url=new java.net.URL(baseUrl.replaceAll("/+$","")+"/api/social/friend-accepted-push");java.net.HttpURLConnection conn=(java.net.HttpURLConnection)url.openConnection();conn.setRequestMethod("POST");conn.setConnectTimeout(7000);conn.setReadTimeout(7000);conn.setDoOutput(true);conn.setRequestProperty("Content-Type","application/json");conn.setRequestProperty("Authorization","Bearer "+tok.getToken());String body=new JSONObject().put("toUid",toUid).toString();try(java.io.OutputStream os=conn.getOutputStream()){os.write(body.getBytes(java.nio.charset.StandardCharsets.UTF_8));}conn.getResponseCode();conn.disconnect();}catch(Exception ignored){}}).start());});}\n'''
    a=a[:end]+method+a[end:]

# 3) Keep equipped cosmetic state with friend snapshots so frames follow the player everywhere.
# Friend docs are lightweight mirrors; saveCosmetics fans equipped state out to each friend mirror.
a=a.replace('x.put("rank",str(d,"rank","لاعب"));fa.put(x);','x.put("rank",str(d,"rank","لاعب"));x.put("equipped",str(d,"equippedCosmetics","{}"));fa.put(x);')
a=a.replace('x.put("rank",str(d,"rank","صانع الدور"));fa.put(x);','x.put("rank",str(d,"rank","صانع الدور"));x.put("equipped",str(d,"equippedCosmetics","{}"));fa.put(x);')

save_pat=r'        @JavascriptInterface public void saveCosmetics\(String inventory,String equipped\)\{.*?\}\n        @JavascriptInterface public void loadCosmetics\(\)'
save_new='''        @JavascriptInterface public void saveCosmetics(String inventory,String equipped){runOnUiThread(()->{FirebaseUser me=currentUser();if(me==null)return;ensureFirestore();Map<String,Object> mine=new HashMap<>();mine.put("inventoryCosmetics",inventory);mine.put("equippedCosmetics",equipped);firestore.collection("users").document(me.getUid()).set(mine,com.google.firebase.firestore.SetOptions.merge()).addOnSuccessListener(v->firestore.collection("users").document(me.getUid()).collection("friends").get().addOnSuccessListener(fs->{WriteBatch batch=firestore.batch();for(DocumentSnapshot f:fs.getDocuments()){Map<String,Object> mirror=new HashMap<>();mirror.put("equippedCosmetics",equipped);batch.set(firestore.collection("users").document(f.getId()).collection("friends").document(me.getUid()),mirror,com.google.firebase.firestore.SetOptions.merge());}batch.commit();}));});}\n        @JavascriptInterface public void loadCosmetics()'''
a,n=re.subn(save_pat,save_new,a,count=1,flags=re.S)
if n!=1: raise SystemExit('second batch: cosmetics persistence method not found')

# 4/5) One realtime query drives the chat UI directly. No extra Firestore GET after every message event.
watch_pat=r'        @JavascriptInterface public void watchChat\(String peerUid\)\{.*?\}\n        @JavascriptInterface public void stopChatWatch\(\)'
watch_new='''        @JavascriptInterface public void watchChat(String peerUid){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();String cid=chatId(u.getUid(),peerUid);if(rtMessages!=null)rtMessages.remove();if(rtTyping!=null)rtTyping.remove();rtMessages=firestore.collection("chats").document(cid).collection("messages").orderBy("createdAt",Query.Direction.ASCENDING).limitToLast(100).addSnapshotListener((snap,err)->{if(err!=null||snap==null)return;try{WriteBatch reads=firestore.batch();boolean hasReads=false;JSONArray arr=new JSONArray();for(DocumentSnapshot d:snap.getDocuments()){boolean mine=u.getUid().equals(d.getString("senderId"));boolean read=Boolean.TRUE.equals(d.getBoolean("read"));if(!mine&&!read){reads.update(d.getReference(),"read",true,"readAt",FieldValue.serverTimestamp());hasReads=true;}JSONObject m=new JSONObject();m.put("id",d.getId());m.put("text",str(d,"text",""));m.put("mine",mine);m.put("read",read||!mine);m.put("time",clock(d.get("createdAt")));arr.put(m);}if(hasReads)reads.commit();JSONObject out=new JSONObject();out.put("ok",true);out.put("action","messages");out.put("messages",arr);sendSocial(out);}catch(Exception ignored){}});rtTyping=firestore.collection("chats").document(cid).collection("typing").document(peerUid).addSnapshotListener((d,e)->{if(e==null&&d!=null&&d.exists()){boolean typing=Boolean.TRUE.equals(d.getBoolean("typing"));realtimeEvent("typing",peerUid,str(d,"name","لاعب"),typing);}});});}\n        @JavascriptInterface public void stopChatWatch()'''
a,n=re.subn(watch_pat,watch_new,a,count=1,flags=re.S)
if n!=1: raise SystemExit('second batch: realtime chat watch method not found')

# Ensure acceptance target is available to the JS push bridge.
# Current accept result has no uid, so return the original requester uid in the success payload.
a=a.replace('p.put("action","friendAccepted");sendSocial(p);','p.put("action","friendAccepted");p.put("uid",fromUid);sendSocial(p);',1)

# ---------- Store category pages ----------
if 'id="storeCategoryView"' not in h:
    block='''<main id="storeCategoryView" class="cosmetic-view store-category-view" hidden><header class="store-category-head"><button id="storeCategoryBack">‹</button><div><small>متجر اللاعب</small><h2 id="storeCategoryTitle">الإطارات</h2></div></header><div id="storeCategoryGrid" class="cosmetic-grid"></div></main>'''
    h=h.replace('<main id="inventoryView"',block+'<main id="inventoryView"',1)

# ---------- Final JS repairs / UX ----------
# Preserve the existing first-batch ownership logic but never dump unowned items into inventory.
old_render="function render(){let all=[...F.map(x=>card('frame',x)),...V.map(x=>card('avatar',x))].join('');if($('cosmeticStoreGrid'))$('cosmeticStoreGrid').innerHTML=all;if($('inventoryGrid'))$('inventoryGrid').innerHTML=all}"
new_render="""function render(){const owned=inv(),e=eq();if($('cosmeticStoreGrid'))$('cosmeticStoreGrid').innerHTML='<button class=\"store-category-card\" data-store-category=\"frame\"><b>الإطارات</b><small>عاين وجهّز إطارك</small></button><button class=\"store-category-card\" data-store-category=\"avatar\"><b>الأفاتارات</b><small>غيّر هوية شخصيتك</small></button><button class=\"store-category-card\" data-store-category=\"card\"><b>البطاقات</b><small>قريبًا</small></button><button class=\"store-category-card\" data-store-category=\"effect\"><b>المؤثرات</b><small>قريبًا</small></button>';if($('inventoryGrid')){const items=[...F.filter(x=>owned.frames.includes(x[0])||e.frame===x[0]).map(x=>card('frame',x)),...V.filter(x=>owned.avatars.includes(x[0])||e.avatar===x[0]).map(x=>card('avatar',x))];$('inventoryGrid').innerHTML=items.length?items.join(''):'<div class=\"inventory-empty\">مخزونك فارغ. خذ أو اشترِ عنصرًا من المتجر أولًا.</div>'}}"""
if old_render not in j: raise SystemExit('second batch: first-batch render function not found')
j=j.replace(old_render,new_render,1)

# The realtime native listener already sends the entire message snapshot, so do not issue another GET.
j=j.replace("else if(e.type==='messagesChanged'&&currentPeer){NativeSocial.loadMessages(currentPeer)}", "else if(e.type==='messagesChanged'&&currentPeer){/* snapshot payload is delivered directly by watchChat */}",1)

# Make typing state explicit, avoid a write on every single character, and keep it alive while actively typing.
typing_pat=r"let typingStopTimer=null;let typingPeer=null;\nfunction stopLocalTyping\(\).*?\$\('chatInput'\)\.addEventListener\('input',\(\)=>\{.*?\}\);"
typing_new="""let typingStopTimer=null;let typingKeepAlive=null;let typingPeer=null;let typingIsOn=false;
function stopLocalTyping(){if(typingStopTimer){clearTimeout(typingStopTimer);typingStopTimer=null}if(typingKeepAlive){clearInterval(typingKeepAlive);typingKeepAlive=null}const peer=typingPeer||currentPeer;if(peer&&typingIsOn&&NativeSocial?.setTyping){try{NativeSocial.setTyping(peer,false)}catch{}}typingIsOn=false;typingPeer=null}
$('chatInput').addEventListener('input',()=>{if(!currentPeer||!NativeSocial?.setTyping)return;const active=$('chatInput').value.trim().length>0;typingPeer=currentPeer;if(active&&!typingIsOn){typingIsOn=true;NativeSocial.setTyping(currentPeer,true);typingKeepAlive=setInterval(()=>{if(currentPeer===typingPeer&&typingIsOn)NativeSocial.setTyping(currentPeer,true)},2500)}if(!active){stopLocalTyping();return}if(typingStopTimer)clearTimeout(typingStopTimer);typingStopTimer=setTimeout(stopLocalTyping,1400)});"""
j,n=re.subn(typing_pat,typing_new,j,count=1,flags=re.S)
if n!=1: raise SystemExit('second batch: typing sender hook not found')

runtime=r'''
;(()=>{
 const SECOND_ROLEPLAY_BATCH=true,$=id=>document.getElementById(id);
 const catalog={frame:[['f1','جمر','frame-fire'],['f2','فضة','frame-silver'],['f3','ملكي','frame-gold'],['f4','ليل','frame-night']],avatar:[['a1','رعد','ر'],['a2','نادر','ن'],['a3','ساهر','س'],['a4','مزن','م']]};
 const inv=()=>{try{return JSON.parse(localStorage.getItem('rp_inv')||'{"frames":[],"avatars":[]}')}catch{return{frames:[],avatars:[]}}};
 const eq=()=>{try{return JSON.parse(localStorage.getItem('rp_eq')||'{}')}catch{return{}}};
 const frameClass=id=>({f1:'frame-fire',f2:'frame-silver',f3:'frame-gold',f4:'frame-night'}[id]||'');
 function equippedFrom(raw){try{const x=typeof raw==='string'?JSON.parse(raw):raw||{};return x.frame||''}catch{return''}}
 function categoryItem(kind,x){const on=eq()[kind]===x[0],owned=(inv()[kind+'s']||[]).includes(x[0]);const preview=kind==='frame'?`<div class="cosmetic-preview ${x[2]}">ل</div>`:`<div class="cosmetic-preview">${x[2]}</div>`;return `<div class="cosmetic-item">${preview}<b>${kind==='frame'?'إطار ':'أفاتار '}${x[1]}</b><small>مجاني</small><button data-kind="${kind}" data-item="${x[0]}">${on?'مستخدم':owned?'استخدام':'أخذ مجانًا'}</button></div>`}
 function openCategory(kind){const v=$('storeCategoryView'),g=$('storeCategoryGrid');if(!v||!g)return;document.querySelectorAll('main').forEach(x=>x.hidden=true);v.hidden=false;const names={frame:'الإطارات',avatar:'الأفاتارات',card:'البطاقات',effect:'المؤثرات'};$('storeCategoryTitle').textContent=names[kind]||'المتجر';const items=catalog[kind]||[];g.innerHTML=items.length?items.map(x=>categoryItem(kind,x)).join(''):'<div class="inventory-empty">هذا القسم قريبًا.</div>'}
 document.addEventListener('click',e=>{const b=e.target.closest?.('[data-store-category]');if(b){e.preventDefault();openCategory(b.dataset.storeCategory)}},true);
 $('storeCategoryBack')?.addEventListener('click',()=>{$('storeCategoryView').hidden=true;$('gameStore').hidden=false});
 // Acceptance push: the native success payload carries the original requester uid.
 let acceptTarget='';document.addEventListener('click',e=>{const b=e.target.closest?.('[data-accept]');if(b)acceptTarget=b.dataset.accept||''},true);
 const prev=window.onNativeSocialResult;window.onNativeSocialResult=r=>{prev?.(r);if(r?.ok&&r.action==='friendAccepted'){const uid=r.uid||acceptTarget;acceptTarget='';const base=(localStorage.getItem('hsnsn_ai_server_url')||'').trim();if(uid&&base)try{NativeSocial?.sendFriendAcceptedPush?.(base,uid)}catch{}};setTimeout(()=>applyFrames(document),0)};
 // Apply equipped frames to every identity element that exposes user data.
 function applyOne(host,raw){const id=equippedFrom(raw);const cls=frameClass(id);const av=host.matches?.('.mini-avatar,.public-avatar-core,.social-avatar')?host:host.querySelector?.('.mini-avatar,.public-avatar-core,.social-avatar,.world-avatar');if(!av)return;av.classList.remove('frame-fire','frame-silver','frame-gold','frame-night','equipped-frame');if(cls)av.classList.add('equipped-frame',cls)}
 function applyFrames(root){root.querySelectorAll?.('[data-equipped]').forEach(x=>applyOne(x,x.dataset.equipped));const self=eq().frame;document.querySelectorAll('#socialAvatar').forEach(x=>applyOne(x,{frame:self}));document.querySelectorAll('.person-card,.request-card,.chat-row').forEach(x=>{if(x.dataset.frame)applyOne(x,{frame:x.dataset.frame})})}
 const obs=new MutationObserver(()=>applyFrames(document));obs.observe(document.documentElement,{subtree:true,childList:true});setTimeout(()=>applyFrames(document),300);
 // Inventory is ownership-only even if older code tries to repaint it.
 const ig=$('inventoryGrid');if(ig)new MutationObserver(()=>{const owned=inv(),e=eq();ig.querySelectorAll('.cosmetic-item').forEach(el=>{const b=el.querySelector('[data-item]');if(!b)return;const list=owned[b.dataset.kind+'s']||[];if(!list.includes(b.dataset.item)&&e[b.dataset.kind]!==b.dataset.item)el.remove()})}).observe(ig,{childList:true});
})();
'''
if 'const SECOND_ROLEPLAY_BATCH=true' not in j:j+=runtime

# Add equipped data to friend/search/request cards and chat rows wherever data exists.
# personHtml is shared by friends/search.
j=j.replace('return `<div class="person-card" data-uid="${esc(p.uid)}">','const __eq=(()=>{try{return JSON.parse(p.equipped||\'{}\').frame||\'\'}catch{return\'\'}})();return `<div class="person-card" data-uid="${esc(p.uid)}" data-frame="${esc(__eq)}" data-equipped="${esc(p.equipped||\'{}\')}">',1)
# Request cards do not yet carry full profile cosmetics; keep the structure compatible for future payloads.
j=j.replace('<div class="request-card" data-uid="${esc(p.uid)}">','<div class="request-card" data-uid="${esc(p.uid)}" data-equipped="${esc(p.equipped||\'{}\')}">',1)
# Chat rows inherit the friend mirror cosmetic state by uid.
old_chats="state.chats.map(c=>`<button class=\"chat-row\" data-chat=\"${esc(c.uid)}\" data-name=\"${esc(c.name)}\""
new_chats="state.chats.map(c=>{const f=state.friends.find(x=>x.uid===c.uid)||{};let fr='';try{fr=JSON.parse(f.equipped||'{}').frame||''}catch{}return `<button class=\"chat-row\" data-frame=\"${esc(fr)}\" data-chat=\"${esc(c.uid)}\" data-name=\"${esc(c.name)}\""
if old_chats in j:
    j=j.replace(old_chats,new_chats,1).replace("</button>`).join(''):'<div class=\"empty-state\">لا توجد محادثات بعد.</div>'}","</button>`}).join(''):'<div class=\"empty-state\">لا توجد محادثات بعد.</div>'}",1)

# Public identity card should show the equipped frame too.
j=j.replace("$('publicIdentityAvatar').textContent=(p.name||'ل')[0];$('publicIdentityCard').hidden=false;", "$('publicIdentityAvatar').textContent=(p.name||'ل')[0];$('publicIdentityAvatar').classList.remove('frame-fire','frame-silver','frame-gold','frame-night','equipped-frame');try{const fr=JSON.parse(p.equipped||'{}').frame;if(fr){const fc={f1:'frame-fire',f2:'frame-silver',f3:'frame-gold',f4:'frame-night'}[fr];if(fc)$('publicIdentityAvatar').classList.add('equipped-frame',fc)}}catch{}$('publicIdentityCard').hidden=false;",1)

# ---------- CSS: category navigation + more premium programmatic frames ----------
if '/* second-roleplay-batch */' not in c:
    c+=r'''
/* second-roleplay-batch */
#cosmeticStoreGrid{grid-template-columns:1fr 1fr}.store-category-card{min-height:132px;border:1px solid #30383e;border-radius:22px;background:linear-gradient(145deg,#11171b,#090d10);color:#fff;padding:20px;text-align:right;display:flex;flex-direction:column;justify-content:flex-end;gap:7px}.store-category-card b{font-size:22px}.store-category-card small{color:#929ca3}.store-category-head{display:flex;align-items:center;gap:14px;margin-bottom:22px}.store-category-head button{width:44px;height:44px;border-radius:14px;border:1px solid #ffffff1f;background:#11171b;color:#fff;font-size:28px}.store-category-head h2{margin:2px 0 0}.inventory-empty{grid-column:1/-1;padding:34px 18px;border:1px dashed #354047;border-radius:18px;text-align:center;color:#8f999f}.equipped-frame{position:relative;isolation:isolate}.equipped-frame.frame-fire{box-shadow:0 0 0 3px #7f2519,0 0 0 7px #3b1712,0 0 24px #a83b2670}.equipped-frame.frame-fire:before{content:'';position:absolute;inset:-9px;border-radius:50%;border:2px solid transparent;border-top-color:#e06a3b;border-bottom-color:#652014;transform:rotate(-18deg)}.equipped-frame.frame-silver{box-shadow:0 0 0 3px #c4ccd2,0 0 0 7px #59636b,0 0 20px #dce8ef45}.equipped-frame.frame-silver:before{content:'';position:absolute;inset:-8px;border-radius:50%;border:1px dashed #e7eef2}.equipped-frame.frame-gold{box-shadow:0 0 0 3px #b59a32,0 0 0 7px #4f4217,0 0 28px #d0ab385c}.equipped-frame.frame-gold:before{content:'';position:absolute;inset:-10px;border-radius:50%;border:2px solid #806b24;clip-path:polygon(0 0,42% 0,42% 100%,0 100%)}.equipped-frame.frame-night{box-shadow:0 0 0 3px #59658e,0 0 0 7px #20263d,0 0 26px #59658e66}.equipped-frame.frame-night:before{content:'';position:absolute;inset:-9px;border-radius:50%;border:2px solid transparent;border-left-color:#8591c2;border-right-color:#3c456b;transform:rotate(25deg)}
'''

H.write_text(h,encoding='utf-8');J.write_text(j,encoding='utf-8');C.write_text(c,encoding='utf-8');A.write_text(a,encoding='utf-8')
print('Applied second roleplay batch: push dedupe/acceptance, store pages, owned inventory, global frames, realtime chat')
