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

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
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
    private String pendingUpdateUrl;
    private int pendingUpdateVersion;
    private boolean updateDownloadStarted;

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
        if(android.os.Build.VERSION.SDK_INT>=33 && checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)!=android.content.pm.PackageManager.PERMISSION_GRANTED) requestPermissions(new String[]{android.Manifest.permission.POST_NOTIFICATIONS},7001);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setDefaultTextEncodingName("utf-8");
        settings.setTextZoom(100);

        webView.addJavascriptInterface(new AuthBridge(), "NativeAuth");
        webView.addJavascriptInterface(new SocialBridge(), "NativeSocial");
        webView.addJavascriptInterface(new PuzzleBridge(), "NativePuzzle");
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
        com.google.firebase.messaging.FirebaseMessaging.getInstance().getToken().addOnSuccessListener(token->{FirebaseUser u=currentUser();if(u!=null){ensureFirestore();firestore.collection("users").document(u.getUid()).set(java.util.Collections.singletonMap("fcmToken",token),com.google.firebase.firestore.SetOptions.merge());}});
        webView.loadUrl("file:///android_asset/index.html");
        new Thread(this::checkForAppUpdate).start();
    }

    private static final String LATEST_RELEASE_API = "https://api.github.com/repos/tekss616-hue/hsnsn/releases/latest";

    private int getInstalledVersionCode() {
        try {
            android.content.pm.PackageInfo info = getPackageManager().getPackageInfo(getPackageName(), 0);
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.P) return (int) info.getLongVersionCode();
            return info.versionCode;
        } catch (Exception ignored) {
            return 0;
        }
    }

    private void checkForAppUpdate() {
        java.net.HttpURLConnection connection = null;
        try {
            java.net.URL url = new java.net.URL(LATEST_RELEASE_API);
            connection = (java.net.HttpURLConnection) url.openConnection();
            connection.setConnectTimeout(10000);
            connection.setReadTimeout(10000);
            connection.setRequestProperty("Accept", "application/vnd.github+json");
            connection.setRequestProperty("User-Agent", "HSNSN-Android");
            int response = connection.getResponseCode();
            if (response < 200 || response >= 300) return;
            java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.InputStreamReader(connection.getInputStream(), java.nio.charset.StandardCharsets.UTF_8));
            StringBuilder body = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) body.append(line);
            reader.close();
            JSONObject release = new JSONObject(body.toString());
            String tag = release.optString("tag_name", "");
            java.util.regex.Matcher matcher = java.util.regex.Pattern.compile("(\\d+)").matcher(tag);
            if (!matcher.find()) return;
            int latestCode = Integer.parseInt(matcher.group(1));
            if (latestCode <= getInstalledVersionCode()) return;
            JSONArray assets = release.optJSONArray("assets");
            if (assets == null) return;
            String apkUrl = "";
            for (int i = 0; i < assets.length(); i++) {
                JSONObject asset = assets.optJSONObject(i);
                if (asset == null) continue;
                String name = asset.optString("name", "");
                if (name.toLowerCase(Locale.ROOT).endsWith(".apk")) {
                    apkUrl = asset.optString("browser_download_url", "");
                    if (!apkUrl.isEmpty()) break;
                }
            }
            if (apkUrl.isEmpty()) return;
            final String foundUrl = apkUrl;
            final int foundCode = latestCode;
            final String foundTag = tag;
            runOnUiThread(() -> showUpdateDialog(foundCode, foundTag, foundUrl));
        } catch (Exception ignored) {
        } finally {
            if (connection != null) connection.disconnect();
        }
    }

    private void showUpdateDialog(int versionCode, String versionName, String apkUrl) {
        if (isFinishing()) return;
        new android.app.AlertDialog.Builder(this)
            .setTitle("تحديث جديد متوفر")
            .setMessage("يتوفر إصدار أحدث من التطبيق (" + versionName + "). اضغط تحديث الآن لتنزيله وتثبيته.")
            .setPositiveButton("تحديث الآن", (dialog, which) -> beginUpdateDownload(versionCode, apkUrl))
            .setNegativeButton("لاحقًا", null)
            .show();
    }

    private void beginUpdateDownload(int versionCode, String apkUrl) {
        pendingUpdateVersion = versionCode;
        pendingUpdateUrl = apkUrl;
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O && !getPackageManager().canRequestPackageInstalls()) {
            try {
                Intent settingsIntent = new Intent(android.provider.Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                    Uri.parse("package:" + getPackageName()));
                startActivity(settingsIntent);
            } catch (Exception ignored) { }
            return;
        }
        if (updateDownloadStarted) return;
        updateDownloadStarted = true;
        try {
            android.app.DownloadManager downloadManager = (android.app.DownloadManager) getSystemService(DOWNLOAD_SERVICE);
            String fileName = "hsnsn-update-" + versionCode + ".apk";
            android.app.DownloadManager.Request request = new android.app.DownloadManager.Request(Uri.parse(apkUrl))
                .setTitle("تحديث التطبيق")
                .setDescription("جارٍ تنزيل الإصدار الجديد...")
                .setNotificationVisibility(android.app.DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                .setDestinationInExternalFilesDir(this, android.os.Environment.DIRECTORY_DOWNLOADS, fileName);
            final long downloadId = downloadManager.enqueue(request);
            android.content.BroadcastReceiver receiver = new android.content.BroadcastReceiver() {
                @Override public void onReceive(android.content.Context context, Intent intent) {
                    if (intent == null || !android.app.DownloadManager.ACTION_DOWNLOAD_COMPLETE.equals(intent.getAction())) return;
                    if (intent.getLongExtra(android.app.DownloadManager.EXTRA_DOWNLOAD_ID, -1L) != downloadId) return;
                    try { unregisterReceiver(this); } catch (Exception ignored) { }
                    updateDownloadStarted = false;
                    Uri uri = downloadManager.getUriForDownloadedFile(downloadId);
                    if (uri == null) return;
                    try {
                        Intent install = new Intent(Intent.ACTION_VIEW)
                            .setDataAndType(uri, "application/vnd.android.package-archive")
                            .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
                        startActivity(install);
                    } catch (Exception ignored) { }
                }
            };
            android.content.IntentFilter filter = new android.content.IntentFilter(android.app.DownloadManager.ACTION_DOWNLOAD_COMPLETE);
            if (android.os.Build.VERSION.SDK_INT >= 33) registerReceiver(receiver, filter, android.content.Context.RECEIVER_EXPORTED);
            else registerReceiver(receiver, filter);
        } catch (Exception ignored) {
            updateDownloadStarted = false;
        }
    }

    private void resumePendingUpdate() {
        if (pendingUpdateUrl == null || pendingUpdateUrl.isEmpty() || updateDownloadStarted) return;
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O && !getPackageManager().canRequestPackageInstalls()) return;
        String url = pendingUpdateUrl;
        int code = pendingUpdateVersion;
        pendingUpdateUrl = null;
        beginUpdateDownload(code, url);
    }

    private void ensureFirebaseAuth() { if (firebaseAuth == null) firebaseAuth = FirebaseAuth.getInstance(); }
    private void ensureFirestore() { if (firestore == null) firestore = FirebaseFirestore.getInstance(); }
    private void ensureCredentialManager() { if (credentialManager == null) credentialManager = CredentialManager.create(this); }
    private void warmAuthComponents() { runOnUiThread(() -> { ensureFirebaseAuth(); ensureCredentialManager(); ensureFirestore(); }); }

    private void upsertUser(FirebaseUser user) {
        if (user == null) return;
        ensureFirestore();
        Map<String,Object> data = new HashMap<>();
        String name = authVisibleName(user);
        data.put("uid", user.getUid());
        data.put("name", name);
        data.put("nameLower", name.toLowerCase(Locale.ROOT));
        data.put("email", user.getEmail() == null ? "" : user.getEmail());
        data.put("rank", "صانع الدور");
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
    private boolean currentUserIsAdmin(){ FirebaseUser u=currentUser(); String e=u==null||u.getEmail()==null?"":u.getEmail().trim(); return "bajanznsb@gmail.com".equalsIgnoreCase(e); }
    private void adminLog(String action,String target){ if(!currentUserIsAdmin())return; ensureFirestore(); Map<String,Object>d=new HashMap<>();d.put("action",action);d.put("target",target==null?"":target);d.put("adminEmail","bajanznsb@gmail.com");d.put("createdAt",FieldValue.serverTimestamp());firestore.collection("adminLogs").add(d); }
    private String chatId(String a, String b) { return a.compareTo(b) < 0 ? a + "_" + b : b + "_" + a; }
    private String requestId(String from, String to) { return from + "_" + to; }
    private String str(DocumentSnapshot d, String k, String fallback) { String v = d.getString(k); return v == null || v.isEmpty() ? fallback : v; }
    private int number(DocumentSnapshot d, String k, int fallback) { Number n = d.get(k, Number.class); return n == null ? fallback : n.intValue(); }
    private String clock(Object o) { if (!(o instanceof Timestamp)) return ""; Date dt = ((Timestamp)o).toDate(); return new SimpleDateFormat("HH:mm", Locale.getDefault()).format(dt); }

    private void notifyJs(String functionName) { if (webView != null) webView.evaluateJavascript("window." + functionName + "&&window." + functionName + "()", null); }

    private void sendAdminAiResult(String requestId, boolean ok, int status, String body, String message) {
        try {
            JSONObject p=new JSONObject();p.put("requestId",requestId==null?"":requestId);p.put("ok",ok);p.put("status",status);p.put("body",body==null?"":body);if(message!=null)p.put("message",message);
            runOnUiThread(()->webView.evaluateJavascript("window.onNativeAdminAiResult&&window.onNativeAdminAiResult("+p+")",null));
        } catch(Exception ignored){}
    }

    private boolean currentUserIsAiAdmin(){ FirebaseUser u=currentUser(); String e=u==null||u.getEmail()==null?"":u.getEmail().trim(); return "bajanznsb@gmail.com".equalsIgnoreCase(e); }

    private void adminAiHttp(String requestId,String serverUrl,String path,String method,String body,String idToken){
        new Thread(()->{
            HttpURLConnection c=null;
            try{
                String base=serverUrl==null?"":serverUrl.trim();
                if(!base.startsWith("https://"))throw new Exception("يجب أن يبدأ عنوان السيرفر بـ https://");
                while(base.endsWith("/"))base=base.substring(0,base.length()-1);
                String cleanPath=path!=null&&path.startsWith("/")?path:"/"+(path==null?"":path);
                URL u=new URL(base+cleanPath);c=(HttpURLConnection)u.openConnection();c.setConnectTimeout(12000);c.setReadTimeout(30000);c.setRequestMethod(method==null?"POST":method);c.setRequestProperty("Authorization","Bearer "+idToken);c.setRequestProperty("Accept","application/json");c.setRequestProperty("Content-Type","application/json; charset=utf-8");
                if(!"GET".equalsIgnoreCase(method)){c.setDoOutput(true);byte[]bytes=(body==null?"{}":body).getBytes(StandardCharsets.UTF_8);try(OutputStream os=c.getOutputStream()){os.write(bytes);}}
                int status=c.getResponseCode();InputStream in=status>=200&&status<400?c.getInputStream():c.getErrorStream();StringBuilder out=new StringBuilder();if(in!=null){try(BufferedReader br=new BufferedReader(new InputStreamReader(in,StandardCharsets.UTF_8))){String line;while((line=br.readLine())!=null)out.append(line);}}
                sendAdminAiResult(requestId,status>=200&&status<300,status,out.toString(),null);
            }catch(Exception e){sendAdminAiResult(requestId,false,0,"",e.getLocalizedMessage());}finally{if(c!=null)c.disconnect();}
        }).start();
    }

    private static final String AUTH_PROFILE_SEP = "\u2063";
    private String authVisibleName(FirebaseUser u){
        String raw=u==null||u.getDisplayName()==null?"":u.getDisplayName();
        int i=raw.indexOf(AUTH_PROFILE_SEP);
        return (i>=0?raw.substring(0,i):raw).trim();
    }
    private String authEmbeddedUsername(FirebaseUser u){
        String raw=u==null||u.getDisplayName()==null?"":u.getDisplayName();
        int i=raw.indexOf(AUTH_PROFILE_SEP);
        return i>=0?raw.substring(i+AUTH_PROFILE_SEP.length()).trim().replaceFirst("^@","").toLowerCase(Locale.ROOT):"";
    }

    public class AuthBridge {
        @JavascriptInterface public void warmAuth() { warmAuthComponents(); }
        @JavascriptInterface public void adminAiRequest(String requestId,String serverUrl,String path,String method,String body){
            runOnUiThread(()->{
                if(!currentUserIsAiAdmin()){sendAdminAiResult(requestId,false,403,"","غير مصرح لحساب الإدارة.");return;}
                FirebaseUser u=currentUser();if(u==null){sendAdminAiResult(requestId,false,401,"","انتهت جلسة تسجيل الدخول.");return;}
                u.getIdToken(false).addOnSuccessListener(t->adminAiHttp(requestId,serverUrl,path,method,body,t.getToken())).addOnFailureListener(e->sendAdminAiResult(requestId,false,401,"",e.getLocalizedMessage()));
            });
        }
        @JavascriptInterface public boolean isAdminAccount(){ FirebaseUser u=currentUser(); String email=u==null||u.getEmail()==null?"":u.getEmail().trim(); return "bajanznsb@gmail.com".equalsIgnoreCase(email); }
        private String cleanUsername(String value){ return value==null?"":value.trim().replaceFirst("^@","").toLowerCase(Locale.ROOT); }
        private boolean validUsername(String value){ return value.matches("[a-z0-9_]{3,20}"); }
        private boolean isUsernameConflict(Exception e){
            Throwable x=e;
            while(x!=null){
                String m=String.valueOf(x.getMessage());
                if(m.contains("USERNAME_TAKEN")||m.contains("اسم المستخدم مستخدم بالفعل"))return true;
                if(x instanceof com.google.firebase.firestore.FirebaseFirestoreException && ((com.google.firebase.firestore.FirebaseFirestoreException)x).getCode()==com.google.firebase.firestore.FirebaseFirestoreException.Code.ABORTED)return true;
                x=x.getCause();
            }
            return false;
        }

        private Task<Void> claimProfileDocs(FirebaseUser u,String name,String username){
            ensureFirestore();String un=cleanUsername(username);
            com.google.firebase.firestore.DocumentReference uname=firestore.collection("usernames").document(un);
            com.google.firebase.firestore.DocumentReference uref=firestore.collection("users").document(u.getUid());
            return firestore.runTransaction(tr->{
                DocumentSnapshot existing=tr.get(uname);
                if(existing.exists()&&!u.getUid().equals(existing.getString("uid"))) throw new IllegalStateException("USERNAME_TAKEN");
                Map<String,Object> idx=new HashMap<>();idx.put("uid",u.getUid());idx.put("username",un);idx.put("updatedAt",FieldValue.serverTimestamp());tr.set(uname,idx);
                Map<String,Object>d=new HashMap<>();d.put("uid",u.getUid());d.put("name",name.trim());d.put("nameLower",name.trim().toLowerCase(Locale.ROOT));d.put("username",un);d.put("usernameLower",un);d.put("email",u.getEmail()==null?"":u.getEmail());d.put("rank","صانع الدور");d.put("updatedAt",FieldValue.serverTimestamp());
                tr.set(uref,d,com.google.firebase.firestore.SetOptions.merge());return null;
            });
        }

        private void dispatchProfile(String action,FirebaseUser user,String name,String username,boolean hasProfile,boolean conflict){
            try{JSONObject payload=new JSONObject();payload.put("ok",true);payload.put("action",action);payload.put("uid",user.getUid());payload.put("email",user.getEmail()==null?"":user.getEmail());payload.put("name",name==null?"":name);payload.put("username",username==null?"":username);payload.put("hasProfile",hasProfile);if(conflict)payload.put("profileConflict",true);final String js="window.onNativeAuthResult&&window.onNativeAuthResult("+payload+")";runOnUiThread(()->webView.evaluateJavascript(js,null));}catch(Exception ignored){}
        }
        private void normalizeVisibleDisplayName(FirebaseUser user,String visibleName){
            if(user==null||visibleName==null||visibleName.trim().isEmpty())return;
            String raw=authVisibleName(user);
            if(!raw.equals(visibleName.trim())){UserProfileChangeRequest up=new UserProfileChangeRequest.Builder().setDisplayName(visibleName.trim()).build();user.updateProfile(up);}
        }
        private void sendProfileAuth(String action,FirebaseUser user,boolean hintedProfile){
            if(user==null){sendAuthResult(false,action,null,"تعذر قراءة الحساب.");return;}
            final String fallbackName=authVisibleName(user);final String legacyUsername=cleanUsername(authEmbeddedUsername(user));ensureFirestore();
            firestore.collection("users").document(user.getUid()).get().addOnCompleteListener(t->{
                if(!t.isSuccessful()){sendAuthResult(false,action,null,"تعذر قراءة هوية المحقق من الخادم.");return;}
                String name=fallbackName,username=legacyUsername;boolean docExists=t.getResult()!=null&&t.getResult().exists();
                if(docExists){DocumentSnapshot d=t.getResult();/* ACCOUNT_ADMIN_BAN_GUARD */if(Boolean.TRUE.equals(d.getBoolean("banned"))){ensureFirebaseAuth();firebaseAuth.signOut();sendAuthResult(false,action,null,"تم إيقاف هذا الحساب من إدارة اللعبة.");return;}String dn=str(d,"name",name),du=cleanUsername(str(d,"username",username));if(!dn.isEmpty())name=dn;if(!du.isEmpty())username=du;}
                final String finalName=name,finalUsername=username;
                if(finalUsername.isEmpty()){normalizeVisibleDisplayName(user,finalName);dispatchProfile(action,user,finalName,"",false,false);return;}
                firestore.collection("usernames").document(finalUsername).get().addOnCompleteListener(idxTask->{
                    if(!idxTask.isSuccessful()){sendAuthResult(false,action,null,"تعذر التحقق من اسم المستخدم.");return;}
                    DocumentSnapshot idx=idxTask.getResult();String owner=idx!=null&&idx.exists()?idx.getString("uid"):null;
                    if(owner!=null&&!owner.isEmpty()&&!user.getUid().equals(owner)){dispatchProfile(action,user,finalName,finalUsername,false,true);return;}
                    claimProfileDocs(user,finalName.isEmpty()?"المحقق":finalName,finalUsername).addOnCompleteListener(claim->{
                        if(claim.isSuccessful()){normalizeVisibleDisplayName(user,finalName);dispatchProfile(action,user,finalName,finalUsername,true,false);}
                        else if(isUsernameConflict(claim.getException()))dispatchProfile(action,user,finalName,finalUsername,false,true);
                        else sendAuthResult(false,action,null,"تعذر مزامنة هوية المحقق مع الخادم.");
                    });
                });
            });
        }
        private void finishProfileAuth(FirebaseUser user,String name,String username,String action){
            UserProfileChangeRequest up=new UserProfileChangeRequest.Builder().setDisplayName(name.trim()).build();
            user.updateProfile(up).addOnCompleteListener(t->{if(t.isSuccessful())dispatchProfile(action,user,name.trim(),cleanUsername(username),true,false);else sendAuthResult(false,action,null,t.getException()==null?"تعذر حفظ اسم المحقق.":t.getException().getLocalizedMessage());});
        }
        private void reserveAndSaveProfile(FirebaseUser user,String name,String username,String action){
            String un=cleanUsername(username);if(user==null){sendAuthResult(false,action,null,"تعذر قراءة الحساب.");return;}if(name==null||name.trim().length()<2){sendAuthResult(false,action,null,"اسم المحقق غير صالح.");return;}if(!validUsername(un)){sendAuthResult(false,action,null,"اسم المستخدم غير صالح.");return;}
            claimProfileDocs(user,name,un).addOnSuccessListener(v->finishProfileAuth(user,name,un,action)).addOnFailureListener(e->{if(isUsernameConflict(e))sendAuthResult(false,action,null,"اسم المستخدم مستخدم بالفعل. اختر اسمًا آخر.");else sendAuthResult(false,action,null,"تعذر حفظ هوية المحقق في الخادم. تحقق من الاتصال وحاول مرة أخرى.");});
        }
        private void rollbackNewAccount(FirebaseUser u,String action,String message){
            if(u==null){sendAuthResult(false,action,null,message);return;}
            u.delete().addOnCompleteListener(x->{ensureFirebaseAuth();firebaseAuth.signOut();sendAuthResult(false,action,null,message);});
        }

        @JavascriptInterface public void createAccount(String name,String username,String email,String password){runOnUiThread(()->{ensureFirebaseAuth();firebaseAuth.createUserWithEmailAndPassword(email,password).addOnSuccessListener(r->{FirebaseUser u=r.getUser();if(u==null){sendAuthResult(false,"create",null,"تعذر إنشاء الحساب.");return;}String un=cleanUsername(username);if(name==null||name.trim().length()<2||!validUsername(un)){rollbackNewAccount(u,"create","بيانات هوية المحقق غير صالحة.");return;}claimProfileDocs(u,name,un).addOnSuccessListener(v->finishProfileAuth(u,name,un,"create")).addOnFailureListener(e->{if(isUsernameConflict(e))rollbackNewAccount(u,"create","اسم المستخدم مستخدم بالفعل. اختر اسمًا آخر.");else rollbackNewAccount(u,"create","تعذر حفظ هوية المحقق في الخادم. حاول مرة أخرى.");});}).addOnFailureListener(e->sendAuthResult(false,"create",null,e.getLocalizedMessage()));});}
        @JavascriptInterface public void signInEmail(String email,String password){runOnUiThread(()->{ensureFirebaseAuth();firebaseAuth.signInWithEmailAndPassword(email,password).addOnSuccessListener(r->sendProfileAuth("login",r.getUser(),false)).addOnFailureListener(e->sendAuthResult(false,"login",null,e.getLocalizedMessage()));});}
        @JavascriptInterface public void signInGoogle(){runOnUiThread(()->{ensureFirebaseAuth();ensureCredentialManager();GetGoogleIdOption option=new GetGoogleIdOption.Builder().setFilterByAuthorizedAccounts(false).setServerClientId(getString(R.string.default_web_client_id)).build();GetCredentialRequest req=new GetCredentialRequest.Builder().addCredentialOption(option).build();credentialManager.getCredentialAsync(MainActivity.this,req,new CancellationSignal(),getMainExecutor(),new CredentialManagerCallback<GetCredentialResponse,GetCredentialException>(){public void onResult(GetCredentialResponse result){if(!(result.getCredential() instanceof CustomCredential)){sendAuthResult(false,"google",null,"تعذر قراءة حساب Google.");return;}CustomCredential c=(CustomCredential)result.getCredential();try{GoogleIdTokenCredential gc=GoogleIdTokenCredential.createFrom(c.getData());AuthCredential fc=GoogleAuthProvider.getCredential(gc.getIdToken(),null);firebaseAuth.signInWithCredential(fc).addOnSuccessListener(a->sendProfileAuth("google",a.getUser(),false)).addOnFailureListener(e->sendAuthResult(false,"google",null,e.getLocalizedMessage()));}catch(Exception e){sendAuthResult(false,"google",null,e.getLocalizedMessage());}}public void onError(@NonNull GetCredentialException e){sendAuthResult(false,"google",null,e.getLocalizedMessage());}});});}
        @JavascriptInterface public void completeProfile(String name,String username){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){sendAuthResult(false,"profileSetup",null,"انتهت جلسة الدخول.");return;}reserveAndSaveProfile(u,name,username,"profileSetup");});}
        @JavascriptInterface public void syncLocalProfile(String name,String username){runOnUiThread(()->{FirebaseUser u=currentUser();String un=cleanUsername(username);if(u==null||name==null||name.trim().length()<2||!validUsername(un)){sendAuthResult(false,"sync",null,null);return;}claimProfileDocs(u,name,un).addOnSuccessListener(v->{normalizeVisibleDisplayName(u,name);sendAuthResult(true,"sync",u,null);}).addOnFailureListener(e->sendAuthResult(false,"sync",null,isUsernameConflict(e)?"USERNAME_CONFLICT":null));});}
        private boolean usesGoogle(FirebaseUser u){
            if(u==null)return false;
            for(com.google.firebase.auth.UserInfo i:u.getProviderData())if("google.com".equals(i.getProviderId()))return true;
            return false;
        }
        private void cleanupAndDeleteAccount(FirebaseUser u){
            if(u==null){sendAuthResult(false,"delete",null,"لا يوجد حساب مسجل.");return;}
            ensureFirestore();
            firestore.collection("users").document(u.getUid()).get().addOnCompleteListener(t->{
                String un="";if(t.isSuccessful()&&t.getResult()!=null&&t.getResult().exists())un=str(t.getResult(),"username","");
                final String username=un;
                u.delete().addOnSuccessListener(v->{
                    java.util.List<com.google.android.gms.tasks.Task<?>> cleanup=new java.util.ArrayList<>();
                    cleanup.add(firestore.collection("users").document(u.getUid()).delete());
                    if(!username.isEmpty())cleanup.add(firestore.collection("usernames").document(username).delete());
                    Tasks.whenAllComplete(cleanup).addOnCompleteListener(x->{ensureFirebaseAuth();firebaseAuth.signOut();sendAuthResult(true,"delete",null,null);});
                }).addOnFailureListener(e->sendAuthResult(false,"delete",null,e.getLocalizedMessage()));
            });
        }
        private void googleReauthAndDelete(FirebaseUser u){
            ensureCredentialManager();
            GetGoogleIdOption option=new GetGoogleIdOption.Builder().setFilterByAuthorizedAccounts(false).setServerClientId(getString(R.string.default_web_client_id)).build();
            GetCredentialRequest req=new GetCredentialRequest.Builder().addCredentialOption(option).build();
            credentialManager.getCredentialAsync(MainActivity.this,req,new CancellationSignal(),getMainExecutor(),new CredentialManagerCallback<GetCredentialResponse,GetCredentialException>(){
                public void onResult(GetCredentialResponse result){
                    if(!(result.getCredential() instanceof CustomCredential)){sendAuthResult(false,"delete",null,"تعذر إعادة التحقق من حساب Google.");return;}
                    try{CustomCredential c=(CustomCredential)result.getCredential();GoogleIdTokenCredential gc=GoogleIdTokenCredential.createFrom(c.getData());AuthCredential fc=GoogleAuthProvider.getCredential(gc.getIdToken(),null);u.reauthenticate(fc).addOnSuccessListener(v->cleanupAndDeleteAccount(u)).addOnFailureListener(e->sendAuthResult(false,"delete",null,e.getLocalizedMessage()));}
                    catch(Exception e){sendAuthResult(false,"delete",null,e.getLocalizedMessage());}
                }
                public void onError(@NonNull GetCredentialException e){sendAuthResult(false,"delete",null,e.getLocalizedMessage());}
            });
        }
        @JavascriptInterface public void deleteAccount(){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){sendAuthResult(false,"delete",null,"لا يوجد حساب مسجل.");return;}if(usesGoogle(u)){googleReauthAndDelete(u);return;}sendAuthResult(false,"delete",null,"REAUTH_PASSWORD");});}
        @JavascriptInterface public void reauthenticatePasswordAndDelete(String password){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){sendAuthResult(false,"delete",null,"لا يوجد حساب مسجل.");return;}String email=u.getEmail();if(email==null||email.isEmpty()){sendAuthResult(false,"delete",null,"تعذر قراءة بريد الحساب.");return;}if(password==null||password.isEmpty()){sendAuthResult(false,"delete",null,"أدخل كلمة المرور.");return;}AuthCredential c=com.google.firebase.auth.EmailAuthProvider.getCredential(email,password);u.reauthenticate(c).addOnSuccessListener(v->cleanupAndDeleteAccount(u)).addOnFailureListener(e->sendAuthResult(false,"delete",null,"كلمة المرور غير صحيحة أو تعذر إعادة التحقق."));});}
        @JavascriptInterface public void signOut(){runOnUiThread(()->{ensureFirebaseAuth();firebaseAuth.signOut();sendAuthResult(true,"logout",null,null);});}
        @JavascriptInterface public void restoreSession(){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){sendAuthResult(false,"restore",null,null);return;}sendProfileAuth("restore",u,false);});}
    }

    private com.google.firebase.firestore.ListenerRegistration rtRequests,rtFriends,rtNotes,rtMessages,rtTyping;
    private void realtimeEvent(String type,String uid,String name,boolean typing){
        try{JSONObject o=new JSONObject();o.put("type",type);if(uid!=null)o.put("uid",uid);if(name!=null)o.put("name",name);o.put("typing",typing);final String js="window.onNativeRealtimeEvent&&window.onNativeRealtimeEvent("+o+")";runOnUiThread(()->webView.evaluateJavascript(js,null));}catch(Exception ignored){}
    }
    private void stopRealtime(){if(rtRequests!=null)rtRequests.remove();if(rtFriends!=null)rtFriends.remove();if(rtNotes!=null)rtNotes.remove();if(rtMessages!=null)rtMessages.remove();if(rtTyping!=null)rtTyping.remove();rtRequests=rtFriends=rtNotes=rtMessages=rtTyping=null;}
    private void showNativeNotification(String title,String text){
        try{if(!getSharedPreferences("app_settings",MODE_PRIVATE).getBoolean("notifications_enabled",true))return;
            android.app.NotificationManager nm=(android.app.NotificationManager)getSystemService(android.content.Context.NOTIFICATION_SERVICE);
            String channel="social_updates";
            if(android.os.Build.VERSION.SDK_INT>=26)nm.createNotificationChannel(new android.app.NotificationChannel(channel,"تحديثات الأصدقاء",android.app.NotificationManager.IMPORTANCE_HIGH));
            if(android.os.Build.VERSION.SDK_INT>=33 && checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)!=android.content.pm.PackageManager.PERMISSION_GRANTED)return;
            android.app.Notification.Builder b=android.os.Build.VERSION.SDK_INT>=26?new android.app.Notification.Builder(this,channel):new android.app.Notification.Builder(this);
            b.setSmallIcon(android.R.drawable.ic_dialog_info).setContentTitle(title).setContentText(text).setAutoCancel(true);
            nm.notify((int)(System.currentTimeMillis()&0x7fffffff),b.build());
        }catch(Exception ignored){}
    }
    public class SocialBridge {
        @JavascriptInterface public void submitReport(String type,String text){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null||text==null||text.trim().isEmpty()){socialError("reportSubmitted",null);return;}ensureFirestore();Map<String,Object>d=new HashMap<>();d.put("uid",u.getUid());d.put("name",authVisibleName(u).isEmpty()?"محقق":authVisibleName(u));d.put("email",u.getEmail()==null?"":u.getEmail());d.put("type",type==null?"bug":type);d.put("text",text.trim());d.put("status","open");d.put("createdAt",FieldValue.serverTimestamp());firestore.collection("reports").add(d).addOnSuccessListener(r->{try{JSONObject o=new JSONObject();o.put("ok",true);o.put("action","reportSubmitted");sendSocial(o);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("reportSubmitted",e));});}
        @JavascriptInterface public void adminLoadDashboard(){runOnUiThread(()->{if(!currentUserIsAdmin()){socialError("adminDashboard",new Exception("غير مصرح"));return;}ensureFirestore();Task<QuerySnapshot> users=firestore.collection("users").limit(1000).get();Task<QuerySnapshot> matches=firestore.collection("puzzleMatches").limit(100).get();Task<QuerySnapshot> reports=firestore.collection("reports").whereEqualTo("status","open").limit(100).get();Task<DocumentSnapshot> config=firestore.collection("appConfig").document("currentCase").get();Tasks.whenAllSuccess(users,matches,reports,config).addOnSuccessListener(all->{try{QuerySnapshot uq=(QuerySnapshot)all.get(0),mq=(QuerySnapshot)all.get(1),rq=(QuerySnapshot)all.get(2);DocumentSnapshot cfg=(DocumentSnapshot)all.get(3);int active=0,waitingPlayers=0;for(DocumentSnapshot d:mq.getDocuments()){String st=str(d,"status","");List<String> mem=(List<String>)d.get("members");if("active".equals(st))active++;if("waiting".equals(st)&&mem!=null)waitingPlayers+=mem.size();}JSONObject o=new JSONObject();o.put("ok",true);o.put("action","adminDashboard");o.put("users",uq.size());o.put("activeMatches",active);o.put("waitingPlayers",waitingPlayers);o.put("openReports",rq.size());o.put("caseEnabled",!cfg.exists()||!Boolean.FALSE.equals(cfg.getBoolean("enabled")));sendSocial(o);}catch(Exception e){socialError("adminDashboard",e);}}).addOnFailureListener(e->socialError("adminDashboard",e));});}
        @JavascriptInterface public void adminLoadReports(){runOnUiThread(()->{if(!currentUserIsAdmin()){socialError("adminReports",null);return;}ensureFirestore();firestore.collection("reports").orderBy("createdAt",Query.Direction.DESCENDING).limit(80).get().addOnSuccessListener(q->{try{JSONArray a=new JSONArray();for(DocumentSnapshot d:q.getDocuments()){JSONObject x=new JSONObject();x.put("id",d.getId());x.put("uid",str(d,"uid",""));x.put("name",str(d,"name","محقق"));x.put("type",str(d,"type","bug"));x.put("text",str(d,"text",""));x.put("status",str(d,"status","open"));Timestamp t=d.getTimestamp("createdAt");if(t!=null)x.put("time",t.toDate().getTime());a.put(x);}JSONObject o=new JSONObject();o.put("ok",true);o.put("action","adminReports");o.put("reports",a);sendSocial(o);}catch(Exception e){socialError("adminReports",e);}}).addOnFailureListener(e->socialError("adminReports",e));});}
        @JavascriptInterface public void adminResolveReport(String id){runOnUiThread(()->{if(!currentUserIsAdmin()||id==null)return;ensureFirestore();firestore.collection("reports").document(id).update("status","resolved","resolvedAt",FieldValue.serverTimestamp()).addOnSuccessListener(v->{adminLog("resolve_report",id);adminLoadReports();adminLoadDashboard();});});}
        @JavascriptInterface public void adminSearchPlayer(String query){runOnUiThread(()->{if(!currentUserIsAdmin()){socialError("adminPlayer",null);return;}ensureFirestore();String q=query==null?"":query.trim().replaceFirst("^@","").toLowerCase(Locale.ROOT);if(q.isEmpty()){socialError("adminPlayer",null);return;}firestore.collection("usernames").document(q).get().addOnSuccessListener(idx->{String uid=idx.exists()?idx.getString("uid"):null;if(uid==null||uid.isEmpty()){firestore.collection("users").whereEqualTo("nameLower",q).limit(1).get().addOnSuccessListener(s->{if(s.isEmpty()){socialError("adminPlayer",new Exception("لم يتم العثور على اللاعب"));return;}adminEmitPlayer(s.getDocuments().get(0));});}else firestore.collection("users").document(uid).get().addOnSuccessListener(this::adminEmitPlayer);});});}
        private void adminEmitPlayer(DocumentSnapshot d){try{JSONObject p=new JSONObject();p.put("uid",d.getId());p.put("name",str(d,"name","محقق"));p.put("username",str(d,"username",""));p.put("rank",str(d,"rank","صانع الدور"));p.put("banned",Boolean.TRUE.equals(d.getBoolean("banned")));p.put("email",str(d,"email",""));JSONObject o=new JSONObject();o.put("ok",true);o.put("action","adminPlayer");o.put("player",p);sendSocial(o);}catch(Exception e){socialError("adminPlayer",e);}}
        @JavascriptInterface public void adminSetPlayerBan(String uid,boolean banned){runOnUiThread(()->{if(!currentUserIsAdmin()||uid==null||uid.isEmpty())return;ensureFirestore();com.google.firebase.firestore.DocumentReference r=firestore.collection("users").document(uid);r.get().addOnSuccessListener(d->{if("bajanznsb@gmail.com".equalsIgnoreCase(str(d,"email",""))){socialError("adminPlayerBan",new Exception("لا يمكن حظر حساب الإدارة"));return;}Map<String,Object>u=new HashMap<>();u.put("banned",banned);u.put("bannedAt",banned?FieldValue.serverTimestamp():null);r.set(u,com.google.firebase.firestore.SetOptions.merge()).addOnSuccessListener(v->{adminLog(banned?"ban_player":"unban_player",uid);try{JSONObject o=new JSONObject();o.put("ok",true);o.put("action","adminPlayerBan");o.put("uid",uid);o.put("banned",banned);sendSocial(o);}catch(Exception ignored){}});});});}
        @JavascriptInterface public void adminLoadMatches(){runOnUiThread(()->{if(!currentUserIsAdmin()){socialError("adminMatches",null);return;}ensureFirestore();firestore.collection("puzzleMatches").orderBy("createdAt",Query.Direction.DESCENDING).limit(50).get().addOnSuccessListener(q->{try{JSONArray a=new JSONArray();for(DocumentSnapshot d:q.getDocuments()){String st=str(d,"status","waiting");if(!"active".equals(st)&&!"waiting".equals(st))continue;JSONObject x=new JSONObject();x.put("id",d.getId());x.put("status",st);List<String>mem=(List<String>)d.get("members");x.put("count",mem==null?0:mem.size());Map<String,Object>names=(Map<String,Object>)d.get("names");Map<String,Object>stages=(Map<String,Object>)d.get("stageByUid");JSONArray pa=new JSONArray();if(mem!=null)for(String uid:mem){JSONObject p=new JSONObject();p.put("uid",uid);p.put("name",names!=null&&names.get(uid)!=null?String.valueOf(names.get(uid)):"محقق");p.put("stage",stages!=null&&stages.get(uid) instanceof Number?((Number)stages.get(uid)).intValue():1);pa.put(p);}x.put("players",pa);a.put(x);}JSONObject o=new JSONObject();o.put("ok",true);o.put("action","adminMatches");o.put("matches",a);sendSocial(o);}catch(Exception e){socialError("adminMatches",e);}}).addOnFailureListener(e->socialError("adminMatches",e));});}
        @JavascriptInterface public void adminLoadCaseConfig(){runOnUiThread(()->{if(!currentUserIsAdmin()){socialError("adminCase",null);return;}ensureFirestore();firestore.collection("appConfig").document("currentCase").get().addOnSuccessListener(d->{try{JSONObject o=new JSONObject();o.put("ok",true);o.put("action","adminCase");o.put("enabled",!d.exists()||!Boolean.FALSE.equals(d.getBoolean("enabled")));o.put("title",str(d,"title","القضية التجريبية الحالية"));sendSocial(o);}catch(Exception e){socialError("adminCase",e);}});});}
        @JavascriptInterface public void adminSetCaseEnabled(boolean enabled){runOnUiThread(()->{if(!currentUserIsAdmin())return;ensureFirestore();Map<String,Object>d=new HashMap<>();d.put("enabled",enabled);d.put("title","القضية التجريبية الحالية");d.put("updatedAt",FieldValue.serverTimestamp());firestore.collection("appConfig").document("currentCase").set(d,com.google.firebase.firestore.SetOptions.merge()).addOnSuccessListener(v->{adminLog(enabled?"enable_case":"disable_case","currentCase");adminLoadCaseConfig();adminLoadDashboard();});});}
        @JavascriptInterface public void adminLoadLogs(){runOnUiThread(()->{if(!currentUserIsAdmin()){socialError("adminLogs",null);return;}ensureFirestore();firestore.collection("adminLogs").orderBy("createdAt",Query.Direction.DESCENDING).limit(80).get().addOnSuccessListener(q->{try{JSONArray a=new JSONArray();for(DocumentSnapshot d:q.getDocuments()){JSONObject x=new JSONObject();x.put("action",str(d,"action",""));x.put("target",str(d,"target",""));Timestamp t=d.getTimestamp("createdAt");if(t!=null)x.put("time",t.toDate().getTime());a.put(x);}JSONObject o=new JSONObject();o.put("ok",true);o.put("action","adminLogs");o.put("logs",a);sendSocial(o);}catch(Exception e){socialError("adminLogs",e);}}).addOnFailureListener(e->socialError("adminLogs",e));});}

        @JavascriptInterface public void setNotificationsEnabled(boolean enabled){runOnUiThread(()->getSharedPreferences("app_settings",MODE_PRIVATE).edit().putBoolean("notifications_enabled",enabled).apply());}
        @JavascriptInterface public void loadBlockedUsers(){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("blockedList",null);return;}ensureFirestore();firestore.collection("users").document(u.getUid()).collection("blocks").get().addOnSuccessListener(q->{List<Task<DocumentSnapshot>> tasks=new ArrayList<>();List<String> ids=new ArrayList<>();for(DocumentSnapshot d:q.getDocuments()){ids.add(d.getId());tasks.add(firestore.collection("users").document(d.getId()).get());}if(tasks.isEmpty()){try{JSONObject out=new JSONObject();out.put("ok",true);out.put("action","blockedList");out.put("players",new JSONArray());sendSocial(out);}catch(Exception ignored){}return;}Tasks.whenAllSuccess(tasks).addOnSuccessListener(all->{try{JSONArray arr=new JSONArray();for(int i=0;i<all.size();i++){DocumentSnapshot d=(DocumentSnapshot)all.get(i);JSONObject p=new JSONObject();p.put("uid",ids.get(i));p.put("name",str(d,"name","محقق"));p.put("username",str(d,"username",""));arr.put(p);}JSONObject out=new JSONObject();out.put("ok",true);out.put("action","blockedList");out.put("players",arr);sendSocial(out);}catch(Exception e){socialError("blockedList",e);}});}).addOnFailureListener(e->socialError("blockedList",e));});}
        @JavascriptInterface public void unblockUser(String uid){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("unblocked",null);return;}ensureFirestore();firestore.collection("users").document(u.getUid()).collection("blocks").document(uid).delete().addOnSuccessListener(v->{try{JSONObject out=new JSONObject();out.put("ok",true);out.put("action","unblocked");out.put("uid",uid);sendSocial(out);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("unblocked",e));});}

        @JavascriptInterface public void startRealtime(){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();stopRealtime();
            rtRequests=firestore.collection("friendRequests").whereEqualTo("toUid",u.getUid()).whereEqualTo("status","pending").addSnapshotListener((x,e)->{if(e==null)realtimeEvent("socialChanged",null,null,false);});
            rtFriends=firestore.collection("users").document(u.getUid()).collection("friends").addSnapshotListener((x,e)->{if(e==null)realtimeEvent("socialChanged",null,null,false);});
            rtNotes=firestore.collection("users").document(u.getUid()).collection("notifications").addSnapshotListener((x,e)->{if(e==null&&x!=null){for(com.google.firebase.firestore.DocumentChange change:x.getDocumentChanges()){if(change.getType()!=com.google.firebase.firestore.DocumentChange.Type.ADDED)continue;DocumentSnapshot d=change.getDocument();if(Boolean.TRUE.equals(d.getBoolean("read")))continue;String type=str(d,"type","");if("friend_accepted".equals(type)){realtimeEvent("friendAccepted",str(d,"fromUid",""),str(d,"fromName","لاعب"),false);}d.getReference().update("read",true);}}});
        });}
        @JavascriptInterface public void stopRealtimeSocial(){runOnUiThread(()->stopRealtime());}
        @JavascriptInterface public void setTyping(String uid,boolean typing){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();String id=chatId(u.getUid(),uid);Map<String,Object> m=new HashMap<>();m.put("uid",u.getUid());m.put("name",authVisibleName(u).isEmpty()?"المحقق":authVisibleName(u));m.put("typing",typing);m.put("updatedAt",FieldValue.serverTimestamp());firestore.collection("chats").document(id).collection("typing").document(u.getUid()).set(m);});}

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
                        DocumentSnapshot pd=(DocumentSnapshot)all.get(0);JSONObject po=new JSONObject();po.put("name",str(pd,"name",authVisibleName(u).isEmpty()?"المحقق":authVisibleName(u)));po.put("username",str(pd,"username",""));po.put("rank",str(pd,"rank","صانع الدور"));po.put("level",number(pd,"level",1));po.put("cases",number(pd,"cases",0));po.put("solved",number(pd,"solved",0));po.put("accuracy",number(pd,"accuracy",0));po.put("xpPercent",number(pd,"xpPercent",8));out.put("profile",po);
                        JSONArray fa=new JSONArray();for(DocumentSnapshot d:((QuerySnapshot)all.get(1)).getDocuments()){JSONObject x=new JSONObject();x.put("uid",d.getId());x.put("name",str(d,"name","محقق"));x.put("rank",str(d,"rank","صانع الدور"));x.put("equipped",str(d,"equippedCosmetics","{}"));fa.put(x);}out.put("friends",fa);
                        JSONArray ra=new JSONArray();for(DocumentSnapshot d:((QuerySnapshot)all.get(2)).getDocuments()){JSONObject x=new JSONObject();x.put("uid",str(d,"fromUid",""));x.put("name",str(d,"fromName","محقق"));ra.put(x);}out.put("requests",ra);
                        JSONArray na=new JSONArray();for(DocumentSnapshot d:((QuerySnapshot)all.get(3)).getDocuments()){JSONObject x=new JSONObject();x.put("id",d.getId());x.put("read",Boolean.TRUE.equals(d.getBoolean("read")));x.put("type",str(d,"type",""));na.put(x);}out.put("notifications",na);
                        JSONArray ca=new JSONArray();for(DocumentSnapshot d:((QuerySnapshot)all.get(4)).getDocuments()){List<String> mem=(List<String>)d.get("members");if(mem==null)continue;String peer="";for(String id:mem)if(!id.equals(u.getUid()))peer=id;Map<String,Object> names=(Map<String,Object>)d.get("names");String peerName=names!=null&&names.get(peer)!=null?String.valueOf(names.get(peer)):"محقق";JSONObject x=new JSONObject();x.put("uid",peer);x.put("name",peerName);x.put("lastMessage",str(d,"lastMessage",""));ca.put(x);}out.put("chats",ca);sendSocial(out);
                    }catch(Exception e){socialError("load",e);}
                }).addOnFailureListener(e->socialError("load",e));
            });
        }

        @JavascriptInterface public void loadPublicProfile(String uid){runOnUiThread(()->{FirebaseUser me=currentUser();if(me==null)return;ensureFirestore();firestore.collection("users").document(uid).get().addOnSuccessListener(d->{try{JSONObject o=new JSONObject();o.put("ok",true);o.put("action","publicProfile");o.put("player",roleplayPlayer(d));sendSocial(o);}catch(Exception e){socialError("publicProfile",e);}});});}
        @JavascriptInterface public void saveCosmetics(String inventory,String equipped){runOnUiThread(()->{FirebaseUser me=currentUser();if(me==null)return;ensureFirestore();Map<String,Object> mine=new HashMap<>();mine.put("inventoryCosmetics",inventory);mine.put("equippedCosmetics",equipped);firestore.collection("users").document(me.getUid()).set(mine,com.google.firebase.firestore.SetOptions.merge()).addOnSuccessListener(v->firestore.collection("users").document(me.getUid()).collection("friends").get().addOnSuccessListener(fs->{WriteBatch batch=firestore.batch();for(DocumentSnapshot f:fs.getDocuments()){Map<String,Object> mirror=new HashMap<>();mirror.put("equippedCosmetics",equipped);batch.set(firestore.collection("users").document(f.getId()).collection("friends").document(me.getUid()),mirror,com.google.firebase.firestore.SetOptions.merge());}batch.commit();}));});}
        @JavascriptInterface public void loadCosmetics(){runOnUiThread(()->{FirebaseUser me=currentUser();if(me==null)return;ensureFirestore();firestore.collection("users").document(me.getUid()).get().addOnSuccessListener(d->{try{JSONObject o=new JSONObject();o.put("ok",true);o.put("action","cosmetics");o.put("inventory",str(d,"inventoryCosmetics",""));o.put("equipped",str(d,"equippedCosmetics",""));sendSocial(o);}catch(Exception ignored){}});});}

        @JavascriptInterface public void sendFriendPush(String baseUrl,String toUid){runOnUiThread(()->{FirebaseUser me=currentUser();if(me==null||baseUrl==null||!baseUrl.startsWith("https://"))return;me.getIdToken(false).addOnSuccessListener(tok->new Thread(()->{try{java.net.URL url=new java.net.URL(baseUrl.replaceAll("/+$","")+"/api/social/friend-push");java.net.HttpURLConnection c=(java.net.HttpURLConnection)url.openConnection();c.setRequestMethod("POST");c.setConnectTimeout(7000);c.setReadTimeout(7000);c.setDoOutput(true);c.setRequestProperty("Content-Type","application/json");c.setRequestProperty("Authorization","Bearer "+tok.getToken());String body=new JSONObject().put("toUid",toUid).toString();try(java.io.OutputStream os=c.getOutputStream()){os.write(body.getBytes(java.nio.charset.StandardCharsets.UTF_8));}c.getResponseCode();c.disconnect();}catch(Exception ignored){}}).start());});}
        @JavascriptInterface public void sendFriendAcceptedPush(String baseUrl,String toUid){runOnUiThread(()->{FirebaseUser me=currentUser();if(me==null||baseUrl==null||!baseUrl.startsWith("https://"))return;me.getIdToken(false).addOnSuccessListener(tok->new Thread(()->{try{java.net.URL url=new java.net.URL(baseUrl.replaceAll("/+$","")+"/api/social/friend-accepted-push");java.net.HttpURLConnection conn=(java.net.HttpURLConnection)url.openConnection();conn.setRequestMethod("POST");conn.setConnectTimeout(7000);conn.setReadTimeout(7000);conn.setDoOutput(true);conn.setRequestProperty("Content-Type","application/json");conn.setRequestProperty("Authorization","Bearer "+tok.getToken());String body=new JSONObject().put("toUid",toUid).toString();try(java.io.OutputStream os=conn.getOutputStream()){os.write(body.getBytes(java.nio.charset.StandardCharsets.UTF_8));}conn.getResponseCode();conn.disconnect();}catch(Exception ignored){}}).start());});}


        @JavascriptInterface public void searchPlayer(String query) {
            runOnUiThread(()->{FirebaseUser me=currentUser();if(me==null){socialError("search",null);return;}ensureFirestore();String q=query.trim().replaceFirst("^@","").toLowerCase(Locale.ROOT);if(q.isEmpty()){socialError("search",null);return;}
                firestore.collection("usernames").document(q).get().addOnSuccessListener(idx->{String uid=idx.exists()?idx.getString("uid"):null;if(uid!=null&&!uid.isEmpty()){firestore.collection("users").document(uid).get().addOnSuccessListener(d->{if(d.exists())sendSearchDoc(me,d,q);else fallbackSearchByFields(me,q);}).addOnFailureListener(e->fallbackSearchByFields(me,q));}else fallbackSearchByFields(me,q);}).addOnFailureListener(e->fallbackSearchByFields(me,q));
            });
        }
        private void fallbackSearchByFields(FirebaseUser me,String q){firestore.collection("users").whereEqualTo("usernameLower",q).limit(1).get().addOnSuccessListener(byUser->{if(!byUser.isEmpty()){sendSearchResult(me,byUser,q);return;}firestore.collection("users").whereEqualTo("nameLower",q).limit(10).get().addOnSuccessListener(byName->sendSearchResult(me,byName,q)).addOnFailureListener(e->socialError("search",e));}).addOnFailureListener(e->socialError("search",e));}
        private JSONObject roleplayPlayer(DocumentSnapshot d)throws Exception{JSONObject p=new JSONObject();p.put("uid",d.getId());p.put("name",str(d,"name","لاعب"));p.put("username",str(d,"username",""));p.put("rank",str(d,"rank","صانع الدور"));p.put("level",number(d,"level",1));p.put("cases",number(d,"cases",0));p.put("solved",number(d,"solved",0));p.put("accuracy",number(d,"accuracy",0));p.put("xpPercent",number(d,"xpPercent",8));p.put("equipped",str(d,"equippedCosmetics","{}"));return p;}
        private void sendSearchDoc(FirebaseUser me,DocumentSnapshot d,String q){Task<DocumentSnapshot> f=firestore.collection("users").document(me.getUid()).collection("friends").document(d.getId()).get();Task<DocumentSnapshot> r=firestore.collection("friendRequests").document(requestId(me.getUid(),d.getId())).get();Tasks.whenAllSuccess(f,r).addOnSuccessListener(x->{try{JSONObject out=new JSONObject();out.put("ok",true);out.put("action","search");out.put("query",q);JSONObject p=roleplayPlayer(d);p.put("self",d.getId().equals(me.getUid()));p.put("friend",((DocumentSnapshot)x.get(0)).exists());DocumentSnapshot requestDoc=(DocumentSnapshot)x.get(1);p.put("requested",requestDoc.exists()&&"pending".equals(str(requestDoc,"status","")));out.put("player",p);sendSocial(out);}catch(Exception e){socialError("search",e);}});}
        private void sendSearchResult(FirebaseUser me,QuerySnapshot snap,String q){if(!snap.isEmpty())sendSearchDoc(me,snap.getDocuments().get(0),q);else try{JSONObject o=new JSONObject();o.put("ok",true);o.put("action","search");sendSocial(o);}catch(Exception ignored){}}

        @JavascriptInterface public void sendFriendRequest(String toUid) {
            runOnUiThread(() -> { FirebaseUser u=currentUser();if(u==null||u.getUid().equals(toUid)){socialError("friendSent",null);return;}ensureFirestore();
                Task<DocumentSnapshot> friend=firestore.collection("users").document(u.getUid()).collection("friends").document(toUid).get();
                Task<DocumentSnapshot> blocked=firestore.collection("users").document(toUid).collection("blocks").document(u.getUid()).get();
                Task<DocumentSnapshot> blockedByMe=firestore.collection("users").document(u.getUid()).collection("blocks").document(toUid).get();
                Tasks.whenAllSuccess(friend,blocked,blockedByMe).addOnSuccessListener(all->{if(((DocumentSnapshot)all.get(0)).exists()){socialError("friendSent",new Exception("هذا اللاعب ضمن أصدقائك بالفعل."));return;}if(((DocumentSnapshot)all.get(1)).exists()||((DocumentSnapshot)all.get(2)).exists()){socialError("friendSent",new Exception("لا يمكن إرسال طلب لهذا اللاعب."));return;}
                    String id=requestId(u.getUid(),toUid);Map<String,Object> r=new HashMap<>();r.put("fromUid",u.getUid());r.put("fromName",authVisibleName(u).isEmpty()?"محقق":authVisibleName(u));r.put("toUid",toUid);r.put("status","pending");r.put("createdAt",FieldValue.serverTimestamp());
                    firestore.collection("friendRequests").document(id).set(r).addOnSuccessListener(v->{Map<String,Object> n=new HashMap<>();n.put("type","friend_request");n.put("fromUid",u.getUid());n.put("fromName",authVisibleName(u).isEmpty()?"محقق":authVisibleName(u));n.put("read",false);n.put("createdAt",FieldValue.serverTimestamp());firestore.collection("users").document(toUid).collection("notifications").add(n);try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","friendSent");sendSocial(p);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("friendSent",e));
                }).addOnFailureListener(e->socialError("friendSent",e)); });
        }

        @JavascriptInterface public void acceptFriendRequest(String fromUid) {
            runOnUiThread(() -> { FirebaseUser u=currentUser();if(u==null){socialError("friendAccepted",null);return;}ensureFirestore();String rid=requestId(fromUid,u.getUid());firestore.collection("friendRequests").document(rid).get().addOnSuccessListener(req->{if(!req.exists()||!"pending".equals(req.getString("status"))){socialError("friendAccepted",new Exception("الطلب لم يعد متاحًا."));return;}String fromName=str(req,"fromName","محقق");String myName=authVisibleName(u).isEmpty()?"محقق":authVisibleName(u);WriteBatch b=firestore.batch();Map<String,Object>a=new HashMap<>();a.put("name",fromName);a.put("rank","محقق");a.put("since",FieldValue.serverTimestamp());Map<String,Object>me=new HashMap<>();me.put("name",myName);me.put("rank","محقق");me.put("since",FieldValue.serverTimestamp());b.set(firestore.collection("users").document(u.getUid()).collection("friends").document(fromUid),a);b.set(firestore.collection("users").document(fromUid).collection("friends").document(u.getUid()),me);b.update(req.getReference(),"status","accepted","updatedAt",FieldValue.serverTimestamp());Map<String,Object>n=new HashMap<>();n.put("type","friend_accepted");n.put("fromUid",u.getUid());n.put("fromName",myName);n.put("read",false);n.put("createdAt",FieldValue.serverTimestamp());b.set(firestore.collection("users").document(fromUid).collection("notifications").document(),n);b.commit().addOnSuccessListener(v->{try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","friendAccepted");p.put("uid",fromUid);sendSocial(p);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("friendAccepted",e));}).addOnFailureListener(e->socialError("friendAccepted",e)); });
        }

        @JavascriptInterface public void rejectFriendRequest(String fromUid) { runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("friendRejected",null);return;}ensureFirestore();firestore.collection("friendRequests").document(requestId(fromUid,u.getUid())).update("status","rejected","updatedAt",FieldValue.serverTimestamp()).addOnSuccessListener(v->{try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","friendRejected");sendSocial(p);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("friendRejected",e));}); }
        @JavascriptInterface public void removeFriend(String uid) { runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("removed",null);return;}ensureFirestore();WriteBatch b=firestore.batch();b.delete(firestore.collection("users").document(u.getUid()).collection("friends").document(uid));b.delete(firestore.collection("users").document(uid).collection("friends").document(u.getUid()));b.commit().addOnSuccessListener(v->{try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","removed");sendSocial(p);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("removed",e));}); }
        @JavascriptInterface public void blockUser(String uid) { runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("blocked",null);return;}ensureFirestore();WriteBatch b=firestore.batch();Map<String,Object>x=new HashMap<>();x.put("createdAt",FieldValue.serverTimestamp());b.set(firestore.collection("users").document(u.getUid()).collection("blocks").document(uid),x);b.delete(firestore.collection("users").document(u.getUid()).collection("friends").document(uid));b.delete(firestore.collection("users").document(uid).collection("friends").document(u.getUid()));b.commit().addOnSuccessListener(v->{try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","blocked");sendSocial(p);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("blocked",e));}); }

        @JavascriptInterface public void watchChat(String peerUid){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();String cid=chatId(u.getUid(),peerUid);if(rtMessages!=null)rtMessages.remove();if(rtTyping!=null)rtTyping.remove();rtMessages=firestore.collection("chats").document(cid).collection("messages").orderBy("createdAt",Query.Direction.ASCENDING).limitToLast(100).addSnapshotListener((snap,err)->{if(err!=null||snap==null)return;try{WriteBatch reads=firestore.batch();boolean hasReads=false;JSONArray arr=new JSONArray();for(DocumentSnapshot d:snap.getDocuments()){boolean mine=u.getUid().equals(d.getString("senderId"));boolean read=Boolean.TRUE.equals(d.getBoolean("read"));if(!mine&&!read){reads.update(d.getReference(),"read",true,"readAt",FieldValue.serverTimestamp());hasReads=true;}JSONObject m=new JSONObject();m.put("id",d.getId());m.put("text",str(d,"text",""));m.put("mine",mine);m.put("read",read||!mine);m.put("time",clock(d.get("createdAt")));arr.put(m);}if(hasReads)reads.commit();JSONObject out=new JSONObject();out.put("ok",true);out.put("action","messages");out.put("messages",arr);sendSocial(out);}catch(Exception ignored){}});rtTyping=firestore.collection("chats").document(cid).collection("typing").document(peerUid).addSnapshotListener((d,e)->{if(e==null&&d!=null&&d.exists()){boolean typing=Boolean.TRUE.equals(d.getBoolean("typing"));realtimeEvent("typing",peerUid,str(d,"name","لاعب"),typing);}});});}
        @JavascriptInterface public void stopChatWatch(){runOnUiThread(()->{if(rtMessages!=null)rtMessages.remove();if(rtTyping!=null)rtTyping.remove();rtMessages=null;rtTyping=null;});}
        @JavascriptInterface public void loadMessages(String peerUid) { runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("messages",null);return;}ensureFirestore();String cid=chatId(u.getUid(),peerUid);firestore.collection("chats").document(cid).collection("messages").orderBy("createdAt", Query.Direction.ASCENDING).limitToLast(100).get().addOnSuccessListener(snap->{try{WriteBatch readBatch=firestore.batch();boolean hasReads=false;JSONArray arr=new JSONArray();for(DocumentSnapshot d:snap.getDocuments()){boolean mine=u.getUid().equals(d.getString("senderId"));boolean read=Boolean.TRUE.equals(d.getBoolean("read"));if(!mine&&!read){readBatch.update(d.getReference(),"read",true,"readAt",FieldValue.serverTimestamp());hasReads=true;}JSONObject m=new JSONObject();m.put("text",str(d,"text",""));m.put("mine",mine);m.put("read",read||!mine);m.put("time",clock(d.get("createdAt")));arr.put(m);}if(hasReads)readBatch.commit();JSONObject out=new JSONObject();out.put("ok",true);out.put("action","messages");out.put("messages",arr);sendSocial(out);}catch(Exception e){socialError("messages",e);}}).addOnFailureListener(e->socialError("messages",e));}); }
        @JavascriptInterface public void sendMessage(String peerUid,String text) { runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("messageSent",null);return;}String clean=text==null?"":text.trim();if(clean.isEmpty()||clean.length()>1000){socialError("messageSent",new Exception("الرسالة غير صالحة."));return;}ensureFirestore();firestore.collection("users").document(u.getUid()).collection("friends").document(peerUid).get().addOnSuccessListener(f->{if(!f.exists()){socialError("messageSent",new Exception("المراسلة متاحة للأصدقاء فقط."));return;}String cid=chatId(u.getUid(),peerUid);String myName=authVisibleName(u).isEmpty()?"محقق":authVisibleName(u);String peerName=str(f,"name","محقق");Map<String,Object>chat=new HashMap<>();chat.put("members",Arrays.asList(u.getUid(),peerUid));Map<String,Object>names=new HashMap<>();names.put(u.getUid(),myName);names.put(peerUid,peerName);chat.put("names",names);chat.put("lastMessage",clean);chat.put("updatedAt",FieldValue.serverTimestamp());Map<String,Object>msg=new HashMap<>();msg.put("senderId",u.getUid());msg.put("text",clean);msg.put("read",false);msg.put("createdAt",FieldValue.serverTimestamp());WriteBatch b=firestore.batch();b.set(firestore.collection("chats").document(cid),chat,com.google.firebase.firestore.SetOptions.merge());b.set(firestore.collection("chats").document(cid).collection("messages").document(),msg);b.commit().addOnSuccessListener(v->{try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","messageSent");sendSocial(p);}catch(Exception ignored){}}).addOnFailureListener(e->socialError("messageSent",e));}).addOnFailureListener(e->socialError("messageSent",e));}); }
    }

    @Override protected void onPause(){if(webView!=null)notifyJs("onNativeAppPause");super.onPause();}
    @Override protected void onResume(){super.onResume(); resumePendingUpdate();if(webView!=null)notifyJs("onNativeAppResume");}
    @Override protected void onActivityResult(int requestCode,int resultCode,Intent data){super.onActivityResult(requestCode,resultCode,data);if(requestCode==FILE_CHOOSER_REQUEST&&filePathCallback!=null){Uri[]results=WebChromeClient.FileChooserParams.parseResult(resultCode,data);filePathCallback.onReceiveValue(results);filePathCallback=null;}}
    @Override public void onBackPressed(){if(webView!=null&&webView.canGoBack())webView.goBack();else super.onBackPressed();}

    public class PuzzleBridge {
        private com.google.firebase.firestore.ListenerRegistration puzzleRoomListener;
        private com.google.firebase.firestore.ListenerRegistration puzzleChatListener;
        private String puzzleMatchId = "";
        private int puzzleStage = 1;

        private void emitPuzzle(JSONObject payload) {
            runOnUiThread(() -> webView.evaluateJavascript("window.onNativePuzzleEvent&&window.onNativePuzzleEvent(" + payload + ")", null));
        }
        private void puzzleFail(String action, String message) {
            try { JSONObject p=new JSONObject();p.put("ok",false);p.put("action",action);p.put("message",message==null?"تعذر إكمال العملية.":message);emitPuzzle(p); } catch(Exception ignored){}
        }
        private String clean(String s){return s==null?"":s.trim().toLowerCase(Locale.ROOT).replace("أ","ا").replace("إ","ا").replace("آ","ا").replace("ة","ه");}
        private String solutionFor(int stage){String[] a={"مفتاح","ساعة","مظلة","تذكرة","قمر","كتاب"};return stage>=1&&stage<=6?a[stage-1]:"";}
        private String answerQuestion(int stage,String raw){
            String q=clean(raw); if(q.isEmpty())return "غير ضروري";
            String[][] yes={
                {"مفتاح","معدن","معدني","باب","قفل","يفتح","صغير"},
                {"ساعه","وقت","زمن","عقارب","دائري","جدار"},
                {"مظله","مطر","يحمي","مقبض","تفتح","فوق الراس"},
                {"تذكره","سفر","ركوب","محطه","ورق","قطار","حافله"},
                {"قمر","ليل","سماء","فضاء","مضيء","هلال"},
                {"كتاب","قراءه","صفحات","ورق","مجلد","مكتبه"}
            };
            for(String x:yes[stage-1])if(q.contains(clean(x)))return "نعم";
            for(int i=1;i<=6;i++)if(i!=stage&&q.contains(clean(solutionFor(i))))return "لا";
            String[] negatives={"سياره","هاتف","جوال","كرسي","شجره","حيوان","انسان","طعام","سلاح","كمبيوتر","بحر"};
            for(String x:negatives)if(q.contains(clean(x)))return "لا";
            return "غير ضروري";
        }
        private String playerName(FirebaseUser u){String n=u.getDisplayName();return n==null||n.trim().isEmpty()?"محقق":n.trim();}
        private void stopPuzzleWatchInternal(){if(puzzleRoomListener!=null){puzzleRoomListener.remove();puzzleRoomListener=null;}if(puzzleChatListener!=null){puzzleChatListener.remove();puzzleChatListener=null;}}

        @JavascriptInterface public void matchmake(){
            runOnUiThread(() -> { FirebaseUser u=currentUser();if(u==null){puzzleFail("match","سجّل الدخول أولًا.");return;}ensureFirestore();
                final com.google.firebase.firestore.DocumentReference queue=firestore.collection("puzzleSystem").document("queue7");
                final String candidate=java.util.UUID.randomUUID().toString();
                firestore.runTransaction(tx->{
                    DocumentSnapshot q=tx.get(queue);String mid=q.exists()?str(q,"waitingMatchId",""):"";com.google.firebase.firestore.DocumentReference match;
                    if(mid.isEmpty()){mid=candidate;match=firestore.collection("puzzleMatches").document(mid);Map<String,Object>d=new HashMap<>();d.put("status","waiting");d.put("members",new ArrayList<>(Arrays.asList(u.getUid())));Map<String,Object>names=new HashMap<>();names.put(u.getUid(),playerName(u));d.put("names",names);Map<String,Object>st=new HashMap<>();st.put(u.getUid(),1);d.put("stageByUid",st);d.put("createdAt",FieldValue.serverTimestamp());tx.set(match,d);Map<String,Object>qd=new HashMap<>();qd.put("waitingMatchId",mid);qd.put("updatedAt",FieldValue.serverTimestamp());tx.set(queue,qd);return mid;}
                    match=firestore.collection("puzzleMatches").document(mid);DocumentSnapshot m=tx.get(match);if(!m.exists()||!"waiting".equals(str(m,"status","waiting"))){mid=candidate;match=firestore.collection("puzzleMatches").document(mid);Map<String,Object>d=new HashMap<>();d.put("status","waiting");d.put("members",new ArrayList<>(Arrays.asList(u.getUid())));Map<String,Object>names=new HashMap<>();names.put(u.getUid(),playerName(u));d.put("names",names);Map<String,Object>st=new HashMap<>();st.put(u.getUid(),1);d.put("stageByUid",st);d.put("createdAt",FieldValue.serverTimestamp());tx.set(match,d);Map<String,Object>qd=new HashMap<>();qd.put("waitingMatchId",mid);qd.put("updatedAt",FieldValue.serverTimestamp());tx.set(queue,qd);return mid;}
                    List<String> members=(List<String>)m.get("members");members=members==null?new ArrayList<>():new ArrayList<>(members);if(!members.contains(u.getUid()))members.add(u.getUid());Map<String,Object>names=(Map<String,Object>)m.get("names");names=names==null?new HashMap<>():new HashMap<>(names);names.put(u.getUid(),playerName(u));Map<String,Object>stages=(Map<String,Object>)m.get("stageByUid");stages=stages==null?new HashMap<>():new HashMap<>(stages);stages.put(u.getUid(),1);Map<String,Object>up=new HashMap<>();up.put("members",members);up.put("names",names);up.put("stageByUid",stages);
                    if(members.size()>=7){up.put("status","active");up.put("startedAt",FieldValue.serverTimestamp());tx.update(queue,"waitingMatchId","");}tx.update(match,up);return mid;
                }).addOnSuccessListener(mid->watchPuzzle(String.valueOf(mid))).addOnFailureListener(e->puzzleFail("match",e.getLocalizedMessage()));
            });
        }
        @JavascriptInterface public void watchPuzzle(String matchId){
            runOnUiThread(() -> {FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();stopPuzzleWatchInternal();puzzleMatchId=matchId;com.google.firebase.firestore.DocumentReference ref=firestore.collection("puzzleMatches").document(matchId);
                puzzleRoomListener=ref.addSnapshotListener((s,e)->{if(e!=null){puzzleFail("watch",e.getLocalizedMessage());return;}if(s==null||!s.exists())return;try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","state");p.put("matchId",matchId);p.put("status",str(s,"status","waiting"));List<String>mem=(List<String>)s.get("members");JSONArray ma=new JSONArray();if(mem!=null)for(String id:mem)ma.put(id);p.put("members",ma);Map<String,Object>names=(Map<String,Object>)s.get("names");JSONObject no=new JSONObject();if(names!=null)for(Map.Entry<String,Object>x:names.entrySet())no.put(x.getKey(),String.valueOf(x.getValue()));p.put("names",no);Map<String,Object>st=(Map<String,Object>)s.get("stageByUid");int stage=1;if(st!=null&&st.get(u.getUid()) instanceof Number)stage=((Number)st.get(u.getUid())).intValue();p.put("stage",stage);JSONObject so=new JSONObject();if(st!=null)for(Map.Entry<String,Object>x:st.entrySet())so.put(x.getKey(),x.getValue());p.put("stages",so);emitPuzzle(p);if(stage!=puzzleStage){puzzleStage=stage;watchPuzzleChat(matchId,stage);}else if(puzzleChatListener==null)watchPuzzleChat(matchId,stage);}catch(Exception ex){puzzleFail("watch",ex.getLocalizedMessage());}});
            });
        }
        private void watchPuzzleChat(String matchId,int stage){if(puzzleChatListener!=null){puzzleChatListener.remove();puzzleChatListener=null;}if(stage>6)return;com.google.firebase.firestore.CollectionReference c=firestore.collection("puzzleMatches").document(matchId).collection("stage"+stage+"Chat");puzzleChatListener=c.limit(100).addSnapshotListener((q,e)->{if(e!=null)return;try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","chat");p.put("stage",stage);JSONArray a=new JSONArray();if(q!=null)for(DocumentSnapshot d:q.getDocuments()){JSONObject m=new JSONObject();m.put("id",d.getId());m.put("uid",str(d,"uid",""));m.put("name",str(d,"name","محقق"));m.put("text",str(d,"text",""));Timestamp t=d.getTimestamp("createdAt");if(t!=null)m.put("time",t.toDate().getTime());a.put(m);}p.put("messages",a);emitPuzzle(p);}catch(Exception ignored){}});}
        @JavascriptInterface public void ask(String matchId,int stage,String question){runOnUiThread(()->{try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","answer");p.put("stage",stage);p.put("question",question==null?"":question.trim());p.put("answer",answerQuestion(stage,question));emitPuzzle(p);}catch(Exception ignored){}});}
        @JavascriptInterface public void sendStageChat(String matchId,int stage,String text){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null||text==null||text.trim().isEmpty()||stage<1||stage>6)return;ensureFirestore();com.google.firebase.firestore.DocumentReference ref=firestore.collection("puzzleMatches").document(matchId);ref.get().addOnSuccessListener(s->{Map<String,Object>st=(Map<String,Object>)s.get("stageByUid");if(st==null||!(st.get(u.getUid()) instanceof Number)||((Number)st.get(u.getUid())).intValue()!=stage)return;Map<String,Object>d=new HashMap<>();d.put("uid",u.getUid());d.put("name",playerName(u));d.put("text",text.trim());d.put("createdAt",FieldValue.serverTimestamp());ref.collection("stage"+stage+"Chat").add(d);});});}
        @JavascriptInterface public void submitSolution(String matchId,int stage,String raw){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null)return;ensureFirestore();String guess=clean(raw),answer=clean(solutionFor(stage));if(!guess.equals(answer)){try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","solution");p.put("correct",false);p.put("stage",stage);emitPuzzle(p);}catch(Exception ignored){}return;}com.google.firebase.firestore.DocumentReference ref=firestore.collection("puzzleMatches").document(matchId);firestore.runTransaction(tx->{DocumentSnapshot s=tx.get(ref);Map<String,Object>st=(Map<String,Object>)s.get("stageByUid");st=st==null?new HashMap<>():new HashMap<>(st);Object cur=st.get(u.getUid());int now=cur instanceof Number?((Number)cur).intValue():1;if(now!=stage)return now;st.put(u.getUid(),stage+1);Map<String,Object>up=new HashMap<>();up.put("stageByUid",st);if(stage==6){Map<String,Object>finished=(Map<String,Object>)s.get("finishedAtByUid");finished=finished==null?new HashMap<>():new HashMap<>(finished);finished.put(u.getUid(),new Date().getTime());up.put("finishedAtByUid",finished);}tx.update(ref,up);return stage+1;}).addOnSuccessListener(next->{try{JSONObject p=new JSONObject();p.put("ok",true);p.put("action","solution");p.put("correct",true);p.put("stage",stage);p.put("nextStage",next);emitPuzzle(p);}catch(Exception ignored){}}).addOnFailureListener(e->puzzleFail("solution",e.getLocalizedMessage()));});}
        @JavascriptInterface public void cancelMatch(String matchId){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null||matchId==null||matchId.isEmpty()){stopPuzzleWatchInternal();return;}ensureFirestore();com.google.firebase.firestore.DocumentReference ref=firestore.collection("puzzleMatches").document(matchId);firestore.runTransaction(tx->{DocumentSnapshot s=tx.get(ref);if(!s.exists()||!"waiting".equals(str(s,"status","waiting")))return null;List<String>mem=(List<String>)s.get("members");mem=mem==null?new ArrayList<>():new ArrayList<>(mem);mem.remove(u.getUid());Map<String,Object>names=(Map<String,Object>)s.get("names");names=names==null?new HashMap<>():new HashMap<>(names);names.remove(u.getUid());Map<String,Object>st=(Map<String,Object>)s.get("stageByUid");st=st==null?new HashMap<>():new HashMap<>(st);st.remove(u.getUid());Map<String,Object>up=new HashMap<>();up.put("members",mem);up.put("names",names);up.put("stageByUid",st);tx.update(ref,up);return null;}).addOnCompleteListener(t->stopPuzzleWatchInternal());});}
        @JavascriptInterface public void stop(){runOnUiThread(this::stopPuzzleWatchInternal);}
    }

}
