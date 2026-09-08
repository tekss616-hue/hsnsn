from pathlib import Path

# Native deletion must reauthenticate BEFORE deleting Firestore profile data.
p=Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java')
s=p.read_text()
start=s.index('        @JavascriptInterface public void deleteAccount()')
end=s.index('        @JavascriptInterface public void signOut()',start)
block=r'''        private boolean usesGoogle(FirebaseUser u){
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
'''
s=s[:start]+block+s[end:]
p.write_text(s)

# Password reauthentication modal for email/password accounts.
p=Path('app/src/main/assets/app.js')
s=p.read_text()
anchor="window.appConfirm=(message,opts={})=>showAppDialog(message,opts);window.appNotice=(message,opts={})=>showAppDialog(message,{...opts,notice:true,ok:opts.ok||'حسنًا'});"
helper=r'''
function requestDeletePassword(){return new Promise(resolve=>{let d=document.getElementById('deletePasswordDialog');if(!d){d=document.createElement('div');d.id='deletePasswordDialog';d.className='app-dialog';d.innerHTML='<div class="app-dialog-card"><div class="app-dialog-mark">◈</div><h3>تأكيد هوية الحساب</h3><p>أدخل كلمة مرور حسابك لإكمال الحذف النهائي.</p><input id="deletePasswordInput" type="password" autocomplete="current-password" placeholder="كلمة المرور" style="width:100%;box-sizing:border-box;margin-top:16px;min-height:48px;border-radius:12px;border:1px solid #ffffff22;background:#090c0e;color:#fff;padding:0 14px"><div class="app-dialog-actions"><button id="deletePasswordCancel" class="app-dialog-btn secondary">إلغاء</button><button id="deletePasswordOk" class="app-dialog-btn primary-dialog danger-dialog">متابعة الحذف</button></div></div>';document.body.appendChild(d)}d.hidden=false;const input=document.getElementById('deletePasswordInput');input.value='';setTimeout(()=>input.focus(),50);document.getElementById('deletePasswordCancel').onclick=()=>{d.hidden=true;resolve('')};document.getElementById('deletePasswordOk').onclick=()=>{const v=input.value;d.hidden=true;resolve(v)}})}
'''
if 'function requestDeletePassword()' not in s:
    s=s.replace(anchor,anchor+helper,1)
old="if(r?.action==='delete'){window.appNotice?.(friendlyAuthError(r?.message),{title:'تعذر حذف الحساب'});return}"
new="if(r?.action==='delete'){if(r?.message==='REAUTH_PASSWORD'){requestDeletePassword().then(p=>{if(p)NativeAuth?.reauthenticatePasswordAndDelete?.(p)});return}window.appNotice?.(friendlyAuthError(r?.message),{title:'تعذر حذف الحساب'});return}"
s=s.replace(old,new)
p.write_text(s)
print('Applied secure delete reauthentication patch')
