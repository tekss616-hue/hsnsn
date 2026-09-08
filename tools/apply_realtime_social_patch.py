from pathlib import Path

# Runtime UI: instant search cleanup, live refresh hooks, remove-friend action,
# typing state and delivery/read ticks. Native bridge additions are appended below.
p=Path('app/src/main/assets/social.js')
s=p.read_text()

s=s.replace("function personHtml(p,actions='friend'){const status=", "function personHtml(p,actions='friend'){const status=",1)
s=s.replace("actions==='friend'?status:`<button class=\"tiny-btn\" data-chat=\"${esc(p.uid)}\" data-name=\"${esc(p.name)}\">مراسلة</button><button class=\"tiny-btn danger\" data-block=\"${esc(p.uid)}\">حظر</button>`", "actions==='friend'?status:`<button class=\"tiny-btn\" data-chat=\"${esc(p.uid)}\" data-name=\"${esc(p.name)}\">مراسلة</button><button class=\"tiny-btn\" data-remove=\"${esc(p.uid)}\">حذف صديق</button><button class=\"tiny-btn danger\" data-block=\"${esc(p.uid)}\">حظر</button>`")

# Message renderer supports sent/read state.
old="state.messages.map(m=>`<div class=\"bubble ${m.mine?'mine':'theirs'}\">${esc(m.text)}<time>${esc(m.time||'')}</time></div>`).join('')"
new="state.messages.map(m=>`<div class=\"bubble ${m.mine?'mine':'theirs'}\">${esc(m.text)}<time>${esc(m.time||'')} ${m.mine?(m.read?'✓✓':'✓'):''}</time></div>`).join('')"
s=s.replace(old,new)

# Clear stale result as soon as search field is cleared/changed.
needle="$('friendSearch').addEventListener('keydown',e=>{if(e.key==='Enter')$('friendSearchBtn').click()});"
extra=needle+"$('friendSearch').addEventListener('input',e=>{const q=e.target.value.trim();if(!q){lastSearch=null;activeSearch='';finishSearch();$('searchResult').innerHTML=''}else if(activeSearch&&q.replace(/^@/,'').toLowerCase()!==activeSearch){lastSearch=null;$('searchResult').innerHTML=''}});"
s=s.replace(needle,extra)

# Native realtime event callback.
insert="""
window.onNativeRealtimeEvent=e=>{if(!e)return;if(e.type==='socialChanged'){refresh()}else if(e.type==='friendAccepted'){toast((e.name||'المحقق')+' وافق على طلب صداقتك');refresh()}else if(e.type==='typing'&&currentPeer===e.uid){const n=$('chatPeerName');if(n)n.textContent=e.typing?(e.name||'المحقق')+' يكتب…':(e.name||'المحقق')}else if(e.type==='messagesChanged'&&currentPeer){NativeSocial.loadMessages(currentPeer)}};
"""
if 'window.onNativeRealtimeEvent' not in s:s=s.replace("$('socialBack').onclick",insert+"$('socialBack').onclick",1)

s=s.replace("else if(b.dataset.block){", "else if(b.dataset.remove){window.appConfirm?.('هل تريد حذف هذا الصديق؟',{title:'حذف صديق',ok:'حذف'}).then(ok=>{if(ok)NativeSocial.removeFriend(b.dataset.remove)})}else if(b.dataset.block){")
s=s.replace("$('chatInput').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();$('chatSend').click()}});", "$('chatInput').addEventListener('input',()=>{if(currentPeer&&NativeSocial?.setTyping)NativeSocial.setTyping(currentPeer,$('chatInput').value.trim().length>0)});$('chatInput').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();if(currentPeer&&NativeSocial?.setTyping)NativeSocial.setTyping(currentPeer,false);$('chatSend').click()}});")
p.write_text(s)

# Settings: remove navigation duplicates; keep actual settings/account actions.
p=Path('app/src/main/assets/index.html'); s=p.read_text()
s=s.replace('<button id="settingsProfile" class="setting-action">ملف المحقق</button><button id="settingsFriends" class="setting-action">الأصدقاء والمحادثات</button>','<div class="settings-section-label">الحساب</div>')
p.write_text(s)

# Remove JS bindings for settings buttons that no longer exist.
p=Path('app/src/main/assets/app.js'); s=p.read_text()
s=s.replace("$('hqSettings').onclick=()=>$('settingsSheet').hidden=false;$('closeSettings').onclick=()=>$('settingsSheet').hidden=true;$('settingsProfile').onclick=()=>{$('settingsSheet').hidden=true;window.openInvestigatorProfile?.()};$('settingsFriends').onclick=()=>{$('settingsSheet').hidden=true;window.openInvestigatorProfile?.();setTimeout(()=>document.querySelector('.social-nav button[data-panel=\"friends\"]')?.click(),20)};", "$('hqSettings').onclick=()=>$('settingsSheet').hidden=false;$('closeSettings').onclick=()=>$('settingsSheet').hidden=true;")
p.write_text(s)

# Native bridge: inject listener fields/helpers and methods into SocialBridge.
p=Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java'); s=p.read_text()
marker='    public class SocialBridge {'
helper=r'''    private com.google.firebase.firestore.ListenerRegistration rtRequests,rtFriends,rtNotes,rtMessages,rtTyping;
    private void realtimeEvent(String type,String uid,String name,boolean typing){
        try{JSONObject o=new JSONObject();o.put("type",type);if(uid!=null)o.put("uid",uid);if(name!=null)o.put("name",name);o.put("typing",typing);final String js="window.onNativeRealtimeEvent&&window.onNativeRealtimeEvent("+o+")";runOnUiThread(()->webView.evaluateJavascript(js,null));}catch(Exception ignored){}
    }
    private void stopRealtime(){if(rtRequests!=null)rtRequests.remove();if(rtFriends!=null)rtFriends.remove();if(rtNotes!=null)rtNotes.remove();if(rtMessages!=null)rtMessages.remove();if(rtTyping!=null)rtTyping.remove();rtRequests=rtFriends=rtNotes=rtMessages=rtTyping=null;}
'''
if 'private void realtimeEvent(' not in s:s=s.replace(marker,helper+marker,1)

# Add methods immediately inside SocialBridge.
methods=r'''
        @JavascriptInterface public void startRealtime(){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();stopRealtime();
            rtRequests=firestore.collection("friendRequests").whereEqualTo("toUid",u.getUid()).whereEqualTo("status","pending").addSnapshotListener((x,e)->{if(e==null)realtimeEvent("socialChanged",null,null,false);});
            rtFriends=firestore.collection("users").document(u.getUid()).collection("friends").addSnapshotListener((x,e)->{if(e==null)realtimeEvent("socialChanged",null,null,false);});
            rtNotes=firestore.collection("users").document(u.getUid()).collection("notifications").addSnapshotListener((x,e)->{if(e==null&&x!=null){for(com.google.firebase.firestore.DocumentChange c:x.getDocumentChanges()){if(c.getType()==com.google.firebase.firestore.DocumentChange.Type.ADDED){DocumentSnapshot d=c.getDocument();if("friend_accepted".equals(str(d,"type","")))realtimeEvent("friendAccepted",str(d,"fromUid",""),str(d,"fromName","المحقق"),false);}}}});
        });}
        @JavascriptInterface public void stopRealtimeSocial(){runOnUiThread(()->stopRealtime());}
        @JavascriptInterface public void removeFriend(String uid){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();WriteBatch b=firestore.batch();b.delete(firestore.collection("users").document(u.getUid()).collection("friends").document(uid));b.delete(firestore.collection("users").document(uid).collection("friends").document(u.getUid()));b.commit().addOnSuccessListener(v->{try{JSONObject o=new JSONObject();o.put("ok",true);o.put("action","friendRemoved");sendSocial(o);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("friendRemoved",e));});}
        @JavascriptInterface public void setTyping(String uid,boolean typing){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();String id=chatId(u.getUid(),uid);Map<String,Object> m=new HashMap<>();m.put("uid",u.getUid());m.put("name",authVisibleName(u).isEmpty()?"المحقق":authVisibleName(u));m.put("typing",typing);m.put("updatedAt",FieldValue.serverTimestamp());firestore.collection("chats").document(id).collection("typing").document(u.getUid()).set(m);});}
'''
if '@JavascriptInterface public void startRealtime()' not in s:s=s.replace(marker,marker+methods,1)

# Start message listener and mark peer messages read whenever chat is opened/refreshed.
load_marker='@JavascriptInterface public void loadMessages(String peerUid)'
if load_marker in s and 'rtMessages=firestore.collection("chats")' not in s:
    pos=s.index(load_marker)
    brace=s.index('{',pos)
    inject='''{ runOnUiThread(()->{FirebaseUser me=currentUser();if(me==null)return;ensureFirestore();String cid=chatId(me.getUid(),peerUid);if(rtMessages!=null)rtMessages.remove();rtMessages=firestore.collection("chats").document(cid).collection("messages").addSnapshotListener((snap,err)->{if(err==null)realtimeEvent("messagesChanged",peerUid,null,false);});if(rtTyping!=null)rtTyping.remove();rtTyping=firestore.collection("chats").document(cid).collection("typing").document(peerUid).addSnapshotListener((d,e)->{if(e==null&&d!=null&&d.exists())realtimeEvent("typing",peerUid,str(d,"name","المحقق"),Boolean.TRUE.equals(d.getBoolean("typing")));});});'''
    s=s[:brace]+inject+s[brace+1:]

p.write_text(s)
print('Applied realtime social patch')
