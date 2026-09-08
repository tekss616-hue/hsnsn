from pathlib import Path

idx=Path('app/src/main/assets/index.html'); html=idx.read_text(encoding='utf-8')
cssf=Path('app/src/main/assets/social.css'); css=cssf.read_text(encoding='utf-8')
jsf=Path('app/src/main/assets/social.js'); js=jsf.read_text(encoding='utf-8')

if 'id="worldGame"' not in html:
    world=r'''
<main id="worldGame" class="world-game" hidden dir="rtl">
  <div class="world-scene" id="worldScene"></div>
  <header class="world-head">
    <button id="worldBack" class="world-round">‹</button>
    <div class="world-place"><small>العالم</small><h2 id="worldPlaceName">الشاطئ</h2></div>
    <button id="worldPlacesOpen" class="world-places-btn">الأماكن</button>
  </header>
  <section class="world-presence"><div id="worldAvatars" class="world-avatars"></div><span id="worldPresenceText">الموجودون الآن</span></section>
  <section id="worldMessages" class="world-messages"></section>
  <form id="worldComposer" class="world-composer"><input id="worldInput" maxlength="500" autocomplete="off" placeholder="اكتب رسالة…"><button type="submit">إرسال</button></form>
  <aside id="worldPlaces" class="world-places" hidden><div class="world-places-card"><header><h3>أماكن العالم</h3><button id="worldPlacesClose">×</button></header><p>انتقل لأي مكان. سترى عدد الموجودين قبل الدخول، وليس هوياتهم.</p><div id="worldPlacesGrid" class="world-places-grid"></div></div></aside>
</main>
'''
    html=html.replace('<script src="app.js"></script>',world+'<script src="app.js"></script>',1)

if '/* social-world-first-batch */' not in css:
    css += r'''
/* social-world-first-batch */
.world-game{position:fixed;inset:0;z-index:230;background:#070a0d;color:#fff;display:grid;grid-template-rows:auto auto 1fr auto;overflow:hidden}.world-game[hidden]{display:none!important}.world-scene{position:absolute;inset:0 0 auto;height:min(38vh,330px);background:radial-gradient(circle at 70% 20%,#41617c 0,#172b3b 30%,#071018 72%);z-index:-2}.world-scene:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,#0002,#070a0d 95%)}.world-game[data-place="palace"] .world-scene{background:radial-gradient(circle at 45% 25%,#826a45,#31261e 34%,#090b10 76%)}.world-game[data-place="garden"] .world-scene{background:radial-gradient(circle at 45% 20%,#3c6b58,#152d27 38%,#070a0d 78%)}.world-game[data-place="hospital"] .world-scene{background:radial-gradient(circle at 50% 20%,#60899a,#1b3541 38%,#070a0d 78%)}.world-game[data-place="police"] .world-scene{background:radial-gradient(circle at 45% 20%,#3b526b,#172331 40%,#070a0d 78%)}.world-game[data-place="market"] .world-scene,.world-game[data-place="restaurant"] .world-scene{background:radial-gradient(circle at 45% 20%,#8a6239,#332419 40%,#070a0d 78%)}.world-game[data-place="hotel"] .world-scene{background:radial-gradient(circle at 45% 20%,#78634d,#2c2520 40%,#070a0d 78%)}.world-game[data-place="harbor"] .world-scene{background:radial-gradient(circle at 45% 20%,#315b76,#102a3a 40%,#070a0d 78%)}.world-head{padding:calc(env(safe-area-inset-top) + 12px) 14px 8px;display:grid;grid-template-columns:48px 1fr auto;gap:10px;align-items:center}.world-round{width:44px;height:44px;border-radius:50%;border:1px solid #ffffff2b;background:#090d12aa;color:#fff;font-size:29px}.world-place small{color:#c9b184}.world-place h2{margin:1px 0;font-size:23px}.world-places-btn{border:1px solid #ffffff30;background:#111820cc;color:#fff;border-radius:13px;padding:11px 15px}.world-presence{display:flex;align-items:center;gap:10px;padding:4px 16px 12px;border-bottom:1px solid #ffffff14}.world-presence span{font-size:12px;color:#d5d8da}.world-avatars{display:flex;direction:ltr}.world-avatar{width:31px;height:31px;border-radius:50%;display:grid;place-items:center;background:#252d34;border:2px solid #0b0e11;margin-left:-7px;font-size:12px;font-weight:700}.world-messages{overflow:auto;padding:18px 14px 24px;display:flex;flex-direction:column;gap:10px}.world-msg{max-width:min(82%,620px);padding:10px 13px;border-radius:16px;background:#151b20;border:1px solid #ffffff12;line-height:1.55}.world-msg.mine{align-self:flex-start;background:#203344}.world-msg b{display:block;font-size:11px;color:#cbb789;margin-bottom:3px}.world-system{align-self:center;color:#8e989f;font-size:11px;padding:4px 10px}.world-composer{display:grid;grid-template-columns:1fr auto;gap:8px;padding:10px 12px calc(env(safe-area-inset-bottom) + 10px);background:#090d11ee;border-top:1px solid #ffffff16}.world-composer input{min-width:0;border:1px solid #303940;border-radius:15px;background:#12181d;color:#fff;padding:13px 14px;font-size:16px}.world-composer button{border:0;border-radius:14px;padding:0 18px;background:#d2b276;color:#17120b;font-weight:800}.world-places{position:absolute;inset:0;z-index:8;background:#000a;display:flex;align-items:flex-end}.world-places[hidden]{display:none!important}.world-places-card{width:100%;max-height:82vh;overflow:auto;background:#0d1216;border-radius:24px 24px 0 0;padding:18px 16px calc(env(safe-area-inset-bottom) + 20px)}.world-places-card header{display:flex;justify-content:space-between;align-items:center}.world-places-card h3{margin:0}.world-places-card header button{border:0;background:#1c242a;color:#fff;width:38px;height:38px;border-radius:50%;font-size:24px}.world-places-card p{color:#8f999f;font-size:12px}.world-places-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.world-place-card{min-height:105px;border:1px solid #2d363c;border-radius:17px;background:linear-gradient(145deg,#182129,#0e1317);color:#fff;text-align:right;padding:14px;display:flex;flex-direction:column;justify-content:flex-end}.world-place-card strong{font-size:17px}.world-place-card small{color:#a8b0b5;margin-top:5px}.world-place-card.active{border-color:#c6a66e;box-shadow:inset 0 0 0 1px #c6a66e55}@media(min-width:700px){.world-places-grid{grid-template-columns:repeat(3,1fr)}.world-messages{padding-left:max(8vw,24px);padding-right:max(8vw,24px)}.world-composer{padding-left:max(8vw,24px);padding-right:max(8vw,24px)}}
'''

if 'SOCIAL_WORLD_FIRST_BATCH' not in js:
    js += r'''
;(()=>{
const SOCIAL_WORLD_FIRST_BATCH=true,$=id=>document.getElementById(id);
const places=[['beach','الشاطئ','🏖️'],['palace','القصر','🏰'],['garden','الحديقة','🌳'],['hospital','المستشفى','🏥'],['police','مركز الشرطة والسجن','🚔'],['market','السوق','🛍️'],['restaurant','المطعم / المقهى','🍽️'],['hotel','الفندق','🏨'],['harbor','الميناء','⚓']];
let preview=false,current='beach',counts={beach:3,palace:2,garden:1,hospital:2,police:0,market:1,restaurant:2,hotel:0,harbor:1},messages={};
const nameOf=k=>(places.find(x=>x[0]===k)||[])[1]||k;
function profileName(){try{return JSON.parse(localStorage.getItem('profile_cache')||'{}').name||'أنت'}catch{return'أنت'}}
function seed(k){if(messages[k])return;messages[k]=[{system:true,text:'دخلت '+nameOf(k)}];if(preview&&k==='beach')messages[k].push({name:'نادر',text:'هلا والله 👋 شكل الليلة بتطول هنا ههههه'});}
function render(){seed(current);const g=$('worldGame');if(!g)return;g.dataset.place=current;$('worldPlaceName').textContent=nameOf(current);$('worldPresenceText').textContent='الموجودون الآن · '+(counts[current]||0);const av=$('worldAvatars');av.innerHTML='';for(let i=0;i<Math.min(counts[current]||0,5);i++){const x=document.createElement('span');x.className='world-avatar';x.textContent=i===0?'أ':String(i+1);av.appendChild(x)}const m=$('worldMessages');m.innerHTML='';messages[current].forEach(x=>{const d=document.createElement('div');if(x.system){d.className='world-system';d.textContent=x.text}else{d.className='world-msg'+(x.mine?' mine':'');d.innerHTML='<b></b><span></span>';d.querySelector('b').textContent=x.name;d.querySelector('span').textContent=x.text}m.appendChild(d)});m.scrollTop=m.scrollHeight;renderPlaces()}
function renderPlaces(){const grid=$('worldPlacesGrid');if(!grid)return;grid.innerHTML='';places.forEach(([k,n,e])=>{const b=document.createElement('button');b.type='button';b.className='world-place-card'+(k===current?' active':'');b.innerHTML='<strong>'+e+' '+n+'</strong><small>الموجودون الآن · '+(counts[k]||0)+'</small>';b.onclick=()=>move(k);grid.appendChild(b)})}
function move(k){if(k===current){$('worldPlaces').hidden=true;return}messages[current]=messages[current]||[];messages[current].push({system:true,text:profileName()+' غادر المكان'});current=k;seed(k);messages[k].push({system:true,text:profileName()+' وصل إلى '+nameOf(k)});$('worldPlaces').hidden=true;render()}
function openWorld(isPreview){preview=!!isPreview;current='beach';const g=$('worldGame');if(!g)return;g.hidden=false;document.body.style.overflow='hidden';render()}
function closeWorld(){const g=$('worldGame');if(g)g.hidden=true;document.body.style.overflow=''}
document.addEventListener('click',e=>{if(e.target.closest?.('#worldBack'))closeWorld();if(e.target.closest?.('#worldPlacesOpen')){$('worldPlaces').hidden=false;renderPlaces()}if(e.target.closest?.('#worldPlacesClose'))$('worldPlaces').hidden=true;if(e.target.closest?.('#adminPreviewOpen'))setTimeout(()=>openWorld(true),0)},true);
$('worldComposer')?.addEventListener('submit',e=>{e.preventDefault();const i=$('worldInput'),t=i.value.trim();if(!t)return;seed(current);messages[current].push({name:profileName(),text:t,mine:true});i.value='';render();if(preview){setTimeout(()=>{if(current==='beach'){messages[current].push({name:'نادر',text:'وصلت 😂 خلنا نشوف وش بيصير الليلة'});render()}},650)}});
window.HSNSNWorld={open:()=>openWorld(false),preview:()=>openWorld(true),move};
})();
'''

idx.write_text(html,encoding='utf-8');cssf.write_text(css,encoding='utf-8');jsf.write_text(js,encoding='utf-8')
print('Applied social world first batch with admin player-view preview')
