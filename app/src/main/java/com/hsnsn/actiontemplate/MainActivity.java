package com.hsnsn.actiontemplate;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Bundle;
import android.os.CancellationSignal;
import android.graphics.Color;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.content.Intent;
import android.net.Uri;
import android.view.View;

import androidx.annotation.NonNull;
import androidx.credentials.CredentialManager;
import androidx.credentials.CredentialManagerCallback;
import androidx.credentials.CustomCredential;
import androidx.credentials.GetCredentialRequest;
import androidx.credentials.GetCredentialResponse;
import androidx.credentials.exceptions.GetCredentialException;

import com.google.android.gms.tasks.Task;
import com.google.android.gms.tasks.Tasks;
import com.google.android.libraries.identity.googleid.GetGoogleIdOption;
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential;
import com.google.firebase.Timestamp;
import com.google.firebase.auth.AuthCredential;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.auth.GoogleAuthProvider;
import com.google.firebase.auth.UserProfileChangeRequest;
import com.google.firebase.firestore.DocumentSnapshot;
import com.google.firebase.firestore.FieldValue;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.Query;
import com.google.firebase.firestore.QuerySnapshot;
import com.google.firebase.firestore.WriteBatch;

import org.json.JSONArray;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public class MainActivity extends Activity {
    private WebView webView;
    private ValueCallback<Uri[]> filePathCallback;
    private static final int FILE_CHOOSER_REQUEST = 1001;
    private FirebaseAuth firebaseAuth;
    private FirebaseFirestore firestore;
    private CredentialManager credentialManager;

    @SuppressLint({"SetJavaScriptEnabled", "JavascriptInterface"})
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().getDecorView().setBackgroundColor(Color.BLACK);
        getWindow().setStatusBarColor(Color.BLACK);
        getWindow().setNavigationBarColor(Color.BLACK);

        webView = new WebView(this);
        webView.setBackgroundColor(Color.BLACK);
        webView.setLayerType(View.LAYER_TYPE_HARDWARE, null);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setDefaultTextEncodingName("utf-8");

        webView.addJavascriptInterface(new AuthBridge(), "NativeAuth");
        webView.addJavascriptInterface(new SocialBridge(), "NativeSocial");
        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback,
                                             FileChooserParams fileChooserParams) {
                if (MainActivity.this.filePathCallback != null) MainActivity.this.filePathCallback.onReceiveValue(null);
                MainActivity.this.filePathCallback = filePathCallback;
                Intent intent = fileChooserParams.createIntent();
                try { startActivityForResult(intent, FILE_CHOOSER_REQUEST); }
                catch (Exception e) { MainActivity.this.filePathCallback = null; return false; }
                return true;
            }
        });
        webView.loadUrl("file:///android_asset/index.html");
    }

    private void ensureFirebaseAuth() { if (firebaseAuth == null) firebaseAuth = FirebaseAuth.getInstance(); }
    private void ensureFirestore() { if (firestore == null) firestore = FirebaseFirestore.getInstance(); }
    private void ensureCredentialManager() { if (credentialManager == null) credentialManager = CredentialManager.create(this); }
    private void warmAuthComponents() { runOnUiThread(() -> { ensureFirebaseAuth(); ensureCredentialManager(); ensureFirestore(); }); }

    private void upsertUser(FirebaseUser user) {
        if (user == null) return;
        ensureFirestore();
        Map<String,Object> data = new HashMap<>();
        String name = user.getDisplayName() == null ? "" : user.getDisplayName().trim();
        data.put("uid", user.getUid());
        data.put("name", name);
        data.put("nameLower", name.toLowerCase(Locale.ROOT));
        data.put("email", user.getEmail() == null ? "" : user.getEmail());
        data.put("rank", "محقق أول");
        data.put("updatedAt", FieldValue.serverTimestamp());
        firestore.collection("users").document(user.getUid()).set(data, com.google.firebase.firestore.SetOptions.merge());
    }

    private void sendAuthResult(boolean ok, String action, FirebaseUser user, String message) {
        try {
            JSONObject payload = new JSONObject();
            payload.put("ok", ok); payload.put("action", action);
            if (message != null) payload.put("message", message);
            if (user != null) {
                payload.put("uid", user.getUid());
                payload.put("email", user.getEmail() == null ? "" : user.getEmail());
                payload.put("name", user.getDisplayName() == null ? "" : user.getDisplayName());
            }
            final String js = "window.onNativeAuthResult&&window.onNativeAuthResult(" + payload + ")";
            runOnUiThread(() -> webView.evaluateJavascript(js, null));
        } catch (Exception ignored) { }
    }

    private void sendSocial(JSONObject payload) {
        runOnUiThread(() -> webView.evaluateJavascript("window.onNativeSocialResult&&window.onNativeSocialResult(" + payload + ")", null));
    }
    private void socialError(String action, Exception e) {
        try { JSONObject p = new JSONObject(); p.put("ok", false); p.put("action", action); p.put("message", e == null ? "تعذر إكمال العملية." : String.valueOf(e.getLocalizedMessage())); sendSocial(p); } catch (Exception ignored) { }
    }
    private FirebaseUser currentUser() { ensureFirebaseAuth(); return firebaseAuth.getCurrentUser(); }
    private String chatId(String a, String b) { return a.compareTo(b) < 0 ? a + "_" + b : b + "_" + a; }
    private String requestId(String from, String to) { return from + "_" + to; }
    private String str(DocumentSnapshot d, String k, String fallback) { String v = d.getString(k); return v == null || v.isEmpty() ? fallback : v; }
    private int number(DocumentSnapshot d, String k, int fallback) { Number n = d.get(k, Number.class); return n == null ? fallback : n.intValue(); }
    private String clock(Object o) { if (!(o instanceof Timestamp)) return ""; Date dt = ((Timestamp)o).toDate(); return new SimpleDateFormat("HH:mm", Locale.getDefault()).format(dt); }

    private void notifyJs(String functionName) { if (webView != null) webView.evaluateJavascript("window." + functionName + "&&window." + functionName + "()", null); }

    public class AuthBridge {
        @JavascriptInterface public void warmAuth() { warmAuthComponents(); }
        @JavascriptInterface public void createAccount(String name, String email, String password) {
            runOnUiThread(() -> { ensureFirebaseAuth(); firebaseAuth.createUserWithEmailAndPassword(email, password)
                .addOnSuccessListener(result -> {
                    FirebaseUser user = result.getUser(); if (user == null) { sendAuthResult(false,"create",null,"تعذر إنشاء الحساب."); return; }
                    UserProfileChangeRequest update = new UserProfileChangeRequest.Builder().setDisplayName(name).build();
                    user.updateProfile(update).addOnCompleteListener(t -> { upsertUser(user); sendAuthResult(true,"create",user,null); });
                }).addOnFailureListener(e -> sendAuthResult(false,"create",null,e.getLocalizedMessage())); });
        }
        @JavascriptInterface public void signInEmail(String email, String password) {
            runOnUiThread(() -> { ensureFirebaseAuth(); firebaseAuth.signInWithEmailAndPassword(email,password)
                .addOnSuccessListener(result -> { upsertUser(result.getUser()); sendAuthResult(true,"login",result.getUser(),null); })
                .addOnFailureListener(e -> sendAuthResult(false,"login",null,e.getLocalizedMessage())); });
        }
        @JavascriptInterface public void signInGoogle() {
            runOnUiThread(() -> { ensureFirebaseAuth(); ensureCredentialManager();
                GetGoogleIdOption googleIdOption = new GetGoogleIdOption.Builder().setFilterByAuthorizedAccounts(false).setServerClientId(getString(R.string.default_web_client_id)).build();
                GetCredentialRequest request = new GetCredentialRequest.Builder().addCredentialOption(googleIdOption).build();
                credentialManager.getCredentialAsync(MainActivity.this, request, new CancellationSignal(), getMainExecutor(), new CredentialManagerCallback<GetCredentialResponse, GetCredentialException>() {
                    @Override public void onResult(GetCredentialResponse result) {
                        if (!(result.getCredential() instanceof CustomCredential)) { sendAuthResult(false,"google",null,"تعذر قراءة بيانات حساب Google."); return; }
                        CustomCredential credential=(CustomCredential)result.getCredential();
                        if (!GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL.equals(credential.getType())) { sendAuthResult(false,"google",null,"نوع اعتماد Google غير مدعوم."); return; }
                        try { GoogleIdTokenCredential gc=GoogleIdTokenCredential.createFrom(credential.getData()); AuthCredential fc=GoogleAuthProvider.getCredential(gc.getIdToken(),null);
                            firebaseAuth.signInWithCredential(fc).addOnSuccessListener(auth->{ upsertUser(auth.getUser()); sendAuthResult(true,"google",auth.getUser(),null); }).addOnFailureListener(e->sendAuthResult(false,"google",null,e.getLocalizedMessage()));
                        } catch(Exception e){ sendAuthResult(false,"google",null,e.getLocalizedMessage()); }
                    }
                    @Override public void onError(@NonNull GetCredentialException e){ sendAuthResult(false,"google",null,e.getLocalizedMessage()); }
                });
            });
        }
        @JavascriptInterface public void updatePlayerName(String name) {
            runOnUiThread(() -> { FirebaseUser user=currentUser(); if(user==null){sendAuthResult(false,"playerName",null,"انتهت جلسة تسجيل الدخول. حاول مرة أخرى.");return;}
                UserProfileChangeRequest update=new UserProfileChangeRequest.Builder().setDisplayName(name).build(); user.updateProfile(update)
                    .addOnSuccessListener(v->{ upsertUser(user); sendAuthResult(true,"playerName",user,null); })
                    .addOnFailureListener(e->sendAuthResult(false,"playerName",null,e.getLocalizedMessage())); });
        }
        @JavascriptInterface public void signOut(){ runOnUiThread(()->{ensureFirebaseAuth();firebaseAuth.signOut();sendAuthResult(true,"logout",null,null);}); }
        @JavascriptInterface public void restoreSession(){ runOnUiThread(()->{FirebaseUser user=currentUser();if(user!=null)upsertUser(user);sendAuthResult(user!=null,"restore",user,null);}); }
    }

    public class SocialBridge {
        @JavascriptInterface public void loadSocial() {
            runOnUiThread(() -> {
                FirebaseUser u=currentUser(); if(u==null){socialError("load",null);return;} ensureFirestore(); upsertUser(u);
                Task<DocumentSnapshot> profile=firestore.collection("users").document(u.getUid()).get();
                Task<QuerySnapshot> friends=firestore.collection("users").document(u.getUid()).collection("friends").get();
                Task<QuerySnapshot> requests=firestore.collection("friendRequests").whereEqualTo("toUid",u.getUid()).whereEqualTo("status","pending").get();
                Task<QuerySnapshot> notes=firestore.collection("users").document(u.getUid()).collection("notifications").limit(50).get();
                Task<QuerySnapshot> chats=firestore.collection("chats").whereArrayContains("members",u.getUid()).limit(50).get();
                Tasks.whenAllSuccess(profile,friends,requests,notes,chats).addOnSuccessListener(all->{
                    try{
                        JSONObject out=new JSONObject();out.put("ok",true);out.put("action","load");
                        DocumentSnapshot pd=(DocumentSnapshot)all.get(0);JSONObject po=new JSONObject();po.put("name",str(pd,"name",u.getDisplayName()==null?"المحقق":u.getDisplayName()));po.put("rank",str(pd,"rank","محقق أول"));po.put("level",number(pd,"level",1));po.put("cases",number(pd,"cases",0));po.put("solved",number(pd,"solved",0));po.put("accuracy",number(pd,"accuracy",0));po.put("xpPercent",number(pd,"xpPercent",8));out.put("profile",po);
                        JSONArray fa=new JSONArray();for(DocumentSnapshot d:((QuerySnapshot)all.get(1)).getDocuments()){JSONObject x=new JSONObject();x.put("uid",d.getId());x.put("name",str(d,"name","محقق"));x.put("rank",str(d,"rank","محقق"));fa.put(x);}out.put("friends",fa);
                        JSONArray ra=new JSONArray();for(DocumentSnapshot d:((QuerySnapshot)all.get(2)).getDocuments()){JSONObject x=new JSONObject();x.put("uid",str(d,"fromUid",""));x.put("name",str(d,"fromName","محقق"));ra.put(x);}out.put("requests",ra);
                        JSONArray na=new JSONArray();for(DocumentSnapshot d:((QuerySnapshot)all.get(3)).getDocuments()){JSONObject x=new JSONObject();x.put("id",d.getId());x.put("read",Boolean.TRUE.equals(d.getBoolean("read")));x.put("type",str(d,"type",""));na.put(x);}out.put("notifications",na);
                        JSONArray ca=new JSONArray();for(DocumentSnapshot d:((QuerySnapshot)all.get(4)).getDocuments()){List<String> mem=(List<String>)d.get("members");if(mem==null)continue;String peer="";for(String id:mem)if(!id.equals(u.getUid()))peer=id;Map<String,Object> names=(Map<String,Object>)d.get("names");String peerName=names!=null&&names.get(peer)!=null?String.valueOf(names.get(peer)):"محقق";JSONObject x=new JSONObject();x.put("uid",peer);x.put("name",peerName);x.put("lastMessage",str(d,"lastMessage",""));ca.put(x);}out.put("chats",ca);sendSocial(out);
                    }catch(Exception e){socialError("load",e);}
                }).addOnFailureListener(e->socialError("load",e));
            });
        }

        @JavascriptInterface public void searchPlayer(String query) {
            runOnUiThread(() -> { FirebaseUser u=currentUser();if(u==null){socialError("search",null);return;}ensureFirestore();String q=query.trim().toLowerCase(Locale.ROOT);
                firestore.collection("users").whereEqualTo("nameLower",q).limit(1).get().addOnSuccessListener(s->{try{JSONObject out=new JSONObject();out.put("ok",true);out.put("action","search");if(!s.isEmpty()){DocumentSnapshot d=s.getDocuments().get(0);if(!d.getId().equals(u.getUid())){JSONObject p=new JSONObject();p.put("uid",d.getId());p.put("name",str(d,"name","محقق"));p.put("rank",str(d,"rank","محقق"));out.put("player",p);}}sendSocial(out);}catch(Exception e){socialError("search",e);}}).addOnFailureListener(e->socialError("search",e)); });
        }

        @JavascriptInterface public void sendFriendRequest(String toUid) {
            runOnUiThread(() -> { FirebaseUser u=currentUser();if(u==null||u.getUid().equals(toUid)){socialError("friendSent",null);return;}ensureFirestore();
                Task<DocumentSnapshot> friend=firestore.collection("users").document(u.getUid()).collection("friends").document(toUid).get();
                Task<DocumentSnapshot> blocked=firestore.collection("users").document(toUid).collection("blocks").document(u.getUid()).get();
                Tasks.whenAllSuccess(friend,blocked).addOnSuccessListener(all->{if(((DocumentSnapshot)all.get(0)).exists()){socialError("friendSent",new Exception("هذا اللاعب ضمن أصدقائك بالفعل."));return;}if(((DocumentSnapshot)all.get(1)).exists()){socialError("friendSent",new Exception("لا يمكن إرسال طلب لهذا اللاعب."));return;}
                    String id=requestId(u.getUid(),toUid);Map<String,Object> r=new HashMap<>();r.put("fromUid",u.getUid());r.put("fromName",u.getDisplayName()==null?"محقق":u.getDisplayName());r.put("toUid",toUid);r.put("status","pending");r.put("createdAt",FieldValue.serverTimestamp());
                    firestore.collection("friendRequests").document(id).set(r).addOnSuccessListener(v->{Map<String,Object> n=new HashMap<>();n.put("type","friend_request");n.put("fromUid",u.getUid());n.put("fromName",u.getDisplayName()==null?"محقق":u.getDisplayName());n.put("read",false);n.put("createdAt",FieldValue.serverTimestamp());firestore.collection("users").document(toUid).collection("notifications").add(n);try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","friendSent");sendSocial(p);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("friendSent",e));
                }).addOnFailureListener(e->socialError("friendSent",e)); });
        }

        @JavascriptInterface public void acceptFriendRequest(String fromUid) {
            runOnUiThread(() -> { FirebaseUser u=currentUser();if(u==null){socialError("friendAccepted",null);return;}ensureFirestore();String rid=requestId(fromUid,u.getUid());firestore.collection("friendRequests").document(rid).get().addOnSuccessListener(req->{if(!req.exists()||!"pending".equals(req.getString("status"))){socialError("friendAccepted",new Exception("الطلب لم يعد متاحًا."));return;}String fromName=str(req,"fromName","محقق");String myName=u.getDisplayName()==null?"محقق":u.getDisplayName();WriteBatch b=firestore.batch();Map<String,Object>a=new HashMap<>();a.put("name",fromName);a.put("rank","محقق");a.put("since",FieldValue.serverTimestamp());Map<String,Object>me=new HashMap<>();me.put("name",myName);me.put("rank","محقق");me.put("since",FieldValue.serverTimestamp());b.set(firestore.collection("users").document(u.getUid()).collection("friends").document(fromUid),a);b.set(firestore.collection("users").document(fromUid).collection("friends").document(u.getUid()),me);b.update(req.getReference(),"status","accepted","updatedAt",FieldValue.serverTimestamp());Map<String,Object>n=new HashMap<>();n.put("type","friend_accepted");n.put("fromUid",u.getUid());n.put("fromName",myName);n.put("read",false);n.put("createdAt",FieldValue.serverTimestamp());b.set(firestore.collection("users").document(fromUid).collection("notifications").document(),n);b.commit().addOnSuccessListener(v->{try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","friendAccepted");sendSocial(p);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("friendAccepted",e));}).addOnFailureListener(e->socialError("friendAccepted",e)); });
        }

        @JavascriptInterface public void rejectFriendRequest(String fromUid) { runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("friendRejected",null);return;}ensureFirestore();firestore.collection("friendRequests").document(requestId(fromUid,u.getUid())).update("status","rejected","updatedAt",FieldValue.serverTimestamp()).addOnSuccessListener(v->{try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","friendRejected");sendSocial(p);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("friendRejected",e));}); }
        @JavascriptInterface public void removeFriend(String uid) { runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("removed",null);return;}ensureFirestore();WriteBatch b=firestore.batch();b.delete(firestore.collection("users").document(u.getUid()).collection("friends").document(uid));b.delete(firestore.collection("users").document(uid).collection("friends").document(u.getUid()));b.commit().addOnSuccessListener(v->{try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","removed");sendSocial(p);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("removed",e));}); }
        @JavascriptInterface public void blockUser(String uid) { runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("blocked",null);return;}ensureFirestore();WriteBatch b=firestore.batch();Map<String,Object>x=new HashMap<>();x.put("createdAt",FieldValue.serverTimestamp());b.set(firestore.collection("users").document(u.getUid()).collection("blocks").document(uid),x);b.delete(firestore.collection("users").document(u.getUid()).collection("friends").document(uid));b.delete(firestore.collection("users").document(uid).collection("friends").document(u.getUid()));b.commit().addOnSuccessListener(v->{try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","blocked");sendSocial(p);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("blocked",e));}); }

        @JavascriptInterface public void loadMessages(String peerUid) { runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("messages",null);return;}ensureFirestore();firestore.collection("chats").document(chatId(u.getUid(),peerUid)).collection("messages").orderBy("createdAt", Query.Direction.ASCENDING).limitToLast(100).get().addOnSuccessListener(s->{try{JSONArray arr=new JSONArray();for(DocumentSnapshot d:s.getDocuments()){JSONObject m=new JSONObject();m.put("text",str(d,"text",""));m.put("mine",u.getUid().equals(d.getString("senderId")));m.put("time",clock(d.get("createdAt")));arr.put(m);}JSONObject p=new JSONObject();p.put("ok",true);p.put("action","messages");p.put("messages",arr);sendSocial(p);}catch(Exception e){socialError("messages",e);}}).addOnFailureListener(e->socialError("messages",e));}); }
        @JavascriptInterface public void sendMessage(String peerUid,String text) { runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("messageSent",null);return;}String clean=text==null?"":text.trim();if(clean.isEmpty()||clean.length()>1000){socialError("messageSent",new Exception("الرسالة غير صالحة."));return;}ensureFirestore();firestore.collection("users").document(u.getUid()).collection("friends").document(peerUid).get().addOnSuccessListener(f->{if(!f.exists()){socialError("messageSent",new Exception("المراسلة متاحة للأصدقاء فقط."));return;}String cid=chatId(u.getUid(),peerUid);String myName=u.getDisplayName()==null?"محقق":u.getDisplayName();String peerName=str(f,"name","محقق");Map<String,Object>chat=new HashMap<>();chat.put("members",Arrays.asList(u.getUid(),peerUid));Map<String,Object>names=new HashMap<>();names.put(u.getUid(),myName);names.put(peerUid,peerName);chat.put("names",names);chat.put("lastMessage",clean);chat.put("updatedAt",FieldValue.serverTimestamp());Map<String,Object>msg=new HashMap<>();msg.put("senderId",u.getUid());msg.put("text",clean);msg.put("createdAt",FieldValue.serverTimestamp());WriteBatch b=firestore.batch();b.set(firestore.collection("chats").document(cid),chat,com.google.firebase.firestore.SetOptions.merge());b.set(firestore.collection("chats").document(cid).collection("messages").document(),msg);b.commit().addOnSuccessListener(v->{try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","messageSent");sendSocial(p);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("messageSent",e));}).addOnFailureListener(e->socialError("messageSent",e));}); }
    }

    @Override protected void onPause(){if(webView!=null)notifyJs("onNativeAppPause");super.onPause();}
    @Override protected void onResume(){super.onResume();if(webView!=null)notifyJs("onNativeAppResume");}
    @Override protected void onActivityResult(int requestCode,int resultCode,Intent data){super.onActivityResult(requestCode,resultCode,data);if(requestCode==FILE_CHOOSER_REQUEST&&filePathCallback!=null){Uri[]results=WebChromeClient.FileChooserParams.parseResult(resultCode,data);filePathCallback.onReceiveValue(results);filePathCallback=null;}}
    @Override public void onBackPressed(){if(webView!=null&&webView.canGoBack())webView.goBack();else super.onBackPressed();}
}
