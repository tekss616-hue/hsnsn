from pathlib import Path
p=Path('app/src/main/assets/app.js')
s=p.read_text()
old="if(r?.action!=='restore'&&r?.action!=='sync')error.textContent=friendlyAuthError(r?.message);return"
new="if(r?.action==='sync'&&r?.message==='USERNAME_CONFLICT'){const n=store.get('investigator_name','المحقق');store.del('investigator_username');showGoogleSetup({});$('playerName').value=n;setTimeout(()=>error.textContent='اسم المستخدم الحالي مستخدم بحساب آخر. اختر اسم مستخدم جديدًا وفريدًا.',40);return}if(r?.action!=='restore'&&r?.action!=='sync')error.textContent=friendlyAuthError(r?.message);return"
if old in s:s=s.replace(old,new,1)
old2="if(r.action==='google'){if(r.hasProfile&&r.name){store.set('investigator_name',r.name);if(r.username)store.set('investigator_username',r.username);showHQ(r.name)}else{showGoogleSetup(r);if(r.profileConflict)setTimeout(()=>error.textContent='اسم المستخدم السابق مرتبط بحساب آخر. اختر اسم مستخدم جديدًا وفريدًا.',40)}return}"
new2="if(r.action==='google'||r.action==='login'||r.action==='restore'){if(r.hasProfile&&r.name){store.set('investigator_name',r.name);if(r.username)store.set('investigator_username',r.username);showHQ(r.name)}else{clearAccountLocal();showGoogleSetup(r);if(r.name)$('playerName').value=r.name;if(r.profileConflict)setTimeout(()=>error.textContent='اسم المستخدم السابق مرتبط بحساب آخر. اختر اسم مستخدم جديدًا وفريدًا.',40)}return}"
if old2 in s:s=s.replace(old2,new2,1)
p.write_text(s)
print('Applied strict returning-account UI flow')
