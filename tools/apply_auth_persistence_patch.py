from pathlib import Path
p=Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java')
s=p.read_text()
start=s.index('    public class AuthBridge {')
end=s.index('    public class SocialBridge {')
auth=r'''    public class AuthBridge {
        private static final String PROFILE_SEP = "\u2063";
        @JavascriptInterface public void warmAuth() { warmAuthComponents(); }
        private String cleanUsername(String value){ return value==null?"":value.trim().replaceFirst("^@","").toLowerCase(Locale.ROOT); }
        private boolean validUsername(String value){ return value.matches("[a-z0-9_]{3,20}"); }
        private String encodedDisplayName(String name,String username){ return name.trim()+PROFILE_SEP+cleanUsername(username); }
        private String authProfileName(FirebaseUser u){ String raw=u==null||u.getDisplayName()==null?"":u.getDisplayName();int i=raw.indexOf(PROFILE_SEP);return (i>=0?raw.substring(0,i):raw).trim(); }
        private String authProfileUsername(FirebaseUser u){ String raw=u==null||u.getDisplayName()==null?"":u.getDisplayName();int i=raw.indexOf(PROFILE_SEP);return i>=0?cleanUsername(raw.substring(i+PROFILE_SEP.length())):""; }
        private void writeProfileDocs(FirebaseUser u,String name,String username){
            if(u==null)return;String un=cleanUsername(username);if(name==null||name.trim().length()<2||!validUsername(un))return;ensureFirestore();
            com.google.firebase.firestore.DocumentReference uname=firestore.collection("usernames").document(un);com.google.firebase.firestore.DocumentReference uref=firestore.collection("users").document(u.getUid());
            firestore.runTransaction(tr->{DocumentSnapshot existing=tr.get(uname);if(existing.exists()&&!u.getUid().equals(existing.getString("uid")))return null;Map<String,Object> idx=new HashMap<>();idx.put("uid",u.getUid());tr.set(uname,idx);Map<String,Object>d=new HashMap<>();d.put("uid",u.getUid());d.put("name",name.trim());d.put("nameLower",name.trim().toLowerCase(Locale.ROOT));d.put("username",un);d.put("usernameLower",un);d.put("email",u.getEmail()==null?"":u.getEmail());d.put("rank","محقق أول");d.put("updatedAt",FieldValue.serverTimestamp());tr.set(uref,d,com.google.firebase.firestore.SetOptions.merge());return null;});
        }
        private void sendProfileAuth(String action,FirebaseUser user,boolean hintedProfile){
            if(user==null){sendAuthResult(false,action,null,"تعذر قراءة الحساب.");return;}
            final String fallbackName=authProfileName(user);final String fallbackUsername=authProfileUsername(user);ensureFirestore();
            firestore.collection("users").document(user.getUid()).get().addOnCompleteListener(t->{
                try{JSONObject payload=new JSONObject();payload.put("ok",true);payload.put("action",action);payload.put("uid",user.getUid());payload.put("email",user.getEmail()==null?"":user.getEmail());String name=fallbackName;String username=fallbackUsername;boolean hasProfile=hintedProfile&&!username.isEmpty();
                    if(t.isSuccessful()&&t.getResult()!=null&&t.getResult().exists()){DocumentSnapshot d=t.getResult();String dn=str(d,"name",name);String du=str(d,"username",username);if(!dn.isEmpty())name=dn;if(!du.isEmpty())username=du;hasProfile=!username.isEmpty();}
                    if(!username.isEmpty()&&!name.isEmpty())writeProfileDocs(user,name,username);
                    payload.put("name",name);payload.put("username",username);payload.put("hasProfile",hasProfile||!username.isEmpty());
                    final String js="window.onNativeAuthResult&&window.onNativeAuthResult("+payload+")";runOnUiThread(()->webView.evaluateJavascript(js,null));
                }catch(Exception e){try{JSONObject payload=new JSONObject();payload.put("ok",true);payload.put("action",action);payload.put("uid",user.getUid());payload.put("email",user.getEmail()==null?"":user.getEmail());payload.put("name",fallbackName);payload.put("username",fallbackUsername);payload.put("hasProfile",!fallbackUsername.isEmpty());final String js="window.onNativeAuthResult&&window.onNativeAuthResult("+payload+")";runOnUiThread(()->webView.evaluateJavascript(js,null));}catch(Exception ignored){}}
            });
        }
        private void finishProfileAuth(FirebaseUser user,String name,String username,String action){
            String un=cleanUsername(username);UserProfileChangeRequest up=new UserProfileChangeRequest.Builder().setDisplayName(encodedDisplayName(name,un)).build();
            user.updateProfile(up).addOnCompleteListener(t->{if(t.isSuccessful()){writeProfileDocs(user,name,un);sendProfileAuth(action,user,true);}else sendAuthResult(false,action,null,t.getException()==null?"تعذر حفظ هوية المحقق.":t.getException().getLocalizedMessage());});
        }
        private void reserveAndSaveProfile(FirebaseUser user,String name,String username,String action){
            String un=cleanUsername(username);if(!validUsername(un)){sendAuthResult(false,action,null,"اسم المستخدم غير صالح.");return;}ensureFirestore();
            com.google.firebase.firestore.DocumentReference uname=firestore.collection("usernames").document(un);firestore.runTransaction(tr->{DocumentSnapshot existing=tr.get(uname);if(existing.exists()&&!user.getUid().equals(existing.getString("uid")))throw new com.google.firebase.firestore.FirebaseFirestoreException("اسم المستخدم مستخدم بالفعل.",com.google.firebase.firestore.FirebaseFirestoreException.Code.ABORTED);return null;})
            .addOnSuccessListener(v->finishProfileAuth(user,name,un,action))
            .addOnFailureListener(e->{if(e instanceof com.google.firebase.firestore.FirebaseFirestoreException&&((com.google.firebase.firestore.FirebaseFirestoreException)e).getCode()==com.google.firebase.firestore.FirebaseFirestoreException.Code.ABORTED)sendAuthResult(false,action,null,e.getLocalizedMessage());else finishProfileAuth(user,name,un,action);});
        }
        @JavascriptInterface public void createAccount(String name,String username,String email,String password){runOnUiThread(()->{ensureFirebaseAuth();firebaseAuth.createUserWithEmailAndPassword(email,password).addOnSuccessListener(r->{FirebaseUser u=r.getUser();if(u==null){sendAuthResult(false,"create",null,"تعذر إنشاء الحساب.");return;}reserveAndSaveProfile(u,name,username,"create");}).addOnFailureListener(e->sendAuthResult(false,"create",null,e.getLocalizedMessage()));});}
        @JavascriptInterface public void signInEmail(String email,String password){runOnUiThread(()->{ensureFirebaseAuth();firebaseAuth.signInWithEmailAndPassword(email,password).addOnSuccessListener(r->sendProfileAuth("login",r.getUser(),false)).addOnFailureListener(e->sendAuthResult(false,"login",null,e.getLocalizedMessage()));});}
        @JavascriptInterface public void signInGoogle(){runOnUiThread(()->{ensureFirebaseAuth();ensureCredentialManager();GetGoogleIdOption option=new GetGoogleIdOption.Builder().setFilterByAuthorizedAccounts(false).setServerClientId(getString(R.string.default_web_client_id)).build();GetCredentialRequest req=new GetCredentialRequest.Builder().addCredentialOption(option).build();credentialManager.getCredentialAsync(MainActivity.this,req,new CancellationSignal(),getMainExecutor(),new CredentialManagerCallback<GetCredentialResponse,GetCredentialException>(){public void onResult(GetCredentialResponse result){if(!(result.getCredential() instanceof CustomCredential)){sendAuthResult(false,"google",null,"تعذر قراءة حساب Google.");return;}CustomCredential c=(CustomCredential)result.getCredential();try{GoogleIdTokenCredential gc=GoogleIdTokenCredential.createFrom(c.getData());AuthCredential fc=GoogleAuthProvider.getCredential(gc.getIdToken(),null);firebaseAuth.signInWithCredential(fc).addOnSuccessListener(a->sendProfileAuth("google",a.getUser(),false)).addOnFailureListener(e->sendAuthResult(false,"google",null,e.getLocalizedMessage()));}catch(Exception e){sendAuthResult(false,"google",null,e.getLocalizedMessage());}}public void onError(@NonNull GetCredentialException e){sendAuthResult(false,"google",null,e.getLocalizedMessage());}});});}
        @JavascriptInterface public void completeProfile(String name,String username){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){sendAuthResult(false,"profileSetup",null,"انتهت جلسة الدخول.");return;}reserveAndSaveProfile(u,name,username,"profileSetup");});}
        @JavascriptInterface public void syncLocalProfile(String name,String username){runOnUiThread(()->{FirebaseUser u=currentUser();String un=cleanUsername(username);if(u==null||name==null||name.trim().length()<2||!validUsername(un)){sendAuthResult(false,"sync",null,null);return;}UserProfileChangeRequest up=new UserProfileChangeRequest.Builder().setDisplayName(encodedDisplayName(name,un)).build();u.updateProfile(up).addOnCompleteListener(t->{writeProfileDocs(u,name,un);sendAuthResult(true,"sync",u,null);});});}
        @JavascriptInterface public void deleteAccount(){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){sendAuthResult(false,"delete",null,"لا يوجد حساب مسجل.");return;}String authUn=authProfileUsername(u);ensureFirestore();firestore.collection("users").document(u.getUid()).get().addOnCompleteListener(t->{String un=authUn;if(t.isSuccessful()&&t.getResult()!=null&&t.getResult().exists())un=str(t.getResult(),"username",authUn);final String username=un;java.util.List<com.google.android.gms.tasks.Task<?>> cleanup=new java.util.ArrayList<>();cleanup.add(firestore.collection("users").document(u.getUid()).delete());if(!username.isEmpty())cleanup.add(firestore.collection("usernames").document(username).delete());Tasks.whenAllComplete(cleanup).addOnCompleteListener(x->u.delete().addOnSuccessListener(v->sendAuthResult(true,"delete",null,null)).addOnFailureListener(e->sendAuthResult(false,"delete",null,e.getLocalizedMessage())));});});}
        @JavascriptInterface public void signOut(){runOnUiThread(()->{ensureFirebaseAuth();firebaseAuth.signOut();sendAuthResult(true,"logout",null,null);});}
        @JavascriptInterface public void restoreSession(){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){sendAuthResult(false,"restore",null,null);return;}sendProfileAuth("restore",u,false);});}
    }

'''
s=s[:start]+auth+s[end:]
p.write_text(s)
print('Applied durable auth profile patch')
