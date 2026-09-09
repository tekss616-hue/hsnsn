from pathlib import Path
import re

J=Path('app/src/main/assets/social.js')
W=Path('.github/workflows/build-apk.yml')
j=J.read_text(encoding='utf-8')

# Root chat fix: opening a conversation must attach the realtime listeners.
old="currentPeer=b.dataset.chat;$('chatPeerName').textContent=b.dataset.name||'اللاعب';$('chatView').hidden=false;NativeSocial.loadMessages(currentPeer)"
new="currentPeer=b.dataset.chat;$('chatPeerName').textContent=b.dataset.name||'اللاعب';$('chatView').hidden=false;NativeSocial.watchChat?.(currentPeer);NativeSocial.loadMessages(currentPeer)"
if old in j:
    j=j.replace(old,new,1)
elif 'NativeSocial.watchChat?.(currentPeer)' not in j:
    raise SystemExit('consolidate: chat open hook not found')

# A realtime snapshot already updates the UI; do not do a second GET after every send.
j=j.replace("case'messageSent':$('chatInput').value='';if(currentPeer)NativeSocial.loadMessages(currentPeer);break", "case'messageSent':$('chatInput').value='';break",1)

# Replace the two overlapping cosmetics runtimes with one owner.
start=j.find(";(()=>{const BATCH_ONE=true")
friend=j.find(";(()=>{const FRIEND_PUSH_BRIDGE_V1=true")
second=j.find(";(()=>{\n const SECOND_ROLEPLAY_BATCH=true")
if start==-1 or friend==-1 or second==-1 or not(start<friend<second):
    raise SystemExit('consolidate: cosmetic runtime boundaries not found')
# Preserve the friend push bridge between the old cosmetic runtimes.
friend_block=j[friend:second]
# Find the end of the second runtime (last IIFE in generated file).
second_end=j.find("\n})();",second)
if second_end==-1: raise SystemExit('consolidate: second runtime end not found')
second_end += len("\n})();")

cosmetics=r'''
;(()=>{
const ROLEPLAY_COSMETICS_V3=true,$=id=>document.getElementById(id),ADMIN='bajanznsb@gmail.com';
const catalog={frame:[['f1','جمر','frame-fire'],['f2','فضة','frame-silver'],['f3','ملكي','frame-gold'],['f4','ليل','frame-night']],avatar:[['a1','رعد','ر'],['a2','نادر','ن'],['a3','ساهر','س'],['a4','مزن','م']]};
const frameClass=id=>({f1:'frame-fire',f2:'frame-silver',f3:'frame-gold',f4:'frame-night'}[id]||'');
const avatarGlyph=id=>({a1:'ر',a2:'ن',a3:'س',a4:'م'}[id]||'');
const admin=()=>{try{return !!NativeAuth?.isAdminAccount?.()}catch{return (localStorage.getItem('auth_email')||'').toLowerCase()===ADMIN}};
const inv=()=>{try{const x=JSON.parse(localStorage.getItem('rp_inv')||'{}');return{frames:Array.isArray(x.frames)?x.frames:[],avatars:Array.isArray(x.avatars)?x.avatars:[]}}catch{return{frames:[],avatars:[]}}};
const eq=()=>{try{return JSON.parse(localStorage.getItem('rp_eq')||'{}')}catch{return{}}};
function persist(){try{NativeSocial?.saveCosmetics?.(JSON.stringify(inv()),JSON.stringify(eq()))}catch{}}
function claimOrEquip(kind,id){const owned=inv(),key=kind+'s';if(!admin()&&!owned[key].includes(id)){owned[key].push(id);localStorage.setItem('rp_inv',JSON.stringify(owned))}const e=eq();e[kind]=id;localStorage.setItem('rp_eq',JSON.stringify(e));persist();render();applyAll(document)}
function item(kind,x){const owned=admin()||inv()[kind+'s'].includes(x[0]),on=eq()[kind]===x[0],preview=kind==='frame'?`<div class="cosmetic-preview ${x[2]}">ل</div>`:`<div class="cosmetic-preview">${x[2]}</div>`;return `<div class="cosmetic-item">${preview}<b>${kind==='frame'?'إطار ':'أفاتار '}${x[1]}</b><small>مجاني</small><button data-kind="${kind}" data-item="${x[0]}">${on?'مستخدم':owned?'استخدام':'أخذ مجانًا'}</button></div>`}
function render(){const owned=inv(),e=eq();if($('cosmeticStoreGrid'))$('cosmeticStoreGrid').innerHTML='<button class="store-category-card" data-store-category="frame"><b>الإطارات</b><small>اختر إطار الشخصية</small></button><button class="store-category-card" data-store-category="avatar"><b>الأفاتارات</b><small>اختر أفاتار الشخصية</small></button><button class="store-category-card" data-store-category="card"><b>البطاقات</b><small>قريبًا</small></button><button class="store-category-card" data-store-category="effect"><b>المؤثرات</b><small>قريبًا</small></button>';if($('inventoryGrid')){const rows=[...catalog.frame.filter(x=>owned.frames.includes(x[0])||e.frame===x[0]).map(x=>item('frame',x)),...catalog.avatar.filter(x=>owned.avatars.includes(x[0])||e.avatar===x[0]).map(x=>item('avatar',x))];$('inventoryGrid').innerHTML=rows.length?rows.join(''):'<div class="inventory-empty">مخزونك فارغ. خذ عنصرًا من المتجر أولًا.</div>'}}
function parseEquipped(raw){try{return typeof raw==='string'?JSON.parse(raw||'{}'):(raw||{})}catch{return{}}}
function decorate(host,raw){const e=parseEquipped(raw),av=host.matches?.('.mini-avatar,.public-avatar-core,.social-avatar,.world-avatar')?host:host.querySelector?.('.mini-avatar,.public-avatar-core,.social-avatar,.world-avatar');if(!av)return;av.classList.remove('frame-fire','frame-silver','frame-gold','frame-night','equipped-frame');const fc=frameClass(e.frame);if(fc)av.classList.add('equipped-frame',fc);const glyph=avatarGlyph(e.avatar);if(glyph)av.textContent=glyph}
function applyAll(root){root.querySelectorAll?.('[data-equipped]').forEach(x=>decorate(x,x.dataset.equipped));const self=eq();document.querySelectorAll('#socialAvatar').forEach(x=>decorate(x,self));document.querySelectorAll('.person-card,.request-card,.chat-row').forEach(x=>{if(x.dataset.frame||x.dataset.equipped)decorate(x,x.dataset.equipped||JSON.stringify({frame:x.dataset.frame}))})}
function openCategory(kind){const v=$('storeCategoryView'),g=$('storeCategoryGrid');if(!v||!g)return;document.querySelectorAll('main').forEach(x=>x.hidden=true);v.hidden=false;const names={frame:'الإطارات',avatar:'الأفاتارات',card:'البطاقات',effect:'المؤثرات'};$('storeCategoryTitle').textContent=names[kind]||'المتجر';const rows=catalog[kind]||[];g.innerHTML=rows.length?rows.map(x=>item(kind,x)).join(''):'<div class="inventory-empty">هذا القسم قريبًا.</div>'}
document.addEventListener('click',ev=>{const c=ev.target.closest?.('[data-store-category]');if(c){ev.preventDefault();openCategory(c.dataset.storeCategory);return}const b=ev.target.closest?.('[data-item]');if(b)claimOrEquip(b.dataset.kind,b.dataset.item)},true);
$('storeCategoryBack')?.addEventListener('click',()=>{$('storeCategoryView').hidden=true;$('gameStore').hidden=false});
$('inventoryBtn')?.addEventListener('click',()=>{document.querySelectorAll('main').forEach(x=>x.hidden=true);$('inventoryView').hidden=false;render()});
$('inventoryBack')?.addEventListener('click',()=>window.openInvestigatorProfile?.());
$('storeTab')?.addEventListener('click',()=>setTimeout(render,0));
$('publicIdentityClose')?.addEventListener('click',()=>$('publicIdentityCard').hidden=true);
document.getElementById('social')?.addEventListener('click',ev=>{const q=ev.target.closest?.('.person-card,.request-card');if(!q||ev.target.closest('button'))return;ev.stopImmediatePropagation();if(q.dataset.uid)NativeSocial?.loadPublicProfile?.(q.dataset.uid)},true);
let acceptTarget='';document.addEventListener('click',ev=>{const b=ev.target.closest?.('[data-accept]');if(b)acceptTarget=b.dataset.accept||''},true);
const old=window.onNativeSocialResult;window.onNativeSocialResult=r=>{if(r?.action==='publicProfile'&&r.ok){const p=r.player||{},av=$('publicIdentityAvatar');$('publicIdentityName').textContent=p.name||'لاعب';$('publicIdentityUsername').textContent=p.username?'@'+p.username:'@—';$('publicIdentityRank').textContent=p.rank||'صانع الدور';$('publicIdentityLevel').textContent=p.level||1;$('publicIdentityRoles').textContent=p.cases||0;$('publicIdentityDone').textContent=p.solved||0;$('publicIdentityAchievement').textContent=(p.accuracy||0)+'%';$('publicIdentityXp').style.width=(p.xpPercent||8)+'%';av.textContent=(p.name||'ل')[0];decorate(av,p.equipped);$('publicIdentityCard').hidden=false;return}if(r?.action==='cosmetics'&&r.ok){try{if(r.inventory)localStorage.setItem('rp_inv',r.inventory);if(r.equipped)localStorage.setItem('rp_eq',r.equipped)}catch{}render();applyAll(document);return}old?.(r);if(r?.ok&&r.action==='friendAccepted'){const uid=r.uid||acceptTarget;acceptTarget='';const base=(localStorage.getItem('hsnsn_ai_server_url')||'').trim();if(uid&&base)try{NativeSocial?.sendFriendAcceptedPush?.(base,uid)}catch{}};setTimeout(()=>applyAll(document),0)};
new MutationObserver(()=>applyAll(document)).observe(document.documentElement,{subtree:true,childList:true});
setTimeout(()=>{render();applyAll(document);NativeSocial?.loadCosmetics?.()},250);
})();
'''

j=j[:start]+cosmetics+friend_block+j[second_end:]
# Marker and invariant: only one cosmetics runtime remains.
if j.count('ROLEPLAY_COSMETICS_V3')!=1: raise SystemExit('consolidate: cosmetics owner count invalid')
J.write_text(j,encoding='utf-8')

# Future builds compile the checked-in final runtime directly. No mutation chain.
workflow='''name: Build Android APK\n\non:\n  push:\n    branches: [ main ]\n  workflow_dispatch:\n\npermissions:\n  contents: write\n\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - name: Checkout\n        uses: actions/checkout@v4\n      - name: Verify consolidated runtime\n        shell: bash\n        run: |\n          set -euo pipefail\n          node --check app/src/main/assets/app.js\n          node --check app/src/main/assets/social.js\n          grep -q 'ROLEPLAY_COSMETICS_V3' app/src/main/assets/social.js\n          grep -q 'watchChat' app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java\n          grep -q 'setTyping' app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java\n          grep -q 'sendFriendPush' app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java\n          grep -q 'sendFriendAcceptedPush' app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java\n          grep -q 'HsnsnMessagingService' app/src/main/AndroidManifest.xml\n          grep -q '/api/admin/nader/chat' app/src/main/assets/social.js\n          ! grep -q 'const BATCH_ONE=true' app/src/main/assets/social.js\n          ! grep -q 'SECOND_ROLEPLAY_BATCH=true' app/src/main/assets/social.js\n      - name: Set up JDK 17\n        uses: actions/setup-java@v4\n        with:\n          distribution: temurin\n          java-version: '17'\n      - name: Restore debug signing key\n        uses: actions/cache@v4\n        with:\n          path: ~/.config/.android/debug.keystore\n          key: veilmark-android-debug-keystore-v1\n      - name: Ensure stable debug signing key\n        shell: bash\n        run: |\n          set -euo pipefail\n          KEYSTORE="$HOME/.config/.android/debug.keystore"\n          mkdir -p "$(dirname "$KEYSTORE")"\n          if [ ! -f "$KEYSTORE" ]; then keytool -genkeypair -v -keystore "$KEYSTORE" -storepass android -alias AndroidDebugKey -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Android Debug,O=Android,C=US"; fi\n      - name: Set up Gradle\n        uses: gradle/actions/setup-gradle@v4\n        with:\n          gradle-version: '8.10.2'\n      - name: Stamp build version\n        shell: bash\n        run: |\n          set -euo pipefail\n          sed -i -E "s/versionCode [0-9]+/versionCode ${GITHUB_RUN_NUMBER}/" app/build.gradle\n          sed -i -E "s/versionName '[^']+'/versionName '1.0.${GITHUB_RUN_NUMBER}'/" app/build.gradle\n      - name: Build debug APK\n        run: gradle assembleDebug --stacktrace\n      - name: Upload APK\n        uses: actions/upload-artifact@v4\n        with:\n          name: action-template-apk\n          path: app/build/outputs/apk/debug/app-debug.apk\n          if-no-files-found: error\n      - name: Publish successful APK release\n        shell: bash\n        env:\n          GH_TOKEN: ${{ github.token }}\n        run: |\n          set -euo pipefail\n          TAG="build-${GITHUB_RUN_NUMBER}"\n          APK="app/build/outputs/apk/debug/app-debug.apk"\n          gh release create "$TAG" "$APK#app-debug.apk" --title "Build ${GITHUB_RUN_NUMBER}" --notes "Automatic successful APK build ${GITHUB_RUN_NUMBER}."\n'''
W.write_text(workflow,encoding='utf-8')
Path('runtime-consolidated-v1').write_text('Final runtime sources are checked in directly. Build-time mutation patches are retired.\n',encoding='utf-8')
print('Consolidated runtime: realtime chat owner, single cosmetics owner, direct-source workflow')
