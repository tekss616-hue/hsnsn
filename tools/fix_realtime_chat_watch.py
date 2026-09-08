from pathlib import Path

# Keep social listeners active after login/HQ, not only after opening the social screen.
p=Path('app/src/main/assets/app.js')
s=p.read_text()
s=s.replace("hq.hidden=false;const currentName=", "hq.hidden=false;if(typeof NativeSocial!=='undefined'&&typeof NativeSocial.startRealtime==='function'){try{NativeSocial.startRealtime()}catch{}}const currentName=",1)
p.write_text(s)

# Open/close a single chat watch explicitly. loadMessages only fetches/render/marks read.
p=Path('app/src/main/assets/social.js')
s=p.read_text()
s=s.replace("currentPeer=b.dataset.chat;$('chatPeerName').textContent=b.dataset.name||'المحقق';$('chatView').hidden=false;NativeSocial.loadMessages(currentPeer)", "currentPeer=b.dataset.chat;$('chatPeerName').textContent=b.dataset.name||'المحقق';$('chatView').hidden=false;NativeSocial.watchChat?.(currentPeer);NativeSocial.loadMessages(currentPeer)")
s=s.replace("$('chatBack').onclick=()=>{$('chatView').hidden=true;currentPeer=null;refresh()}", "$('chatBack').onclick=()=>{$('chatView').hidden=true;NativeSocial.stopChatWatch?.();currentPeer=null;refresh()}")
p.write_text(s)

p=Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java')
s=p.read_text()
start=s.index('        @JavascriptInterface public void loadMessages(String peerUid)')
end=s.index('        @JavascriptInterface public void sendMessage(String peerUid,String text)',start)
replacement=r'''        @JavascriptInterface public void watchChat(String peerUid){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();String cid=chatId(u.getUid(),peerUid);if(rtMessages!=null)rtMessages.remove();if(rtTyping!=null)rtTyping.remove();rtMessages=firestore.collection("chats").document(cid).collection("messages").addSnapshotListener((snap,err)->{if(err==null)realtimeEvent("messagesChanged",peerUid,null,false);});rtTyping=firestore.collection("chats").document(cid).collection("typing").document(peerUid).addSnapshotListener((d,e)->{if(e==null&&d!=null&&d.exists())realtimeEvent("typing",peerUid,str(d,"name","المحقق"),Boolean.TRUE.equals(d.getBoolean("typing")));});});}
        @JavascriptInterface public void stopChatWatch(){runOnUiThread(()->{if(rtMessages!=null)rtMessages.remove();if(rtTyping!=null)rtTyping.remove();rtMessages=null;rtTyping=null;});}
        @JavascriptInterface public void loadMessages(String peerUid) { runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("messages",null);return;}ensureFirestore();String cid=chatId(u.getUid(),peerUid);firestore.collection("chats").document(cid).collection("messages").orderBy("createdAt", Query.Direction.ASCENDING).limitToLast(100).get().addOnSuccessListener(snap->{try{WriteBatch readBatch=firestore.batch();boolean hasReads=false;JSONArray arr=new JSONArray();for(DocumentSnapshot d:snap.getDocuments()){boolean mine=u.getUid().equals(d.getString("senderId"));boolean read=Boolean.TRUE.equals(d.getBoolean("read"));if(!mine&&!read){readBatch.update(d.getReference(),"read",true,"readAt",FieldValue.serverTimestamp());hasReads=true;}JSONObject m=new JSONObject();m.put("text",str(d,"text",""));m.put("mine",mine);m.put("read",read||!mine);m.put("time",clock(d.get("createdAt")));arr.put(m);}if(hasReads)readBatch.commit();JSONObject out=new JSONObject();out.put("ok",true);out.put("action","messages");out.put("messages",arr);sendSocial(out);}catch(Exception e){socialError("messages",e);}}).addOnFailureListener(e->socialError("messages",e));}); }
'''
s=s[:start]+replacement+s[end:]
p.write_text(s)

# Android 13+ system notifications require a manifest declaration as well as runtime consent.
p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text()
if 'android.permission.POST_NOTIFICATIONS' not in s:
    pos=s.find('>')+1
    s=s[:pos]+'\n    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />'+s[pos:]
p.write_text(s)
print('Fixed realtime chat watch lifecycle and notification permission')
