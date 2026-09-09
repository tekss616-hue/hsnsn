from pathlib import Path

A=Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java');a=A.read_text()
mark='        @JavascriptInterface public void searchPlayer(String query) {'
method=r'''        @JavascriptInterface public void sendFriendPush(String baseUrl,String toUid){runOnUiThread(()->{FirebaseUser me=currentUser();if(me==null||baseUrl==null||!baseUrl.startsWith("https://"))return;me.getIdToken(false).addOnSuccessListener(tok->new Thread(()->{try{java.net.URL url=new java.net.URL(baseUrl.replaceAll("/+$","")+"/api/social/friend-push");java.net.HttpURLConnection c=(java.net.HttpURLConnection)url.openConnection();c.setRequestMethod("POST");c.setConnectTimeout(7000);c.setReadTimeout(7000);c.setDoOutput(true);c.setRequestProperty("Content-Type","application/json");c.setRequestProperty("Authorization","Bearer "+tok.getToken());String body=new JSONObject().put("toUid",toUid).toString();try(java.io.OutputStream os=c.getOutputStream()){os.write(body.getBytes(java.nio.charset.StandardCharsets.UTF_8));}c.getResponseCode();c.disconnect();}catch(Exception ignored){}}).start());});}

'''
if 'sendFriendPush(String baseUrl' not in a:a=a.replace(mark,method+mark,1)
A.write_text(a)

J=Path('app/src/main/assets/social.js');j=J.read_text()
if 'FRIEND_PUSH_BRIDGE_V1' not in j:j+=r'''
;(()=>{const FRIEND_PUSH_BRIDGE_V1=true;let target='';document.addEventListener('click',e=>{const b=e.target.closest?.('[data-add]');if(b)target=b.dataset.add||''},true);const old=window.onNativeSocialResult;window.onNativeSocialResult=r=>{old?.(r);if(r?.ok&&r.action==='friendSent'&&target){const base=(localStorage.getItem('hsnsn_ai_server_url')||'').trim();if(base)try{NativeSocial?.sendFriendPush?.(base,target)}catch{}target=''}}})();
'''
J.write_text(j)
print('Connected successful friend requests to authenticated push sender')