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

import com.google.android.libraries.identity.googleid.GetGoogleIdOption;
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential;
import com.google.firebase.auth.AuthCredential;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.auth.GoogleAuthProvider;
import com.google.firebase.auth.UserProfileChangeRequest;

import org.json.JSONObject;

public class MainActivity extends Activity {
    private WebView webView;
    private ValueCallback<Uri[]> filePathCallback;
    private static final int FILE_CHOOSER_REQUEST = 1001;
    private FirebaseAuth firebaseAuth;
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

    private void ensureFirebaseAuth() {
        if (firebaseAuth == null) firebaseAuth = FirebaseAuth.getInstance();
    }

    private void ensureCredentialManager() {
        if (credentialManager == null) credentialManager = CredentialManager.create(this);
    }

    private void warmAuthComponents() {
        runOnUiThread(() -> {
            ensureFirebaseAuth();
            ensureCredentialManager();
        });
    }

    private void sendAuthResult(boolean ok, String action, FirebaseUser user, String message) {
        try {
            JSONObject payload = new JSONObject();
            payload.put("ok", ok);
            payload.put("action", action);
            if (message != null) payload.put("message", message);
            if (user != null) {
                payload.put("uid", user.getUid());
                payload.put("email", user.getEmail() == null ? "" : user.getEmail());
                payload.put("name", user.getDisplayName() == null ? "" : user.getDisplayName());
            }
            final String js = "window.onNativeAuthResult&&window.onNativeAuthResult(" + payload.toString() + ")";
            runOnUiThread(() -> webView.evaluateJavascript(js, null));
        } catch (Exception ignored) { }
    }

    private void notifyJs(String functionName) {
        if (webView == null) return;
        webView.evaluateJavascript("window." + functionName + "&&window." + functionName + "()", null);
    }

    public class AuthBridge {
        @JavascriptInterface
        public void warmAuth() {
            warmAuthComponents();
        }

        @JavascriptInterface
        public void createAccount(String name, String email, String password) {
            runOnUiThread(() -> {
                ensureFirebaseAuth();
                firebaseAuth.createUserWithEmailAndPassword(email, password)
                    .addOnSuccessListener(result -> {
                        FirebaseUser user = result.getUser();
                        if (user == null) {
                            sendAuthResult(false, "create", null, "تعذر إنشاء الحساب.");
                            return;
                        }
                        sendAuthResult(true, "create", user, null);
                        UserProfileChangeRequest update = new UserProfileChangeRequest.Builder()
                            .setDisplayName(name)
                            .build();
                        user.updateProfile(update);
                    })
                    .addOnFailureListener(e -> sendAuthResult(false, "create", null, e.getLocalizedMessage()));
            });
        }

        @JavascriptInterface
        public void signInEmail(String email, String password) {
            runOnUiThread(() -> {
                ensureFirebaseAuth();
                firebaseAuth.signInWithEmailAndPassword(email, password)
                    .addOnSuccessListener(result -> sendAuthResult(true, "login", result.getUser(), null))
                    .addOnFailureListener(e -> sendAuthResult(false, "login", null, e.getLocalizedMessage()));
            });
        }

        @JavascriptInterface
        public void signInGoogle() {
            runOnUiThread(() -> {
                ensureFirebaseAuth();
                ensureCredentialManager();
                GetGoogleIdOption googleIdOption = new GetGoogleIdOption.Builder()
                    .setFilterByAuthorizedAccounts(false)
                    .setServerClientId(getString(R.string.default_web_client_id))
                    .build();
                GetCredentialRequest request = new GetCredentialRequest.Builder()
                    .addCredentialOption(googleIdOption)
                    .build();
                credentialManager.getCredentialAsync(
                    MainActivity.this,
                    request,
                    new CancellationSignal(),
                    getMainExecutor(),
                    new CredentialManagerCallback<GetCredentialResponse, GetCredentialException>() {
                        @Override
                        public void onResult(GetCredentialResponse result) {
                            if (!(result.getCredential() instanceof CustomCredential)) {
                                sendAuthResult(false, "google", null, "تعذر قراءة بيانات حساب Google.");
                                return;
                            }
                            CustomCredential credential = (CustomCredential) result.getCredential();
                            if (!GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL.equals(credential.getType())) {
                                sendAuthResult(false, "google", null, "نوع اعتماد Google غير مدعوم.");
                                return;
                            }
                            try {
                                GoogleIdTokenCredential googleCredential = GoogleIdTokenCredential.createFrom(credential.getData());
                                AuthCredential firebaseCredential = GoogleAuthProvider.getCredential(googleCredential.getIdToken(), null);
                                firebaseAuth.signInWithCredential(firebaseCredential)
                                    .addOnSuccessListener(auth -> sendAuthResult(true, "google", auth.getUser(), null))
                                    .addOnFailureListener(e -> sendAuthResult(false, "google", null, e.getLocalizedMessage()));
                            } catch (Exception e) {
                                sendAuthResult(false, "google", null, e.getLocalizedMessage());
                            }
                        }

                        @Override
                        public void onError(@NonNull GetCredentialException e) {
                            sendAuthResult(false, "google", null, e.getLocalizedMessage());
                        }
                    }
                );
            });
        }

        @JavascriptInterface
        public void updatePlayerName(String name) {
            runOnUiThread(() -> {
                ensureFirebaseAuth();
                FirebaseUser user = firebaseAuth.getCurrentUser();
                if (user == null) {
                    sendAuthResult(false, "playerName", null, "انتهت جلسة تسجيل الدخول. حاول مرة أخرى.");
                    return;
                }
                UserProfileChangeRequest update = new UserProfileChangeRequest.Builder().setDisplayName(name).build();
                user.updateProfile(update)
                    .addOnSuccessListener(v -> sendAuthResult(true, "playerName", user, null))
                    .addOnFailureListener(e -> sendAuthResult(false, "playerName", null, e.getLocalizedMessage()));
            });
        }

        @JavascriptInterface
        public void signOut() {
            runOnUiThread(() -> {
                ensureFirebaseAuth();
                firebaseAuth.signOut();
                sendAuthResult(true, "logout", null, null);
            });
        }

        @JavascriptInterface
        public void restoreSession() {
            runOnUiThread(() -> {
                ensureFirebaseAuth();
                FirebaseUser user = firebaseAuth.getCurrentUser();
                sendAuthResult(user != null, "restore", user, null);
            });
        }
    }

    @Override
    protected void onPause() {
        if (webView != null) notifyJs("onNativeAppPause");
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (webView != null) notifyJs("onNativeAppResume");
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == FILE_CHOOSER_REQUEST && filePathCallback != null) {
            Uri[] results = WebChromeClient.FileChooserParams.parseResult(resultCode, data);
            filePathCallback.onReceiveValue(results);
            filePathCallback = null;
        }
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }
}
