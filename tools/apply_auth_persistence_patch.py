from pathlib import Path

p=Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java')
s=p.read_text()
marker='    public class AuthBridge {'
helpers=r'''    private static final String AUTH_PROFILE_SEP = "\u2063";
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

'''
if 'AUTH_PROFILE_SEP' not in s:
    s=s.replace(marker,helpers+marker,1)

start=s.index('    public class AuthBridge {')
end=s.index('    public class SocialBridge {')
auth=r'''    public class AuthBridge {
        @JavascriptInterface public void warmAuth() { warmAuthComponents(); }
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
                Map<String,Object>d=new HashMap<>();d.put("uid",u.getUid());d.put("name",name.trim());d.put("nameLower",name.trim().toLowerCase(Locale.ROOT));d.put("username",un);d.put("usernameLower",un);d.put("email",u.getEmail()==null?"":u.getEmail());d.put("rank","محقق أول");d.put("updatedAt",FieldValue.serverTimestamp());
                tr.set(uref,d,com.google.firebase.firestore.SetOptions.merge());return null;
            });
        }

        private void dispatchProfile(String action,FirebaseUser user,String name,String username,boolean hasProfile,boolean conflict){
            try{JSONObject payload=new JSONObject();payload.put("ok",true);payload.put("action",action);payload.put("uid",user.getUid());payload.put("email",user.getEmail()==null?"":user.getEmail());payload.put("name",name==null?"":name);payload.put("username",username==null?"":username);payload.put("hasProfile",hasProfile);if(conflict)payload.put("profileConflict",true);final String js="window.onNativeAuthResult&&window.onNativeAuthResult("+payload+")";runOnUiThread(()->webView.evaluateJavascript(js,null));}catch(Exception ignored){}
        }
        private void normalizeVisibleDisplayName(FirebaseUser user,String visibleName){
            if(user==null||visibleName==null||visibleName.trim().isEmpty())return;
            String raw=user.getDisplayName()==null?"":user.getDisplayName();
            if(!raw.equals(visibleName.trim())){UserProfileChangeRequest up=new UserProfileChangeRequest.Builder().setDisplayName(visibleName.trim()).build();user.updateProfile(up);}
        }
        private void sendProfileAuth(String action,FirebaseUser user,boolean hintedProfile){
            if(user==null){sendAuthResult(false,action,null,"تعذر قراءة الحساب.");return;}
            final String fallbackName=authVisibleName(user);final String legacyUsername=cleanUsername(authEmbeddedUsername(user));ensureFirestore();
            firestore.collection("users").document(user.getUid()).get().addOnCompleteListener(t->{
                if(!t.isSuccessful()){sendAuthResult(false,action,null,"تعذر قراءة هوية المحقق من الخادم.");return;}
                String name=fallbackName,username=legacyUsername;boolean docExists=t.getResult()!=null&&t.getResult().exists();
                if(docExists){DocumentSnapshot d=t.getResult();String dn=str(d,"name",name),du=cleanUsername(str(d,"username",username));if(!dn.isEmpty())name=dn;if(!du.isEmpty())username=du;}
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
        @JavascriptInterface public void deleteAccount(){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){sendAuthResult(false,"delete",null,"لا يوجد حساب مسجل.");return;}ensureFirestore();firestore.collection("users").document(u.getUid()).get().addOnCompleteListener(t->{String un="";if(t.isSuccessful()&&t.getResult()!=null&&t.getResult().exists())un=cleanUsername(str(t.getResult(),"username",""));final String username=un;java.util.List<com.google.android.gms.tasks.Task<?>> cleanup=new java.util.ArrayList<>();cleanup.add(firestore.collection("users").document(u.getUid()).delete());if(!username.isEmpty())cleanup.add(firestore.collection("usernames").document(username).delete());Tasks.whenAllComplete(cleanup).addOnCompleteListener(x->u.delete().addOnSuccessListener(v->sendAuthResult(true,"delete",null,null)).addOnFailureListener(e->sendAuthResult(false,"delete",null,e.getLocalizedMessage())));});});}
        @JavascriptInterface public void signOut(){runOnUiThread(()->{ensureFirebaseAuth();firebaseAuth.signOut();sendAuthResult(true,"logout",null,null);});}
        @JavascriptInterface public void restoreSession(){runOnUiThread(()->{FirebaseUser u=currentUser();if(u==null){sendAuthResult(false,"restore",null,null);return;}sendProfileAuth("restore",u,false);});}
    }

'''
s=s[:start]+auth+s[end:]

s=s.replace('u.getDisplayName()==null?"المحقق":u.getDisplayName()','authVisibleName(u).isEmpty()?"المحقق":authVisibleName(u)')
s=s.replace('u.getDisplayName()==null?"محقق":u.getDisplayName()','authVisibleName(u).isEmpty()?"محقق":authVisibleName(u)')
s=s.replace('user.getDisplayName()==null?"":user.getDisplayName()','authVisibleName(user)')

p.write_text(s)
print('Applied rooted auth/profile integrity patch')
