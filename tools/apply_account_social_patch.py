from pathlib import Path
p=Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java')
s=p.read_text()
start=s.index('    public class AuthBridge {')
end=s.index('    public class SocialBridge {')
auth=r'''    public class AuthBridge {
        @JavascriptInterface public void warmAuth() { warmAuthComponents(); }
        private String cleanUsername(String value){ return value==null?"":value.trim().replaceFirst("^@","").toLowerCase(Locale.ROOT); }
        private boolean validUsername(String value){ return value.matches("[a-z0-9_]{3,20}"); }
        private void sendProfileAuth(String action,FirebaseUser user,boolean hasProfile){
            if(user==null){sendAuthResult(false,action,null,"تعذر قراءة الحساب.");return;}
            ensureFirestore();firestore.collection("users").document(user.getUid()).get().addOnCompleteListener(t->{
                try{JSONObject payload=new JSONObject();payload.put("ok",true);payload.put("action",action);payload.put("uid",user.getUid());payload.put("email",user.getEmail()==null?"":user.getEmail());payload.put("name",user.getDisplayName()==null?"":user.getDisplayName());
                    if(t.isSuccessful()&&t.getResult()!=null&&t.getResult().exists()){DocumentSnapshot d=t.getResult();payload.put("username",str(d,"username",""));payload.put("hasProfile",hasProfile||!str(d,"username","").isEmpty());}else payload.put("hasProfile",hasProfile);
                    final String js="window.onNativeAuthResult&&window.onNativeAuthResult("+payload+")";runOnUiThread(()->webView.evaluateJavascript(js,null));
                }catch(Exception e){sendAuthResult(true,action,user,null);}
            });
        }
        private void finishProfileAuth(FirebaseUser user,String name,String action){
            UserProfileChangeRequest up=new UserProfileChangeRequest.Builder().setDisplayName(name).build();
            user.updateProfile(up).addOnCompleteListener(t->{if(t.isSuccessful())sendProfileAuth(action,user,true);else sendAuthResult(false,action,null,t.getException()==null?"تعذر حفظ اسم المحقق.":t.getException().getLocalizedMessage());});
        }
        private void reserveAndSaveProfile(FirebaseUser user,String name,String username,String action){
            ensureFirestore();String un=cleanUsername(username);if(!validUsername(un)){sendAuthResult(false,action,null,"اسم المستخدم غير صالح.");return;}
            com.google.firebase.firestore.DocumentReference uname=firestore.collection("usernames").document(un);com.google.firebase.firestore.DocumentReference uref=firestore.collection("users").document(user.getUid());
            firestore.runTransaction(tr->{DocumentSnapshot existing=tr.get(uname);if(existing.exists()&&!user.getUid().equals(existing.getString("uid")))throw new com.google.firebase.firestore.FirebaseFirestoreException("اسم المستخدم مستخدم بالفعل.",com.google.firebase.firestore.FirebaseFirestoreException.Code.ABORTED);Map<String,Object> idx=new HashMap<>();idx.put("uid",user.getUid());tr.set(uname,idx);Map<String,Object>d=new HashMap<>();d.put("uid",user.getUid());d.put("name",name);d.put("nameLower",name.trim().toLowerCase(Locale.ROOT));d.put("username",un);d.put("usernameLower",un);d.put("email",user.getEmail()==null?"":user.getEmail());d.put("rank","محقق أول");d.put("updatedAt",FieldValue.serverTimestamp());tr.set(uref,d,com.google.firebase.firestore.SetOptions.merge());return null;})
            .addOnSuccessListener(v->finishProfileAuth(user,name,action))
            .addOnFailureListener(e->{if(e instanceof com.google.firebase.firestore.FirebaseFirestoreException&&((com.google.firebase.firestore.FirebaseFirestoreException)e).getCode()==com.google.firebase.firestore.FirebaseFirestoreException.Code.ABORTED)sendAuthResult(false,action,null,e.getLocalizedMessage());else finishProfileAuth(user,name,action);});
        }
        @JavascriptInterface public void createAccount(String name,String username,String email,String password){runOnUiThread(()->{ensureFirebaseAuth();firebaseAuth.createUserWithEmailAndPassword(email,password).addOnSuccessListener(r->{FirebaseUser u=r.getUser();if(u==null){sendAuthResult(false,"create",null,"تعذر إنشاء الحساب.");return;}reserveAndSaveProfile(u,name,username,"create");}).addOnFailureListener(e->sendAuthResult(false,"create",null,e.getLocalizedMessage()));});}
        @JavascriptInterface public void signInEmail(String email,String password){runOnUiThread(()->{ensureFirebaseAuth();firebaseAuth.signInWithEmailAndPassword(email,password).addOnSuccessListener(r->sendProfileAuth("login",r.getUser(),true)).addOnFailureListener(e->sendAuthResult(false,"login",null,e.getLocalizedMessage()));});}
        @JavascriptInterface public void signInGoogle(){runOnUiThread(()->{ensureFirebaseAuth();ensureCredentialManager();GetGoogleIdOption option=new GetGoogleIdOption.Builder().setFilterByAuthorizedAccounts(false).setServerClientId(getString(R.string.default_web_client_id)).build();GetCredentialRequest req=new GetCredentialRequest.Builder().addCredentialOption(option).build();credentialManager.getCredentialAsync(MainActivity.this,req,new CancellationSignal(),getMainExecutor(),new CredentialManagerCallback<GetCredentialResponse,GetCredentialException>(){public void onResult(GetCredentialResponse result){if(!(result.getCredential() instanceof CustomCredential)){sendAuthResult(false,"google",null,"تعذر قراءة حساب Google.");return;}CustomCredential c=(CustomCredential)result.getCredential();try{GoogleIdTokenCredential gc=GoogleIdTokenCredential.createFrom(c.getData());AuthCredential fc=GoogleAuthProvider.getCredential(gc.getIdToken(),null);firebaseAuth.signInWithCredential(fc).addOnSuccessListener(a->{FirebaseUser u=a.getUser();sendProfileAuth("google",u,false);}).addOnFailureListener(e->sendAuthResult(false,"google",null,e.getLocalizedMessage()));}catch(Exception e){sendAuthResult(false,"google",null,e.getLocalizedMessage());}}public void onError(@NonNull GetCredentialException e){sendAuthResult(false,"google",null,e.getLocalizedMessage());}});});}
        @JavascriptInterface public void completeProfile(String name,String username){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){sendAuthResult(false,"profileSetup",null,"انتهت جلسة الدخول.");return;}reserveAndSaveProfile(u,name,username,"profileSetup");});}
        @JavascriptInterface public void syncLocalProfile(String name,String username){runOnUiThread(()->{FirebaseUser u=currentUser();String un=cleanUsername(username);if(u==null||name==null||name.trim().length()<2||!validUsername(un)){sendAuthResult(false,"sync",null,null);return;}ensureFirestore();com.google.firebase.firestore.DocumentReference uname=firestore.collection("usernames").document(un);com.google.firebase.firestore.DocumentReference uref=firestore.collection("users").document(u.getUid());firestore.runTransaction(tr->{DocumentSnapshot existing=tr.get(uname);if(existing.exists()&&!u.getUid().equals(existing.getString("uid")))return null;Map<String,Object> idx=new HashMap<>();idx.put("uid",u.getUid());tr.set(uname,idx);Map<String,Object>d=new HashMap<>();d.put("uid",u.getUid());d.put("name",name.trim());d.put("nameLower",name.trim().toLowerCase(Locale.ROOT));d.put("username",un);d.put("usernameLower",un);d.put("email",u.getEmail()==null?"":u.getEmail());d.put("rank","محقق أول");d.put("updatedAt",FieldValue.serverTimestamp());tr.set(uref,d,com.google.firebase.firestore.SetOptions.merge());return null;}).addOnSuccessListener(v->sendAuthResult(true,"sync",u,null)).addOnFailureListener(e->sendAuthResult(false,"sync",null,null));});}
        @JavascriptInterface public void deleteAccount(){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){sendAuthResult(false,"delete",null,"لا يوجد حساب مسجل.");return;}ensureFirestore();firestore.collection("users").document(u.getUid()).get().addOnCompleteListener(t->{String un="";if(t.isSuccessful()&&t.getResult()!=null&&t.getResult().exists())un=str(t.getResult(),"username","");final String username=un;java.util.List<com.google.android.gms.tasks.Task<?>> cleanup=new java.util.ArrayList<>();cleanup.add(firestore.collection("users").document(u.getUid()).delete());if(!username.isEmpty())cleanup.add(firestore.collection("usernames").document(username).delete());Tasks.whenAllComplete(cleanup).addOnCompleteListener(x->u.delete().addOnSuccessListener(v->sendAuthResult(true,"delete",null,null)).addOnFailureListener(e->sendAuthResult(false,"delete",null,e.getLocalizedMessage())));}).addOnFailureListener(e->u.delete().addOnSuccessListener(v->sendAuthResult(true,"delete",null,null)).addOnFailureListener(err->sendAuthResult(false,"delete",null,err.getLocalizedMessage())));});}
        @JavascriptInterface public void signOut(){runOnUiThread(()->{ensureFirebaseAuth();firebaseAuth.signOut();sendAuthResult(true,"logout",null,null);});}
        @JavascriptInterface public void restoreSession(){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){sendAuthResult(false,"restore",null,null);return;}sendProfileAuth("restore",u,true);});}
    }

'''
s=s[:start]+auth+s[end:]
a=s.index('        @JavascriptInterface public void searchPlayer(String query) {')
b=s.index('        @JavascriptInterface public void sendFriendRequest',a)
search=r'''        @JavascriptInterface public void searchPlayer(String query) {
            runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){socialError("search",null);return;}ensureFirestore();String q=query.trim().replaceFirst("^@","").toLowerCase(Locale.ROOT);
                firestore.collection("users").whereEqualTo("usernameLower",q).limit(1).get().addOnSuccessListener(byUser->{
                    if(!byUser.isEmpty()){sendSearchResult(u,byUser);return;}
                    firestore.collection("users").whereEqualTo("nameLower",q).limit(10).get().addOnSuccessListener(byName->sendSearchResult(u,byName)).addOnFailureListener(e->socialError("search",e));
                }).addOnFailureListener(e->socialError("search",e));
            });
        }
        private void sendSearchResult(FirebaseUser me,QuerySnapshot snap){try{JSONObject out=new JSONObject();out.put("ok",true);out.put("action","search");for(DocumentSnapshot d:snap.getDocuments()){JSONObject p=new JSONObject();p.put("uid",d.getId());p.put("name",str(d,"name","محقق"));p.put("username",str(d,"username",""));p.put("rank",str(d,"rank","محقق"));p.put("self",d.getId().equals(me.getUid()));out.put("player",p);break;}sendSocial(out);}catch(Exception e){socialError("search",e);}}

'''
s=s[:a]+search+s[b:]
s=s.replace('po.put("name",str(pd,"name",u.getDisplayName()==null?"المحقق":u.getDisplayName()));po.put("rank"','po.put("name",str(pd,"name",u.getDisplayName()==null?"المحقق":u.getDisplayName()));po.put("username",str(pd,"username",""));po.put("rank"')
p.write_text(s)
print('Applied account/social patch')