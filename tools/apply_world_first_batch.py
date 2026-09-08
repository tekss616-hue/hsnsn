from pathlib import Path

idx=Path('app/src/main/assets/index.html'); html=idx.read_text(encoding='utf-8')
cssf=Path('app/src/main/assets/social.css'); css=cssf.read_text(encoding='utf-8')
jsf=Path('app/src/main/assets/social.js'); js=jsf.read_text(encoding='utf-8')

if 'id="worldGame"' not in html:
    world=r'''
<main id="worldGame" class="world-game" hidden dir="rtl" aria-label="العالم الاجتماعي">
  <div class="world-scene" id="worldScene" aria-hidden="true"><div class="world-orb"></div><div class="world-horizon"></div><div class="world-landmark"></div><div class="world-depth"></div></div>
  <header class="world-head">
    <button id="worldBack" class="world-round" aria-label="العودة">‹</button>
    <div class="world-place"><small id="worldModeLabel">العالم</small><h2 id="worldPlaceName">الشاطئ</h2></div>
    <button id="worldPlacesOpen" class="world-places-btn">الأماكن</button>
  </header>
  <section class="world-presence"><div id="worldAvatars" class="world-avatars"></div><span id="worldPresenceText">الموجودون الآن</span><span id="worldNaderStatus" class="world-nader-status" hidden>نادر موجود هنا</span></section>
  <section id="worldMessages" class="world-messages" aria-live="polite"></section>
  <div id="worldTyping" class="world-typing" hidden></div>
  <form id="worldComposer" class="world-composer"><input id="worldInput" maxlength="500" autocomplete="off" enterkeyhint="send" placeholder="اكتب رسالة…"><button type="submit">إرسال</button></form>
  <aside id="worldPlaces" class="world-places" hidden><div class="world-places-card"><header><h3>أماكن العالم</h3><button id="worldPlacesClose" aria-label="إغلاق">×</button></header><p>انتقل لأي مكان. سترى عدد الموجودين قبل الدخول.</p><div id="worldPlacesGrid" class="world-places-grid"></div></div></aside>
</main>
'''
    html=html.replace('<script src="app.js"></script>',world+'<script src="app.js"></script>',1)

# Remove older world blocks before appending the upgraded responsive system.
for marker in ['/* social-world-first-batch */','/* social-world-approved-images */','/* social-world-v2 */']:
    if marker in css:
        css=css.split(marker,1)[0].rstrip()+"\n"

css += r'''
/* social-world-v2 */
.world-game{position:fixed;inset:0;z-index:10000;background:#070a0d;color:#fff;display:grid;grid-template-rows:auto auto minmax(0,1fr) auto auto;overflow:hidden;isolation:isolate}.world-game[hidden]{display:none!important}
.world-scene{position:absolute;inset:0 0 auto 0;height:clamp(250px,39svh,430px);overflow:hidden;z-index:-2;background:linear-gradient(180deg,#274b67 0%,#193247 36%,#101d27 68%,#080c10 100%);transition:background .45s ease}
.world-scene:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.04),rgba(7,10,13,.16) 52%,#070a0d 100%)}
.world-orb{position:absolute;width:84px;height:84px;border-radius:50%;left:12%;top:13%;background:radial-gradient(circle at 35% 35%,#fff7d9 0 10%,#e9c98b 38%,#d7a951 70%,transparent 72%);opacity:.72;filter:blur(.2px)}
.world-horizon{position:absolute;left:-5%;right:-5%;bottom:20%;height:44%;background:linear-gradient(180deg,transparent 0 30%,rgba(8,15,18,.15) 31%),linear-gradient(12deg,transparent 0 41%,#0b171b 42% 64%,transparent 65%);opacity:.9}
.world-landmark{position:absolute;left:50%;bottom:18%;width:min(62vw,460px);height:43%;transform:translateX(-50%);background:#10191d;opacity:.9;clip-path:polygon(6% 100%,6% 62%,16% 62%,16% 44%,25% 44%,25% 62%,36% 62%,36% 32%,46% 32%,46% 17%,54% 17%,54% 32%,64% 32%,64% 62%,75% 62%,75% 44%,84% 44%,84% 62%,94% 62%,94% 100%)}
.world-depth{position:absolute;inset:auto -10% 0;height:27%;background:radial-gradient(ellipse at 50% 100%,#152129 0,#0c1419 50%,#070a0d 74%)}
.world-game[data-place="beach"] .world-scene{background:linear-gradient(180deg,#335f7e 0%,#24465d 42%,#102431 72%,#080d11 100%)}.world-game[data-place="beach"] .world-landmark{width:72%;height:17%;bottom:22%;clip-path:polygon(0 85%,12% 72%,24% 77%,36% 61%,48% 68%,61% 55%,74% 67%,86% 58%,100% 70%,100% 100%,0 100%)}.world-game[data-place="beach"] .world-depth{background:linear-gradient(180deg,rgba(38,95,126,.2),#0b1720 54%,#070a0d)}
.world-game[data-place="palace"] .world-scene{background:linear-gradient(180deg,#65543f,#3a3027 48%,#151311 78%,#090a0b)}.world-game[data-place="palace"] .world-orb{background:radial-gradient(circle,#ffe5a8,#b98746 64%,transparent 67%)}
.world-game[data-place="garden"] .world-scene{background:linear-gradient(180deg,#315a4d,#1d3b33 46%,#10211c 76%,#080c0a)}.world-game[data-place="garden"] .world-landmark{width:78%;height:34%;bottom:20%;border-radius:50% 50% 18% 18%;clip-path:polygon(0 100%,0 62%,8% 54%,14% 60%,21% 35%,29% 57%,36% 48%,44% 19%,52% 49%,61% 36%,68% 58%,77% 41%,84% 64%,92% 53%,100% 67%,100% 100%)}
.world-game[data-place="hospital"] .world-scene{background:linear-gradient(180deg,#587583,#314b57 48%,#172830 78%,#080b0d)}.world-game[data-place="hospital"] .world-landmark{clip-path:polygon(7% 100%,7% 20%,42% 20%,42% 6%,58% 6%,58% 20%,93% 20%,93% 100%,61% 100%,61% 56%,39% 56%,39% 100%)}
.world-game[data-place="police"] .world-scene{background:linear-gradient(180deg,#34495d,#223242 50%,#111a23 78%,#07090c)}.world-game[data-place="police"] .world-landmark{clip-path:polygon(8% 100%,8% 28%,92% 28%,92% 100%,70% 100%,70% 57%,62% 57%,62% 100%,38% 100%,38% 57%,30% 57%,30% 100%)}
.world-game[data-place="market"] .world-scene{background:linear-gradient(180deg,#775638,#4c3828 48%,#201710 78%,#0c0907)}.world-game[data-place="market"] .world-landmark{clip-path:polygon(0 100%,0 60%,10% 60%,16% 36%,26% 60%,36% 60%,43% 28%,52% 60%,62% 60%,69% 39%,79% 60%,89% 60%,95% 31%,100% 60%,100% 100%)}
.world-game[data-place="restaurant"] .world-scene{background:linear-gradient(180deg,#6f4b35,#432d23 50%,#1b1210 78%,#0a0807)}.world-game[data-place="restaurant"] .world-landmark{clip-path:polygon(9% 100%,9% 30%,91% 30%,91% 100%,68% 100%,68% 60%,32% 60%,32% 100%)}
.world-game[data-place="hotel"] .world-scene{background:linear-gradient(180deg,#635b52,#3c342f 48%,#1a1715 78%,#0a0908)}.world-game[data-place="hotel"] .world-landmark{clip-path:polygon(16% 100%,16% 16%,84% 16%,84% 100%,63% 100%,63% 54%,37% 54%,37% 100%)}
.world-game[data-place="harbor"] .world-scene{background:linear-gradient(180deg,#315b76,#1d3b50 48%,#102634 78%,#080d11)}.world-game[data-place="harbor"] .world-landmark{clip-path:polygon(0 100%,0 78%,22% 78%,30% 54%,33% 54%,33% 77%,58% 77%,67% 34%,70% 34%,70% 77%,100% 77%,100% 100%)}
.world-head{padding:calc(env(safe-area-inset-top) + 12px) clamp(12px,3vw,28px) 8px;display:grid;grid-template-columns:48px 1fr auto;gap:10px;align-items:center;text-shadow:0 1px 8px #000}.world-round{width:44px;height:44px;border-radius:50%;border:1px solid #ffffff2b;background:#090d12b8;color:#fff;font-size:29px}.world-place small{color:#d4bd91;font-size:11px}.world-place h2{margin:1px 0;font-size:clamp(22px,4.8vw,30px)}.world-places-btn{border:1px solid #ffffff30;background:#111820c9;color:#fff;border-radius:13px;padding:11px 15px}.world-presence{display:flex;align-items:center;gap:10px;padding:4px clamp(14px,3vw,28px) 12px;border-bottom:1px solid #ffffff14;min-width:0}.world-presence span{font-size:12px;color:#d5d8da}.world-avatars{display:flex;direction:ltr;flex:0 0 auto}.world-avatar{width:32px;height:32px;border-radius:50%;display:grid;place-items:center;background:linear-gradient(145deg,#303943,#1d242a);border:2px solid #0b0e11;margin-left:-7px;font-size:11px;font-weight:800}.world-avatar.nader{background:linear-gradient(145deg,#5a4528,#2c2419);color:#f2d39a;border-color:#171109}.world-nader-status{margin-inline-start:auto;color:#d7b879!important;white-space:nowrap}
.world-messages{overflow:auto;overscroll-behavior:contain;padding:18px clamp(14px,5vw,54px) 20px;display:flex;flex-direction:column;gap:10px;scroll-padding-bottom:20px}.world-msg{max-width:min(82%,650px);padding:10px 13px;border-radius:16px;background:#151b20e8;border:1px solid #ffffff12;line-height:1.55;backdrop-filter:blur(7px)}.world-msg.mine{align-self:flex-start;background:#203344}.world-msg.nader{background:#201b14;border-color:#6a543433}.world-msg b{display:block;font-size:11px;color:#cbb789;margin-bottom:3px}.world-system{align-self:center;color:#8e989f;font-size:11px;padding:4px 10px;text-align:center}.world-typing{padding:0 clamp(16px,5vw,56px) 6px;color:#b9a174;font-size:12px}.world-typing[hidden]{display:none!important}
.world-composer{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;padding:10px clamp(12px,4vw,44px) calc(env(safe-area-inset-bottom) + 10px);background:#090d11f2;border-top:1px solid #ffffff16}.world-composer input{min-width:0;border:1px solid #303940;border-radius:15px;background:#12181d;color:#fff;padding:13px 14px;font-size:16px}.world-composer button{border:0;border-radius:14px;padding:0 18px;background:#d2b276;color:#17120b;font-weight:800;min-height:46px}
.world-places{position:absolute;inset:0;z-index:8;background:#000a;display:flex;align-items:flex-end}.world-places[hidden]{display:none!important}.world-places-card{width:100%;max-height:min(82svh,760px);overflow:auto;background:#0d1216;border-radius:24px 24px 0 0;padding:18px clamp(16px,4vw,36px) calc(env(safe-area-inset-bottom) + 20px)}.world-places-card header{display:flex;justify-content:space-between;align-items:center}.world-places-card h3{margin:0}.world-places-card header button{border:0;background:#1c242a;color:#fff;width:40px;height:40px;border-radius:50%;font-size:24px}.world-places-card p{color:#8f999f;font-size:12px}.world-places-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.world-place-card{min-height:105px;border:1px solid #2d363c;border-radius:17px;background:linear-gradient(145deg,#182129,#0e1317);color:#fff;text-align:right;padding:14px;display:flex;flex-direction:column;justify-content:flex-end}.world-place-card strong{font-size:16px}.world-place-card small{color:#a8b0b5;margin-top:5px}.world-place-card.active{border-color:#c6a66e;box-shadow:inset 0 0 0 1px #c6a66e55}
body.world-preview-active>main:not(#worldGame),body.world-preview-active>.settings-sheet,body.world-preview-active>.admin-ai-panel,body.world-preview-active>#helpReportPanel{display:none!important}
@media(min-width:700px){.world-places-grid{grid-template-columns:repeat(3,1fr)}.world-head,.world-presence,.world-messages,.world-composer,.world-typing{padding-left:max(8vw,28px);padding-right:max(8vw,28px)}}
@media(orientation:landscape) and (max-height:650px){.world-scene{height:62svh}.world-place h2{font-size:21px}.world-head{padding-top:calc(env(safe-area-inset-top) + 6px)}.world-presence{padding-bottom:6px}.world-messages{padding-top:10px}.world-place-card{min-height:84px}}
'''

# Replace any older world runtime with the unified upgraded runtime.
marker=';(()=>{\nconst SOCIAL_WORLD_FIRST_BATCH=true'
pos=js.find(marker)
if pos!=-1:
    js=js[:pos].rstrip()+"\n"
marker2=';(()=>{\nconst SOCIAL_WORLD_V2=true'
pos=js.find(marker2)
if pos!=-1:
    js=js[:pos].rstrip()+"\n"

js += r'''
;(()=>{
const SOCIAL_WORLD_V2=true,$=id=>document.getElementById(id);
const places=[['beach','الشاطئ'],['palace','القصر'],['garden','الحديقة'],['hospital','المستشفى'],['police','مركز الشرطة والسجن'],['market','السوق'],['restaurant','المطعم / المقهى'],['hotel','الفندق'],['harbor','الميناء']];
let preview=false,current='beach',naderPlace='beach',naderTyping=false,returnState=[],keyboardBottom=0;
const baseCounts={beach:2,palace:1,garden:1,hospital:1,police:0,market:1,restaurant:1,hotel:0,harbor:1};
const messages={};
const nameOf=k=>(places.find(x=>x[0]===k)||[])[1]||k;
function profileName(){try{const p=JSON.parse(localStorage.getItem('profile_cache')||'{}');return p.name||p.displayName||JSON.parse(localStorage.getItem('investigator_name')||'null')||'أنت'}catch{return'أنت'}}
function ensure(k){if(!messages[k])messages[k]=[]}
function countAt(k){return (baseCounts[k]||0)+(naderPlace===k?1:0)}
function addSystem(k,text){ensure(k);const last=messages[k][messages[k].length-1];if(last?.system&&last.text===text)return;messages[k].push({system:true,text})}
function addMsg(k,name,text,mine=false,nader=false){ensure(k);messages[k].push({name,text,mine,nader})}
function render(){ensure(current);const g=$('worldGame');if(!g)return;g.dataset.place=current;$('worldPlaceName').textContent=nameOf(current);$('worldModeLabel').textContent=preview?'معاينة الإدارة · نفس العالم':'العالم';$('worldPresenceText').textContent='الموجودون الآن · '+countAt(current);const ns=$('worldNaderStatus');if(ns)ns.hidden=naderPlace!==current;const av=$('worldAvatars');av.innerHTML='';if(naderPlace===current){const n=document.createElement('span');n.className='world-avatar nader';n.textContent='ن';n.title='نادر';av.appendChild(n)}for(let i=0;i<Math.min(baseCounts[current]||0,4);i++){const x=document.createElement('span');x.className='world-avatar';x.textContent=String(i+1);av.appendChild(x)}const m=$('worldMessages');m.innerHTML='';messages[current].forEach(x=>{const d=document.createElement('div');if(x.system){d.className='world-system';d.textContent=x.text}else{d.className='world-msg'+(x.mine?' mine':'')+(x.nader?' nader':'');d.innerHTML='<b></b><span></span>';d.querySelector('b').textContent=x.name;d.querySelector('span').textContent=x.text}m.appendChild(d)});const t=$('worldTyping');if(t){t.hidden=!(naderTyping&&naderPlace===current);t.textContent='نادر يكتب…'}requestAnimationFrame(()=>{m.scrollTop=m.scrollHeight});renderPlaces()}
function renderPlaces(){const grid=$('worldPlacesGrid');if(!grid)return;grid.innerHTML='';places.forEach(([k,n])=>{const b=document.createElement('button');b.type='button';b.className='world-place-card'+(k===current?' active':'');b.innerHTML='<strong>'+n+'</strong><small>الموجودون الآن · '+countAt(k)+(naderPlace===k?' · نادر هنا':'')+'</small>';b.onclick=()=>move(k);grid.appendChild(b)})}
function move(k){if(k===current){$('worldPlaces').hidden=true;return}current=k;ensure(k);addSystem(k,'وصلت إلى '+nameOf(k));$('worldPlaces').hidden=true;render();maybeNaderGreets()}
function captureReturnState(){returnState=[];document.querySelectorAll('main').forEach(m=>{if(m.id!=='worldGame'&&!m.hidden&&getComputedStyle(m).display!=='none')returnState.push(m.id)})}
function isolate(){captureReturnState();document.body.classList.add('world-preview-active');document.querySelectorAll('main').forEach(m=>{if(m.id!=='worldGame')m.hidden=true})}
function openWorld(isPreview=false){preview=!!isPreview;current='beach';const g=$('worldGame');if(!g)return;isolate();g.hidden=false;document.body.style.overflow='hidden';ensure(current);if(!messages[current].length)addSystem(current,'وصلت إلى '+nameOf(current));render();maybeNaderGreets()}
function closeWorld(){const g=$('worldGame');if(g)g.hidden=true;document.body.classList.remove('world-preview-active');document.body.style.overflow='';returnState.forEach(id=>{const e=$(id);if(e)e.hidden=false});returnState=[]}
function naderReplyFor(text){const t=text.trim();if(/هلا|مرحبا|السلام/.test(t))return 'هلا والله 👋 موجود معكم.';if(/وين|أين/.test(t))return 'أنا هنا في '+nameOf(naderPlace)+'، وإذا نقلت مكان ببان عندكم هناك.';if(/كيف|وش/.test(t))return 'تمام 😄 أراقب سوالف العالم وأدخل إذا عندي شيء يستاهل.';return ['وصلت فكرتك 😄','ههههه تمام، كملوا وأنا معكم.','أشوفها كذا أفضل بصراحة.','موجود 👀 وش عندكم؟'][Math.floor(Math.random()*4)]}
function naderSpeak(text){if(naderPlace!==current)return;naderTyping=true;render();const delay=Math.min(1900,700+text.length*18);setTimeout(()=>{naderTyping=false;addMsg(current,'نادر',naderReplyFor(text),false,true);render()},delay)}
function maybeNaderGreets(){if(naderPlace!==current)return;ensure(current);if(messages[current].some(x=>x.nader))return;naderTyping=true;render();setTimeout(()=>{naderTyping=false;addMsg(current,'نادر','هلا والله 👋 أنا نادر. بكون موجود هنا معكم وأتنقل بين الأماكن.',false,true);render()},900)}
function moveNader(){const choices=places.map(x=>x[0]).filter(k=>k!==naderPlace);const next=choices[Math.floor(Math.random()*choices.length)];naderPlace=next;render();if(naderPlace===current)maybeNaderGreets()}
setInterval(()=>{if(!$('worldGame')?.hidden&&Math.random()<.34)moveNader()},45000);
function fixKeyboard(){const g=$('worldGame');if(!g||g.hidden)return;const vv=window.visualViewport;if(vv){keyboardBottom=Math.max(0,window.innerHeight-vv.height-vv.offsetTop);g.style.paddingBottom=keyboardBottom+'px';setTimeout(()=>{const m=$('worldMessages');if(m)m.scrollTop=m.scrollHeight},60)}}
window.visualViewport?.addEventListener('resize',fixKeyboard);window.visualViewport?.addEventListener('scroll',fixKeyboard);
document.addEventListener('click',e=>{if(e.target.closest?.('#worldBack'))closeWorld();if(e.target.closest?.('#worldPlacesOpen')){$('worldPlaces').hidden=false;renderPlaces()}if(e.target.closest?.('#worldPlacesClose'))$('worldPlaces').hidden=true;if(e.target.closest?.('#adminPreviewOpen'))setTimeout(()=>openWorld(true),0)},true);
$('worldInput')?.addEventListener('focus',()=>setTimeout(fixKeyboard,80));
$('worldComposer')?.addEventListener('submit',e=>{e.preventDefault();const i=$('worldInput'),t=i.value.trim();if(!t)return;ensure(current);addMsg(current,profileName(),t,true,false);i.value='';render();if(naderPlace===current)naderSpeak(t)});
window.HSNSNWorld={open:()=>openWorld(false),preview:()=>openWorld(true),move,close:closeWorld,moveNader};
})();
'''

idx.write_text(html,encoding='utf-8');cssf.write_text(css,encoding='utf-8');jsf.write_text(js,encoding='utf-8')
print('Applied unified responsive world v2 with Nader presence and shared admin preview')
