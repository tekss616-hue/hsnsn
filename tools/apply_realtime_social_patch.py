from pathlib import Path

# ---------- Web UI ----------
p=Path('app/src/main/assets/social.js')
s=p.read_text()

# Friend card: message + remove + block.
s=s.replace(
    "actions==='friend'?status:`<button class=\"tiny-btn\" data-chat=\"${esc(p.uid)}\" data-name=\"${esc(p.name)}\">مراسلة</button><button class=\"tiny-btn danger\" data-block=\"${esc(p.uid)}\">حظر</button>`",
    "actions==='friend'?status:`<button class=\"tiny-btn\" data-chat=\"${esc(p.uid)}\" data-name=\"${esc(p.name)}\">مراسلة</button><button class=\"tiny-btn\" data-remove=\"${esc(p.uid)}\">حذف صديق</button><button class=\"tiny-btn danger\" data-block=\"${esc(p.uid)}\">حظر</button>`"
)

# Request badge must represent real pending requests, not old unread notification docs.
s=s.replace(
    "const u=state.notifications.filter(x=>!x.read).length,b=$('socialBellBadge');b.textContent=u;b.hidden=!u",
    "const u=state.requests.length,b=$('socialBellBadge');b.textContent=u;b.hidden=!u"
)

# WhatsApp-like ticks.
s=s.replace(
    "state.messages.map(m=>`<div class=\"bubble ${m.mine?'mine':'theirs'}\">${esc(m.text)}<time>${esc(m.time||'')}</time></div>`).join('')",
    "state.messages.map(m=>`<div class=\"bubble ${m.mine?'mine':'theirs'}\">${esc(m.text)}<time>${esc(m.time||'')} ${m.mine?(m.read?'✓✓':'✓'):''}</time></div>`).join('')"
)

# Hide stale search card immediately when the query is cleared/changed.
needle="$('friendSearch').addEventListener('keydown',e=>{if(e.key==='Enter')$('friendSearchBtn').click()});"
if "friendSearch').addEventListener('input'" not in s:
    s=s.replace(needle,needle+"$('friendSearch').addEventListener('input',e=>{const q=e.target.value.trim();if(!q){lastSearch=null;activeSearch='';finishSearch();$('searchResult').innerHTML=''}else if(activeSearch&&q.replace(/^@/,'').toLowerCase()!==activeSearch){lastSearch=null;$('searchResult').innerHTML=''}});")

# Realtime event callback.
if 'window.onNativeRealtimeEvent' not in s:
    realtime="""window.onNativeRealtimeEvent=e=>{if(!e)return;if(e.type==='socialChanged'){refresh()}else if(e.type==='friendAccepted'){toast((e.name||'المحقق')+' وافق على طلب صداقتك');refresh()}else if(e.type==='typing'&&currentPeer===e.uid){const n=$('chatPeerName');if(n)n.textContent=e.typing?(e.name||'المحقق')+' يكتب…':(e.name||'المحقق')}else if(e.type==='messagesChanged'&&currentPeer){NativeSocial.loadMessages(currentPeer)}};\n"""
    s=s.replace("$('socialBack').onclick",realtime+"$('socialBack').onclick",1)

# Start realtime listeners whenever social UI opens.
s=s.replace(
    "window.openInvestigatorProfile=()=>{window.stopSceneAudio?.();document.querySelectorAll('main').forEach(m=>m.hidden=true);social.hidden=false;panel('profile');refresh()}",
    "window.openInvestigatorProfile=()=>{window.stopSceneAudio?.();document.querySelectorAll('main').forEach(m=>m.hidden=true);social.hidden=false;panel('profile');refresh();NativeSocial?.startRealtime?.()}"
)

# Remove friend button handler.
s=s.replace(
    "else if(b.dataset.block){",
    "else if(b.dataset.remove){window.appConfirm?.('هل تريد حذف هذا الصديق؟',{title:'حذف صديق',ok:'حذف'}).then(ok=>{if(ok)NativeSocial.removeFriend(b.dataset.remove)})}else if(b.dataset.block){"
)

# Typing state.
s=s.replace(
    "$('chatInput').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();$('chatSend').click()}});",
    "$('chatInput').addEventListener('input',()=>{if(currentPeer&&NativeSocial?.setTyping)NativeSocial.setTyping(currentPeer,$('chatInput').value.trim().length>0)});$('chatInput').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();if(currentPeer&&NativeSocial?.setTyping)NativeSocial.setTyping(currentPeer,false);$('chatSend').click()}});"
)

# React to native remove result immediately.
s=s.replace(
    "case'blocked':toast('تم حظر اللاعب');refresh();break;",
    "case'blocked':toast('تم حظر اللاعب');refresh();break;case'removed':case'friendRemoved':toast('تم حذف الصديق');refresh();break;"
)
p.write_text(s)

# Settings should contain settings/account actions, not duplicate navigation links.
p=Path('app/src/main/assets/index.html')
s=p.read_text()
s=s.replace('<button id="settingsProfile" class="setting-action">ملف المحقق</button><button id="settingsFriends" class="setting-action">الأصدقاء والمحادثات</button>','<div class="settings-section-label">الحساب</div>')
p.write_text(s)

p=Path('app/src/main/assets/app.js')
s=p.read_text()
s=s.replace("$('hqSettings').onclick=()=>$('settingsSheet').hidden=false;$('closeSettings').onclick=()=>$('settingsSheet').hidden=true;$('settingsProfile').onclick=()=>{$('settingsSheet').hidden=true;window.openInvestigatorProfile?.()};$('settingsFriends').onclick=()=>{$('settingsSheet').hidden=true;window.openInvestigatorProfile?.();setTimeout(()=>document.querySelector('.social-nav button[data-panel=\"friends\"]')?.click(),20)};", "$('hqSettings').onclick=()=>$('settingsSheet').hidden=false;$('closeSettings').onclick=()=>$('settingsSheet').hidden=true;")
p.write_text(s)

# ---------- Native Android / Firestore ----------
p=Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java')
s=p.read_text()
marker='    public class SocialBridge {'
helper=r'''    private com.google.firebase.firestore.ListenerRegistration rtRequests,rtFriends,rtNotes,rtMessages,rtTyping;
    private void realtimeEvent(String type,String uid,String name,boolean typing){
        try{JSONObject o=new JSONObject();o.put("type",type);if(uid!=null)o.put("uid",uid);if(name!=null)o.put("name",name);o.put("typing",typing);final String js="window.onNativeRealtimeEvent&&window.onNativeRealtimeEvent("+o+")";runOnUiThread(()->webView.evaluateJavascript(js,null));}catch(Exception ignored){}
    }
    private void stopRealtime(){if(rtRequests!=null)rtRequests.remove();if(rtFriends!=null)rtFriends.remove();if(rtNotes!=null)rtNotes.remove();if(rtMessages!=null)rtMessages.remove();if(rtTyping!=null)rtTyping.remove();rtRequests=rtFriends=rtNotes=rtMessages=rtTyping=null;}
    private void showNativeNotification(String title,String text){
        try{
            android.app.NotificationManager nm=(android.app.NotificationManager)getSystemService(android.content.Context.NOTIFICATION_SERVICE);
            String channel="social_updates";
            if(android.os.Build.VERSION.SDK_INT>=26)nm.createNotificationChannel(new android.app.NotificationChannel(channel,"تحديثات الأصدقاء",android.app.NotificationManager.IMPORTANCE_HIGH));
            if(android.os.Build.VERSION.SDK_INT>=33 && checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)!=android.content.pm.PackageManager.PERMISSION_GRANTED)return;
            android.app.Notification.Builder b=android.os.Build.VERSION.SDK_INT>=26?new android.app.Notification.Builder(this,channel):new android.app.Notification.Builder(this);
            b.setSmallIcon(android.R.drawable.ic_dialog_info).setContentTitle(title).setContentText(text).setAutoCancel(true);
            nm.notify((int)(System.currentTimeMillis()&0x7fffffff),b.build());
        }catch(Exception ignored){}
    }
'''
if 'private void realtimeEvent(' not in s:
    s=s.replace(marker,helper+marker,1)

# Android 13+ notification permission.
perm_anchor='        setContentView(webView);'
if 'requestPermissions(new String[]{android.Manifest.permission.POST_NOTIFICATIONS}' not in s:
    s=s.replace(perm_anchor,perm_anchor+'\n        if(android.os.Build.VERSION.SDK_INT>=33 && checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)!=android.content.pm.PackageManager.PERMISSION_GRANTED) requestPermissions(new String[]{android.Manifest.permission.POST_NOTIFICATIONS},7001);',1)

methods=r'''
        @JavascriptInterface public void startRealtime(){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();stopRealtime();
            rtRequests=firestore.collection("friendRequests").whereEqualTo("toUid",u.getUid()).whereEqualTo("status","pending").addSnapshotListener((x,e)->{if(e==null)realtimeEvent("socialChanged",null,null,false);});
            rtFriends=firestore.collection("users").document(u.getUid()).collection("friends").addSnapshotListener((x,e)->{if(e==null)realtimeEvent("socialChanged",null,null,false);});
            rtNotes=firestore.collection("users").document(u.getUid()).collection("notifications").addSnapshotListener((x,e)->{if(e==null&&x!=null){for(com.google.firebase.firestore.DocumentChange c:x.getDocumentChanges()){if(c.getType()!=com.google.firebase.firestore.DocumentChange.Type.ADDED)continue;DocumentSnapshot d=c.getDocument();if(Boolean.TRUE.equals(d.getBoolean("read")))continue;String type=str(d,"type","");String from=str(d,"fromName","المحقق");if("friend_request".equals(type)){showNativeNotification("طلب صداقة جديد",from+" أرسل لك طلب صداقة");}else if("friend_accepted".equals(type)){showNativeNotification("تم قبول طلب الصداقة",from+" وافق على طلب صداقتك");realtimeEvent("friendAccepted",str(d,"fromUid",""),from,false);}d.getReference().update("read",true);}}});
        });}
        @JavascriptInterface public void stopRealtimeSocial(){runOnUiThread(()->stopRealtime());}
        @JavascriptInterface public void setTyping(String uid,boolean typing){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();String id=chatId(u.getUid(),uid);Map<String,Object> m=new HashMap<>();m.put("uid",u.getUid());m.put("name",authVisibleName(u).isEmpty()?"المحقق":authVisibleName(u));m.put("typing",typing);m.put("updatedAt",FieldValue.serverTimestamp());firestore.collection("chats").document(id).collection("typing").document(u.getUid()).set(m);});}
'''
if '@JavascriptInterface public void startRealtime()' not in s:
    s=s.replace(marker,marker+methods,1)

old_load='''        @JavascriptInterface public void loadMessages(String peerUid) { runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("messages",null);return;}ensureFirestore();firestore.collection("chats").document(chatId(u.getUid(),peerUid)).collection("messages").orderBy("createdAt", Query.Direction.ASCENDING).limitToLast(100).get().addOnSuccessListener(s->{try{JSONArray arr=new JSONArray();for(DocumentSnapshot d:s.getDocuments()){JSONObject m=new JSONObject();m.put("text",str(d,"text",""));m.put("mine",u.getUid().equals(d.getString("senderId")));m.put("time",clock(d.get("createdAt")));arr.put(m);}JSONObject p=new JSONObject();p.put("ok",true);p.put("action","messages");p.put("messages",arr);sendSocial(p);}catch(Exception e){socialError("messages",e);}}).addOnFailureListener(e->socialError("messages",e));}); }'''
new_load='''        @JavascriptInterface public void loadMessages(String peerUid) { runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("messages",null);return;}ensureFirestore();String cid=chatId(u.getUid(),peerUid);if(rtMessages!=null)rtMessages.remove();rtMessages=firestore.collection("chats").document(cid).collection("messages").addSnapshotListener((snap,err)->{if(err==null)realtimeEvent("messagesChanged",peerUid,null,false);});if(rtTyping!=null)rtTyping.remove();rtTyping=firestore.collection("chats").document(cid).collection("typing").document(peerUid).addSnapshotListener((d,e)->{if(e==null&&d!=null&&d.exists())realtimeEvent("typing",peerUid,str(d,"name","المحقق"),Boolean.TRUE.equals(d.getBoolean("typing")));});firestore.collection("chats").document(cid).collection("messages").orderBy("createdAt", Query.Direction.ASCENDING).limitToLast(100).get().addOnSuccessListener(snap->{try{WriteBatch readBatch=firestore.batch();boolean hasReads=false;JSONArray arr=new JSONArray();for(DocumentSnapshot d:snap.getDocuments()){boolean mine=u.getUid().equals(d.getString("senderId"));if(!mine&&!Boolean.TRUE.equals(d.getBoolean("read"))){readBatch.update(d.getReference(),"read",true,"readAt",FieldValue.serverTimestamp());hasReads=true;}JSONObject m=new JSONObject();m.put("text",str(d,"text",""));m.put("mine",mine);m.put("read",Boolean.TRUE.equals(d.getBoolean("read"))||!mine);m.put("time",clock(d.get("createdAt")));arr.put(m);}if(hasReads)readBatch.commit();JSONObject out=new JSONObject();out.put("ok",true);out.put("action","messages");out.put("messages",arr);sendSocial(out);}catch(Exception e){socialError("messages",e);}}).addOnFailureListener(e->socialError("messages",e));}); }'''
s=s.replace(old_load,new_load)

old_send='''Map<String,Object>msg=new HashMap<>();msg.put("senderId",u.getUid());msg.put("text",clean);msg.put("createdAt",FieldValue.serverTimestamp());'''
new_send='''Map<String,Object>msg=new HashMap<>();msg.put("senderId",u.getUid());msg.put("text",clean);msg.put("read",false);msg.put("createdAt",FieldValue.serverTimestamp());'''
s=s.replace(old_send,new_send)

p.write_text(s)
print('Applied stable realtime social patch')
